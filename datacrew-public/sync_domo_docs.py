#!/usr/bin/env python3
"""Sync Domo documentation from GitHub repos into the knowledge store.

Detects new commits, pulls changes, and re-ingests changed files.
Tracks sync state in the database so only deltas are processed.

Usage:
    python3 sync_domo_docs.py                    # Sync all repos
    python3 sync_domo_docs.py --repo docs-hub     # Sync specific repo
    python3 sync_domo_docs.py --force             # Force full re-ingest
    python3 sync_domo_docs.py --status            # Show sync status
"""

import argparse
import hashlib
import os
import re
import sqlite3
import subprocess
from pathlib import Path

DB_PATH = "/workspace/dc_public_memories/domo_docs.db"
REPOS = {
    "docs-hub": {
        "url": "https://github.com/DomoApps/domo-documentation-hub.git",
        "local_path": "/workspace/domo-docs-hub",
        "branch": "main",
        "doc_dir": "",  # root of repo
        "extension": ".mdx",
        "url_template": "https://domo-support.domo.com/s/article/{doc_id}?language=en_US",
        "doc_type": "support",
    },
    "developer-portal": {
        "url": "https://github.com/DomoApps/domo-developer-portal.git",
        "local_path": "/workspace/domo-developer-portal",
        "branch": "master",
        "doc_dir": "docs",
        "extension": ".md",
        "url_template": "https://developer.domo.com/docs/portal/{path}",
        "doc_type": "developer",
        "skip_dirs": ["Installation-Guides"],
    },
}


def get_category_docs_hub(filepath):
    """Map directory path to doc category for the documentation hub."""
    parts = filepath.split("/")
    if len(parts) >= 1:
        top = parts[0]
        if top == "s":
            # s/article/..., s/topic/..., s/workflow/...
            if len(parts) >= 2:
                doc_type = parts[1]
                if doc_type == "article":
                    return "article"
                elif doc_type == "topic":
                    return "topic"
                elif doc_type == "workflow":
                    return "workflow"
        # Check for category indicators in the path
        path_lower = filepath.lower()
        category_map = {
            "connector": "connector",
            "visualization": "visualization",
            "dataflow": "dataflow",
            "beast-mode": "beast-mode",
            "beastmode": "beast-mode",
            "dataset": "dataset",
            "governance": "governance",
            "admin": "governance",
            "app": "app",
            "workflow": "workflow",
            "api": "api",
        }
        for key, cat in category_map.items():
            if key in path_lower:
                return cat
    return "article"


def get_category_developer_portal(filepath):
    """Map directory path to doc category for the developer portal."""
    parts = filepath.split("/")
    if len(parts) >= 2:
        top = parts[0]
        category_map = {
            "API-Reference": {
                "Domo-App-APIs": "app-api",
                "Product-APIs": "product-api",
                "Domo-APIs": "domo-api",
                "Embed-APIs": "embed-api",
            },
            "Apps": "app-framework",
            "Embedded-Analytics": "embedded",
            "Connectors": "connector-dev",
            "Automate-Actions": "automation",
            "Data-Science": "data-science",
            "Governance": "governance",
            "Getting-Started": "getting-started",
            "Partner-Developers": "partner",
            "Forms": "forms",
            "Security": "security",
            "Misc": "misc",
            "Other-Resources": "resources",
        }
        if top in category_map:
            val = category_map[top]
            if isinstance(val, dict) and len(parts) >= 3:
                return val.get(parts[1], "api")
            elif isinstance(val, str):
                return val
    return "developer"


def clean_content(content):
    """Clean markdown content for storage."""
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)
    content = re.sub(r"!\[.*?\]\(.*?assets.*?\)", "", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def extract_title(content, filepath):
    """Extract title from content or filepath."""
    match = re.search(r"^#\s+(.+?)(?:\s*<!--.*?-->)?\s*$", content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r"!\[.*?\]\(.*?\)", "", title).strip()
        return title
    return Path(filepath).stem.replace("-", " ").title()


def get_doc_id_docs_hub(filepath, repo_root):
    """Extract doc_id from the documentation hub file path."""
    rel_path = os.path.relpath(filepath, repo_root)
    # For docs hub, the doc_id is in the path: s/article/XXXXX/filename.mdx
    match = re.search(r"s/(?:article|topic|workflow)/([^/]+)/", rel_path)
    if match:
        return match.group(1)
    # Fallback: hash the relative path
    return hashlib.md5(rel_path.encode()).hexdigest()[:12]


def get_doc_id_developer_portal(filepath, repo_root, doc_dir):
    """Generate doc_id for developer portal docs."""
    if doc_dir:
        rel_path = os.path.relpath(filepath, os.path.join(repo_root, doc_dir))
    else:
        rel_path = os.path.relpath(filepath, repo_root)
    return f"dev-{hashlib.md5(rel_path.encode()).hexdigest()[:12]}"


def get_changed_files(repo_path, branch, since_sha=None):
    """Get list of changed files since a commit SHA using git."""
    try:
        if since_sha:
            cmd = f"git -C {repo_path} diff --name-status {since_sha}..origin/{branch}"
        else:
            # No previous sync — get all files
            cmd = f"git -C {repo_path} ls-files"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"  git error: {result.stderr[:200]}")
            return []

        changes = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            if since_sha:
                parts = line.split("\t")
                if len(parts) == 2:
                    status, filepath = parts
                    changes.append({"status": status, "path": filepath})
                elif len(parts) == 3:
                    # Renamed file
                    status, old_path, new_path = parts
                    changes.append({"status": "R", "path": new_path, "old_path": old_path})
            else:
                changes.append({"status": "A", "path": line.strip()})

        return changes
    except (OSError, subprocess.SubprocessError) as e:
        print(f"  Error getting changed files: {e}")
        return []


def get_current_sha(repo_path, branch):
    """Get the current HEAD SHA for a branch."""
    result = subprocess.run(
        f"git -C {repo_path} rev-parse origin/{branch}", shell=True, capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def pull_latest(repo_path, branch):
    """Pull latest changes from remote."""
    result = subprocess.run(
        f"git -C {repo_path} fetch origin {branch} && git -C {repo_path} checkout origin/{branch}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"  git pull error: {result.stderr[:200]}")
        return False
    return True


def sync_repo(repo_name, conn, force=False):
    """Sync a single repo."""
    config = REPOS[repo_name]
    cur = conn.cursor()

    repo_path = config["local_path"]
    branch = config["branch"]
    doc_dir = config["doc_dir"]
    extension = config["extension"]

    print(f"\n=== Syncing {repo_name} ===")

    # Check if repo exists locally
    if not os.path.exists(repo_path):
        print(f"  Repo not found at {repo_path}, cloning...")
        result = subprocess.run(
            f"git clone -b {branch} {config['url']} {repo_path}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"  Clone failed: {result.stderr[:200]}")
            return {"added": 0, "updated": 0, "removed": 0}

    # Pull latest
    if not pull_latest(repo_path, branch):
        print("  Pull failed, skipping")
        return {"added": 0, "updated": 0, "removed": 0}

    # Get current SHA
    current_sha = get_current_sha(repo_path, branch)
    if not current_sha:
        print("  Could not get current SHA")
        return {"added": 0, "updated": 0, "removed": 0}

    # Get last synced SHA
    cur.execute("SELECT last_commit_sha FROM sync_state WHERE repo = ?", (repo_name,))
    row = cur.fetchone()
    last_sha = row[0] if row else None

    if force:
        last_sha = None
        print("  Force mode: full re-ingest")
    elif last_sha == current_sha:
        print(f"  Already up to date (SHA: {current_sha[:7]})")
        return {"added": 0, "updated": 0, "removed": 0}
    elif last_sha:
        print(f"  Last sync: {last_sha[:7]}, Current: {current_sha[:7]}")
    else:
        print("  First sync, ingesting all docs")

    # Get changed files
    changes = get_changed_files(repo_path, branch, last_sha)
    if not changes and not force:
        print("  No changes detected")
        return {"added": 0, "updated": 0, "removed": 0}

    print(f"  Changed files: {len(changes)}")

    # Process changes
    stats = {"added": 0, "updated": 0, "removed": 0}
    full_root = os.path.join(repo_path, doc_dir) if doc_dir else repo_path

    for change in changes:
        filepath = change["path"]
        status = change["status"]

        # Only process doc files
        if not filepath.endswith(extension):
            continue

        # Skip directories we don't want
        skip = False
        if config.get("skip_dirs"):
            for skip_dir in config["skip_dirs"]:
                if skip_dir in filepath.split("/"):
                    skip = True
                    break
        if skip:
            continue

        # Compute doc_id based on repo type
        if repo_name == "docs-hub":
            doc_id = get_doc_id_docs_hub(filepath, "")
            category = get_category_docs_hub(filepath)
            full_path = os.path.join(repo_path, filepath)
            source_url = f"https://domo-support.domo.com/s/article/{doc_id}?language=en_US"
        else:
            doc_id = get_doc_id_developer_portal(filepath, "", doc_dir)
            category = get_category_developer_portal(filepath)
            full_path = os.path.join(repo_path, filepath)
            # Remove .md extension and doc_dir prefix for URL
            url_path = filepath.replace(".md", "")
            source_url = f"https://developer.domo.com/docs/portal/{url_path}"

        if status in ("D",):
            # File deleted
            cur.execute("SELECT title FROM docs WHERE doc_id = ?", (doc_id,))
            old = cur.fetchone()
            if old:
                cur.execute("DELETE FROM docs WHERE doc_id = ?", (doc_id,))
                cur.execute(
                    "INSERT INTO doc_changes (doc_id, change_type, old_title, sync_repo) VALUES (?, 'removed', ?, ?)",
                    (doc_id, old[0], repo_name),
                )
                stats["removed"] += 1
            continue

        # File added or modified
        if not os.path.exists(full_path):
            continue

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        cleaned = clean_content(content)
        if len(cleaned) < 100:
            continue

        title = extract_title(content, filepath)
        word_count = len(cleaned.split())

        # Check if doc exists
        cur.execute("SELECT doc_id, title FROM docs WHERE doc_id = ?", (doc_id,))
        existing = cur.fetchone()

        if existing:
            # Update
            cur.execute(
                """
                UPDATE docs SET title = ?, category = ?, clean_content = ?, word_count = ?, source_url = ?
                WHERE doc_id = ?
            """,
                (title, category, cleaned, word_count, source_url, doc_id),
            )
            cur.execute(
                "INSERT INTO doc_changes (doc_id, change_type, old_title, new_title, sync_repo) VALUES (?, 'updated', ?, ?, ?)",
                (doc_id, existing[1], title, repo_name),
            )
            stats["updated"] += 1
        else:
            # Insert
            cur.execute(
                """
                INSERT INTO docs (doc_id, title, category, doc_type, file_path, clean_content, word_count, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (doc_id, title, category, config["doc_type"], filepath, cleaned, word_count, source_url),
            )
            cur.execute(
                "INSERT INTO doc_changes (doc_id, change_type, new_title, sync_repo) VALUES (?, 'added', ?, ?)",
                (doc_id, title, repo_name),
            )
            stats["added"] += 1

    # If force mode, also check for docs that no longer exist in the repo
    if force:
        # Get all doc IDs currently in DB for this repo
        cur.execute("SELECT doc_id, file_path FROM docs WHERE doc_type = ?", (config["doc_type"],))
        existing_docs = cur.fetchall()
        repo_files = set()
        for root, dirs, files in os.walk(full_root):
            for f in files:
                if f.endswith(extension):
                    repo_files.add(os.path.relpath(os.path.join(root, f), repo_path))

        for doc_id, file_path in existing_docs:
            if file_path not in repo_files:
                cur.execute("SELECT title FROM docs WHERE doc_id = ?", (doc_id,))
                old = cur.fetchone()
                if old:
                    cur.execute("DELETE FROM docs WHERE doc_id = ?", (doc_id,))
                    cur.execute(
                        "INSERT INTO doc_changes (doc_id, change_type, old_title, sync_repo) VALUES (?, 'removed', ?, ?)",
                        (doc_id, old[0], repo_name),
                    )
                    stats["removed"] += 1

    # Update sync state
    cur.execute(
        """
        INSERT OR REPLACE INTO sync_state (repo, last_commit_sha, last_sync_at, docs_added, docs_updated, docs_removed)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
    """,
        (repo_name, current_sha, stats["added"], stats["updated"], stats["removed"]),
    )

    conn.commit()

    # Rebuild FTS index if any changes
    if stats["added"] > 0 or stats["updated"] > 0 or stats["removed"] > 0:
        print("  Rebuilding FTS index...")
        cur.execute("INSERT INTO docs_fts(docs_fts) VALUES('rebuild')")
        conn.commit()

    print(f"  Results: +{stats['added']} ~{stats['updated']} -{stats['removed']}")

    return stats


def show_status(conn):
    """Show current sync status."""
    cur = conn.cursor()

    print("=== Sync Status ===\n")

    for repo_name, config in REPOS.items():
        cur.execute("SELECT * FROM sync_state WHERE repo = ?", (repo_name,))
        row = cur.fetchone()

        if row:
            print(f"{repo_name}:")
            print(f"  Last commit: {row[1][:7] if row[1] else 'never'}")
            print(f"  Last sync: {row[2]}")
            print(f"  Last stats: +{row[3]} ~{row[4]} -{row[5]}")
        else:
            print(f"{repo_name}: never synced")

        # Check current remote SHA
        current_sha = get_current_sha(config["local_path"], config["branch"])
        if current_sha:
            print(f"  Current remote SHA: {current_sha[:7]}")

        # Count docs
        cur.execute("SELECT COUNT(*) FROM docs WHERE doc_type = ?", (config["doc_type"],))
        count = cur.fetchone()[0]
        print(f"  Docs in DB: {count}")
        print()

    # Recent changes
    cur.execute(
        "SELECT doc_id, change_type, new_title, old_title, changed_at FROM doc_changes ORDER BY changed_at DESC LIMIT 10"
    )
    rows = cur.fetchall()
    if rows:
        print("Recent changes:")
        for r in rows:
            title = r[2] or r[3] or r[0]
            print(f"  [{r[1]}] {title} ({r[4]})")


def main():
    parser = argparse.ArgumentParser(description="Sync Domo docs from GitHub to knowledge store")
    parser.add_argument("--repo", choices=list(REPOS.keys()), help="Sync specific repo only")
    parser.add_argument("--force", action="store_true", help="Force full re-ingest")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)

    if args.status:
        show_status(conn)
        conn.close()
        return

    total_stats = {"added": 0, "updated": 0, "removed": 0}

    repos_to_sync = [args.repo] if args.repo else list(REPOS.keys())

    for repo_name in repos_to_sync:
        stats = sync_repo(repo_name, conn, force=args.force)
        total_stats["added"] += stats["added"]
        total_stats["updated"] += stats["updated"]
        total_stats["removed"] += stats["removed"]

    # Rebuild TF-IDF if there were significant changes
    total_changes = total_stats["added"] + total_stats["updated"] + total_stats["removed"]
    if total_changes > 5:
        print(f"\n{total_changes} changes detected — TF-IDF rebuild recommended")
        print("  Run: python3 /workspace/dc_public_memories/rebuild_tfidf.py")

    print(f"\n=== Total: +{total_stats['added']} ~{total_stats['updated']} -{total_stats['removed']} ===")

    conn.close()


if __name__ == "__main__":
    main()

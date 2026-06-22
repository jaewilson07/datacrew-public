#!/usr/bin/env python3
"""Query the Domo docs knowledge store.

Combines FTS5 full-text search, TF-IDF cosine similarity, and NER entity
lookup to find the most relevant Domo documentation for a given question.

Also logs queries and answer quality to drive wiki page generation:
- "confident" hits → raw docs were sufficient, no wiki needed
- "partial" hits → required synthesis across docs → wiki page generated
- "miss" → couldn't find good answer → flagged for external ingestion

Usage:
    python3 query_domo_docs.py "how to create a beast mode case statement"
    python3 query_domo_docs.py "snowflake connector" --top 5
    python3 query_domo_docs.py "SSO SAML" --mode entities
    python3 query_domo_docs.py "how does sharing work" --log --quality partial
    python3 query_domo_docs.py "how does sharing work" --log --quality partial --correction "need Admin role"
"""

import argparse
import json
import os
import re
import sqlite3
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domo_docs.db")

# Base URLs for Domo docs
DOMO_SUPPORT_BASE = "https://domo-support.domo.com/s/article"
DOMO_DEVELOPER_BASE = "https://developer.domo.com/docs/portal"


def doc_url(doc_id, source_url=None):
    """Generate the Domo doc URL. Uses source_url if available (developer portal docs),
    otherwise constructs from doc_id (support articles)."""
    if source_url:
        return source_url
    if doc_id.startswith("dev-"):
        # Developer portal docs don't have a simple ID-to-URL mapping
        # source_url should have been set during ingestion
        return None
    return f"{DOMO_SUPPORT_BASE}/{doc_id}?language=en_US"


# ---------------------------------------------------------------------------
# Search modes
# ---------------------------------------------------------------------------


def fts_search(cur, query, top_n=5):
    """Full-text search using SQLite FTS5."""
    cur.execute(
        "SELECT docs.doc_id, docs.title, docs.category, docs.clean_content, "
        "bm25(docs_fts) AS score "
        "FROM docs_fts JOIN docs ON docs_fts.doc_id = docs.doc_id "
        "WHERE docs_fts MATCH ? "
        "ORDER BY score ASC LIMIT ?",
        (query, top_n),
    )
    return [
        {
            "doc_id": r[0],
            "title": r[1],
            "category": r[2],
            "content": r[3],
            "score": round(float(r[4]), 4),
        }
        for r in cur.fetchall()
    ]


def tfidf_search(cur, query, top_n=5):
    """TF-IDF cosine similarity search across all docs."""
    cur.execute("SELECT doc_id, clean_content FROM docs WHERE word_count > 50")
    docs = cur.fetchall()
    if not docs:
        return []

    doc_ids = [d[0] for d in docs]
    corpus = [d[1] for d in docs]

    vectorizer = TfidfVectorizer(
        max_features=5000,
        min_df=3,
        max_df=0.7,
        ngram_range=(1, 3),
        sublinear_tf=True,
        stop_words="english",
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_\-]+\b",
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    top_indices = similarities.argsort()[-top_n:][::-1]
    results = []
    for idx in top_indices:
        if similarities[idx] > 0:
            doc_id = doc_ids[idx]
            cur.execute(
                "SELECT doc_id, title, category, clean_content FROM docs WHERE doc_id = ?",
                (doc_id,),
            )
            row = cur.fetchone()
            if row:
                results.append(
                    {
                        "doc_id": row[0],
                        "title": row[1],
                        "category": row[2],
                        "content": row[3],
                        "score": round(float(similarities[idx]), 4),
                    }
                )
    return results


def hybrid_search(cur, query, top_n=5):
    """Combine FTS + TF-IDF: merge scores, dedupe by doc_id."""
    fts_results = fts_search(cur, query, top_n=top_n * 2)
    tfidf_results = tfidf_search(cur, query, top_n=top_n * 2)

    all_results = {}

    for r in fts_results:
        all_results[r["doc_id"]] = {
            "doc_id": r["doc_id"],
            "title": r["title"],
            "category": r["category"],
            "content": r["content"],
            "fts_score": r["score"],
            "tfidf_score": 0,
        }

    for r in tfidf_results:
        if r["doc_id"] in all_results:
            all_results[r["doc_id"]]["tfidf_score"] = r["score"]
        else:
            all_results[r["doc_id"]] = {
                "doc_id": r["doc_id"],
                "title": r["title"],
                "category": r["category"],
                "content": r["content"],
                "fts_score": 0,
                "tfidf_score": r["score"],
            }

    def rank_key(item):
        has_both = 1 if item["fts_score"] != 0 and item["tfidf_score"] != 0 else 0
        return (has_both, item["tfidf_score"])

    ranked = sorted(all_results.values(), key=rank_key, reverse=True)
    return ranked[:top_n]


def entity_search(cur, query, top_n=5):
    """Find docs that mention entities related to the query."""
    cur.execute(
        "SELECT de.doc_id, de.entity_text, de.entity_label, d.title, d.category, "
        "COUNT(*) as mention_count "
        "FROM doc_entities de "
        "JOIN docs d ON de.doc_id = d.doc_id "
        "WHERE de.entity_text LIKE ? OR de.entity_text LIKE ? "
        "GROUP BY de.doc_id, de.entity_text "
        "ORDER BY mention_count DESC "
        "LIMIT ?",
        (f"%{query}%", f"{query}%", top_n * 3),
    )
    rows = cur.fetchall()
    results = []
    seen = set()
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            results.append(
                {
                    "doc_id": r[0],
                    "entity": r[1],
                    "entity_label": r[2],
                    "title": r[3],
                    "category": r[4],
                    "mentions": r[5],
                }
            )
    return results[:top_n]


def get_doc_entities(cur, doc_id, top_n=10):
    """Get NER entities for a specific doc."""
    cur.execute(
        "SELECT entity_text, entity_label FROM doc_entities " "WHERE doc_id = ? ORDER BY entity_text",
        (doc_id,),
    )
    entities = {}
    for r in cur.fetchall():
        entities.setdefault(r[1], []).append(r[0])
    return {k: v[:top_n] for k, v in entities.items()}


def get_doc_keywords(cur, doc_id, top_n=10):
    """Get TF-IDF keywords for a specific doc."""
    cur.execute(
        "SELECT term, tfidf_score FROM doc_keywords " "WHERE doc_id = ? ORDER BY tfidf_score DESC LIMIT ?",
        (doc_id, top_n),
    )
    return [(r[0], round(r[1], 4)) for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Query logging + wiki generation
# ---------------------------------------------------------------------------


def log_query(question, docs_found, doc_ids_used, answer_quality, channel=None, correction=None, wiki_page_id=None):
    """Log a query to the knowledge store for wiki prioritization.

    Args:
        question: The question asked
        docs_found: Number of docs returned by search
        doc_ids_used: List of doc_ids that were used to answer
        answer_quality: 'confident' (single doc nailed it),
                       'partial' (had to synthesize across docs),
                       'miss' (couldn't find a good answer)
        channel: DUG Slack channel where the question was asked
        correction: Community correction text (if someone pushed back)
        wiki_page_id: ID of wiki page generated (if any)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO query_log "
        "(question, docs_found, doc_ids_used, answer_quality, channel, "
        "correction, wiki_page_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            question,
            docs_found,
            json.dumps(doc_ids_used),
            answer_quality,
            channel,
            correction,
            wiki_page_id,
        ),
    )
    conn.commit()

    # If this was a partial hit or miss, check if we should generate a wiki page
    if answer_quality in ("partial", "miss"):
        wiki_id = check_and_generate_wiki(cur, question, doc_ids_used, answer_quality, correction)
        if wiki_id:
            cur.execute(
                "UPDATE query_log SET wiki_page_id = ? WHERE id = ?",
                (wiki_id, cur.lastrowid),
            )
            conn.commit()

    conn.close()


def check_and_generate_wiki(cur, question, doc_ids_used, answer_quality, correction=None):
    """Check if a wiki page should be generated for this question.

    Generates a wiki page when:
    - answer_quality is 'partial' (had to synthesize across docs)
    - answer_quality is 'miss' (no good answer found)
    - A correction was provided (community pushback)

    Returns the wiki_page_id if generated, None otherwise.
    """
    # Generate a slug from the question
    slug = question_to_slug(question)

    # Check if a wiki page already exists for this topic
    cur.execute("SELECT page_id, content, corrections FROM wiki_pages WHERE page_id = ?", (slug,))
    existing = cur.fetchone()

    if existing:
        # Update existing wiki page with new correction if provided
        if correction:
            existing_corrections = json.loads(existing[2]) if existing[2] else []
            existing_corrections.append(
                {
                    "text": correction,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            cur.execute(
                "UPDATE wiki_pages SET corrections = ?, updated_at = ? WHERE page_id = ?",
                (json.dumps(existing_corrections), datetime.utcnow().isoformat(), slug),
            )
        return slug

    # Generate wiki page stub
    # The actual content will be filled in by the agent when it reads the source docs
    # and synthesizes the answer. This just creates the entry.
    content = f"# {question}\n\n"
    content += "*This wiki page was auto-generated because the knowledge store "
    content += (
        f"{'could not find a good answer' if answer_quality == 'miss' else 'required synthesis across multiple docs'} "
    )
    content += "for this question.*\n\n"
    content += "## Source Documents\n\n"

    for doc_id in doc_ids_used:
        cur.execute("SELECT title, category FROM docs WHERE doc_id = ?", (doc_id,))
        row = cur.fetchone()
        if row:
            content += f"- [{row[1]}] {row[0]}\n"

    content += "\n## Answer\n\n"
    content += "*To be filled in from the agent's synthesized response.*\n"

    if correction:
        content += "\n## Community Corrections\n\n"
        content += f"- {correction}\n"
        corrections_json = json.dumps([{"text": correction, "timestamp": datetime.utcnow().isoformat()}])
    else:
        corrections_json = json.dumps([])

    cur.execute(
        "INSERT OR REPLACE INTO wiki_pages "
        "(page_id, title, content, source_doc_ids, source_questions, corrections, category) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            slug,
            question,
            content,
            json.dumps(doc_ids_used),
            json.dumps([question]),
            corrections_json,
            "auto-generated",
        ),
    )

    return slug


def question_to_slug(question):
    """Convert a question to a URL-friendly slug for wiki page ID."""
    slug = question.lower().strip()
    # Remove question words
    for word in ["how does", "how do", "how to", "what is", "what are", "can i", "does domo", "in domo"]:
        slug = slug.replace(word, "")
    # Keep only alphanumeric + spaces
    slug = re.sub(r"[^a-z0-9\s\-]", "", slug)
    # Collapse spaces and replace with hyphens
    slug = re.sub(r"\s+", "-", slug.strip())
    # Limit length
    slug = slug[:60].rstrip("-")
    return slug or "unnamed-topic"


def get_wiki_page(page_id):
    """Retrieve a wiki page by ID."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM wiki_pages WHERE page_id = ?", (page_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "page_id": row[0],
        "title": row[1],
        "content": row[2],
        "source_doc_ids": json.loads(row[3]) if row[3] else [],
        "source_questions": json.loads(row[4]) if row[4] else [],
        "corrections": json.loads(row[5]) if row[5] else [],
        "category": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }


def update_wiki_page(page_id, content, corrections=None):
    """Update a wiki page's content (e.g., after agent synthesizes answer)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if corrections is not None:
        cur.execute(
            "UPDATE wiki_pages SET content = ?, corrections = ?, updated_at = ? WHERE page_id = ?",
            (content, json.dumps(corrections), datetime.utcnow().isoformat(), page_id),
        )
    else:
        cur.execute(
            "UPDATE wiki_pages SET content = ?, updated_at = ? WHERE page_id = ?",
            (content, datetime.utcnow().isoformat(), page_id),
        )
    conn.commit()
    conn.close()


def get_wiki_priorities(min_questions=1):
    """Get docs/topics that need wiki pages based on query log analysis.

    Returns topics sorted by priority:
    - partial hits with corrections (highest)
    - partial hits without corrections
    - misses
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            question,
            answer_quality,
            COUNT(*) as times_asked,
            COUNT(CASE WHEN correction IS NOT NULL THEN 1 END) as corrections_count,
            GROUP_CONCAT(DISTINCT doc_ids_used) as all_doc_ids,
            GROUP_CONCAT(correction, ' | ') as all_corrections
        FROM query_log
        WHERE answer_quality IN ('partial', 'miss')
        GROUP BY question
        ORDER BY
            corrections_count DESC,
            times_asked DESC
    """)

    priorities = []
    for row in cur.fetchall():
        priorities.append(
            {
                "question": row[0],
                "quality": row[1],
                "times_asked": row[2],
                "corrections_count": row[3],
                "all_doc_ids": row[4],
                "corrections": row[5],
            }
        )

    conn.close()
    return priorities


# ---------------------------------------------------------------------------
# Main search function (used by agent)
# ---------------------------------------------------------------------------


def search(query, top_n=5, mode="hybrid", channel=None):
    """Search the Domo docs knowledge store.

    Args:
        query: Natural language question or keywords
        top_n: Number of results to return
        mode: 'fts', 'tfidf', 'hybrid', or 'entities'
        channel: DUG Slack channel (for logging)

    Returns:
        List of result dicts with doc metadata and scores
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if mode == "fts":
        results = fts_search(cur, query, top_n)
    elif mode == "tfidf":
        results = tfidf_search(cur, query, top_n)
    elif mode == "entities":
        results = entity_search(cur, query, top_n)
    else:
        results = hybrid_search(cur, query, top_n)

    # Enrich results with entities, keywords, and source URLs
    for r in results:
        if "doc_id" in r and "content" not in r:
            cur.execute("SELECT clean_content FROM docs WHERE doc_id = ?", (r["doc_id"],))
            row = cur.fetchone()
            r["content"] = row[0] if row else ""
        # Add source URL
        if "doc_id" in r and not r.get("doc_id", "").startswith("wiki:"):
            # Try to get source_url from DB first
            cur.execute("SELECT source_url FROM docs WHERE doc_id = ?", (r["doc_id"],))
            src_row = cur.fetchone()
            source_url = src_row[0] if src_row and src_row[0] else None
            r["url"] = doc_url(r["doc_id"], source_url)

    # Check if a wiki page exists for this query
    slug = question_to_slug(query)
    cur.execute("SELECT page_id, content FROM wiki_pages WHERE page_id = ?", (slug,))
    wiki = cur.fetchone()
    if wiki:
        # Prepend wiki page as first result
        results.insert(
            0,
            {
                "doc_id": f"wiki:{wiki[0]}",
                "title": f"[WIKI] {query}",
                "category": "wiki",
                "content": wiki[1],
                "score": 1.0,  # Wiki pages always rank highest
            },
        )

    conn.close()
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Query the Domo docs knowledge store")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--top", type=int, default=5, help="Number of results")
    parser.add_argument(
        "--mode",
        choices=["fts", "tfidf", "hybrid", "entities"],
        default="hybrid",
        help="Search mode",
    )
    parser.add_argument("--content", action="store_true", help="Show content preview")
    parser.add_argument("--log", action="store_true", help="Log this query")
    parser.add_argument(
        "--quality",
        choices=["confident", "partial", "miss"],
        help="Answer quality (for logging)",
    )
    parser.add_argument("--correction", type=str, help="Community correction text")
    parser.add_argument("--channel", type=str, help="DUG Slack channel")
    parser.add_argument(
        "--priorities",
        action="store_true",
        help="Show wiki generation priorities based on query log",
    )
    args = parser.parse_args()

    if args.priorities:
        priorities = get_wiki_priorities()
        if not priorities:
            print("No partial hits or misses logged yet.")
        else:
            print("=== Wiki Generation Priorities ===\n")
            for p in priorities:
                print(f"[{p['quality']}] {p['question']}")
                print(f"  Asked {p['times_asked']}x, {p['corrections_count']} corrections")
                if p["corrections"]:
                    print(f"  Corrections: {p['corrections'][:100]}")
                print()
        return

    results = search(args.query, args.top, args.mode)

    if not results:
        print("No results found.")
        return

    print(f"=== Results for '{args.query}' ({args.mode} mode) ===\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r.get('category', '?')}] {r.get('title', r.get('entity', '?'))}")
        if "url" in r:
            print(f"   URL: {r['url']}")
        if "score" in r:
            print(f"   Score: {r['score']}")
        if "fts_score" in r and r["fts_score"]:
            print(f"   FTS score: {r['fts_score']}")
        if "tfidf_score" in r and r["tfidf_score"]:
            print(f"   TF-IDF score: {r['tfidf_score']}")
        if "entity" in r:
            print(f"   Entity: [{r['entity_label']}] {r['entity']} (x{r['mentions']})")

        if args.content and "content" in r and r["content"]:
            preview = r["content"][:300].replace("\n", " ")
            print(f"   Preview: {preview}...")

        # Show entities and keywords
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        doc_id = r.get("doc_id")
        if doc_id and not doc_id.startswith("wiki:"):
            entities = get_doc_entities(cur, doc_id)
            keywords = get_doc_keywords(cur, doc_id)
            if entities:
                for label, names in entities.items():
                    print(f"   {label}: {', '.join(names[:5])}")
            if keywords:
                print(f"   Keywords: {', '.join(k[0] for k in keywords[:5])}")
        conn.close()
        print()

    # Log the query if requested
    if args.log and args.quality:
        doc_ids = [r["doc_id"] for r in results if not r.get("doc_id", "").startswith("wiki:")]
        log_query(
            question=args.query,
            docs_found=len(results),
            doc_ids_used=doc_ids,
            answer_quality=args.quality,
            channel=args.channel,
            correction=args.correction,
        )
        print(f"Query logged with quality: {args.quality}")
        if args.correction:
            print(f"Correction recorded: {args.correction}")


if __name__ == "__main__":
    main()

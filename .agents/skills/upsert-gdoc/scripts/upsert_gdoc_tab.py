"""Upsert markdown content as tabs in a Google Doc.

Usage:
    # Single tab
    python3 upsert_gdoc_tab.py --doc-id DOC_ID --title "Tab Title" --file content.md

    # Multiple tabs
    python3 upsert_gdoc_tab.py --doc-id DOC_ID \
        --title "Tab 1" --file article1.md \
        --title "Tab 2" --file article2.md
"""
import argparse
import asyncio
import os
import sys

# Add cboti to path
sys.path.insert(0, "/workspace/libraries/cboti/src")

from cboti.integrations.google.drive.google_docs import GoogleDoc
from cboti.integrations.google.auth import GoogleAuth


def load_env_var(name: str) -> str:
    """Load an env var, handling Infisical's JSON-quoting."""
    val = os.getenv(name)
    if val:
        val = val.strip().strip("'\"")
        return val
    # Try reading from .env
    try:
        with open("/workspace/.env") as f:
            for line in f:
                if line.startswith(f"{name}="):
                    val = line.split("=", 1)[1].strip().strip("'\"")
                    return val
    except FileNotFoundError:
        pass
    raise ValueError(f"Env var {name} not found in environment or .env")


async def upsert_tab(doc: GoogleDoc, document_id: str, title: str, content: str) -> None:
    """Upsert a single tab to a Google Doc."""
    print(f"  Upserting tab: '{title}'...")
    tab = await doc.Tabs.upsert(
        document_id,
        title,
        content,
        mode="replace",
    )
    print(f"  Done: tab_id={tab.tab_id}, title='{tab.title}'")


async def main():
    parser = argparse.ArgumentParser(description="Upsert markdown as Google Doc tabs")
    parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    parser.add_argument("--title", action="append", dest="titles", help="Tab title (repeat for multiple)")
    parser.add_argument("--file", action="append", dest="files", help="Markdown file path (repeat for multiple)")
    args = parser.parse_args()

    if not args.titles or not args.files:
        parser.error("At least one --title and --file pair is required")

    if len(args.titles) != len(args.files):
        parser.error("Number of --title and --file arguments must match")

    # Load credentials
    gdoc_client = load_env_var("GDOC_CLIENT")
    gdoc_token = load_env_var("GDOC_TOKEN")

    auth = GoogleAuth(
        credentials_json=gdoc_client,
        token_json=gdoc_token,
        scopes=["https://www.googleapis.com/auth/drive"],
    )

    doc = GoogleDoc(auth)

    # Read and upsert each tab
    for title, filepath in zip(args.titles, args.files):
        with open(filepath) as f:
            content = f.read()
        await upsert_tab(doc, args.doc_id, title, content)

    print(f"\nAll tabs pushed to: https://docs.google.com/document/d/{args.doc_id}/edit")


if __name__ == "__main__":
    asyncio.run(main())

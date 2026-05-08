#!/usr/bin/env python3
"""Template CLI task for runbook scripts."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Runbook task template")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    if args.dry_run:
        print("[DRY RUN] No changes applied")
    else:
        print("Executing task...")

    print("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

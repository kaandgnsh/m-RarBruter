#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bounded, local-only wordlist password recovery for RAR archives."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from collections.abc import Callable, Sequence
from typing import TextIO

DEFAULT_MAX_ATTEMPTS = 1000
MAX_ALLOWED_ATTEMPTS = 10_000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Test a bounded number of wordlist candidates against a RAR archive "
            "you own or are authorized to recover. Dry-run is the default."
        )
    )
    parser.add_argument("--archive", required=True, help="Path to the local RAR archive.")
    parser.add_argument("--wordlist", required=True, help="Path to a local UTF-8 wordlist.")
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=DEFAULT_MAX_ATTEMPTS,
        metavar="N",
        help=f"Maximum wordlist lines to inspect (1–{MAX_ALLOWED_ATTEMPTS}; default: {DEFAULT_MAX_ATTEMPTS}).",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Actually test candidates. Without this flag, the command only previews the plan.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt; requires --run.",
    )
    return parser


def validate_file(raw_path: str, label: str) -> Path:
    """Resolve a path and ensure it points to a regular file."""
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"{label} is not a regular file: {path}")
    return path


def scan_wordlist(
    wordlist_path: str | Path,
    max_attempts: int,
    verify_password: Callable[[str], bool],
    *,
    progress: Callable[[int], None] | None = None,
) -> tuple[str | None, int, int]:
    """Test up to max_attempts wordlist lines without logging candidate values.

    Returns (password_or_none, candidates_tested, lines_scanned). Blank lines are
    skipped, but still count against the line cap so a huge empty wordlist cannot
    bypass the limit.
    """
    if not 1 <= max_attempts <= MAX_ALLOWED_ATTEMPTS:
        raise ValueError(
            f"max_attempts must be between 1 and {MAX_ALLOWED_ATTEMPTS}."
        )

    tested = 0
    scanned = 0
    with Path(wordlist_path).open("r", encoding="utf-8", errors="replace") as stream:
        for raw_line in stream:
            if scanned >= max_attempts:
                break
            scanned += 1
            candidate = raw_line.rstrip("\r\n")
            if not candidate:
                continue

            tested += 1
            if verify_password(candidate):
                return candidate, tested, scanned
            if progress is not None and tested % 100 == 0:
                progress(tested)

    return None, tested, scanned


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[str], str] = input,
    output: TextIO | None = None,
    rarfile_module: object | None = None,
) -> int:
    stream = sys.stdout if output is None else output
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.yes and not args.run:
        parser.error("--yes can only be used together with --run.")
    if not 1 <= args.max_attempts <= MAX_ALLOWED_ATTEMPTS:
        parser.error(f"--max-attempts must be between 1 and {MAX_ALLOWED_ATTEMPTS}.")

    try:
        archive_path = validate_file(args.archive, "Archive")
        wordlist_path = validate_file(args.wordlist, "Wordlist")
        if archive_path.samefile(wordlist_path):
            parser.error("Archive and wordlist must be two different files.")
    except ValueError as exc:
        parser.error(str(exc))

    print(f"Archive: {archive_path}", file=stream)
    print(f"Wordlist: {wordlist_path}", file=stream)
    print(f"Maximum wordlist lines: {args.max_attempts}", file=stream)
    print("Scope: local archive and local wordlist only; no files will be extracted.", file=stream)

    if not args.run:
        print("Dry run only; no passwords were tested. Add --run to continue.", file=stream)
        return 0

    if not args.yes:
        try:
            answer = input_fn(
                "Confirm that this is your archive or you have permission to recover it. "
                "Test the displayed wordlist? [y/N] "
            )
        except EOFError:
            print("No confirmation received; recovery cancelled.", file=stream)
            return 1
        if answer.strip().lower() not in {"y", "yes"}:
            print("Recovery cancelled; no password candidates were tested.", file=stream)
            return 0

    module = rarfile_module
    if module is None:
        try:
            import rarfile as module  # type: ignore[no-redef]
        except ImportError:
            print(
                "Missing dependency. Install it with: python -m pip install -r requirements.txt",
                file=stream,
            )
            return 2

    try:
        with module.RarFile(str(archive_path)) as archive:
            if not archive.needs_password():
                print(
                    "The archive does not appear to contain password-protected entries; "
                    "no candidates were tested.",
                    file=stream,
                )
                return 2

            def verify(candidate: str) -> bool:
                try:
                    archive.testrar(pwd=candidate)
                    return True
                except module.RarWrongPassword:
                    return False

            def report_progress(tested: int) -> None:
                print(f"Candidates tested: {tested}", file=stream)

            password, tested, scanned = scan_wordlist(
                wordlist_path,
                args.max_attempts,
                verify,
                progress=report_progress,
            )
    except (OSError, module.Error) as exc:
        print(
            f"Could not test the archive: {exc}. Check the archive, rarfile setup, "
            "and compatible RAR utility available on PATH.",
            file=stream,
        )
        return 2

    print(f"Candidates tested: {tested}; wordlist lines scanned: {scanned}.", file=stream)
    if password is not None:
        print(f"Password found: {password!r}", file=stream)
        return 0

    print("No matching password was found within the selected wordlist limit.", file=stream)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

# m-RarBruter

<p align="center">
  <strong>A legacy Python prototype for offline password recovery of RAR archives.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Mode-Local%20Files-444444?style=for-the-badge" alt="Local files only">
  <img src="https://img.shields.io/badge/Status-Legacy%20%7C%20Not%20Functional-8A5A00?style=for-the-badge" alt="Legacy prototype">
</p>

---

## Overview

**m-RarBruter** is an older proof-of-concept intended to test candidate passwords from a local wordlist against a RAR archive. It was written as a small Python learning project, not as a maintained recovery application.

> [!WARNING]
> **The current script is not functional as published.** It contains multiple syntax and runtime errors, uses incorrect `rarfile` APIs, and does not configure the external RAR utility correctly. The repository has no automated tests. Do not rely on it to recover important files or run it without reviewing and repairing the source first.

This README documents the current repository honestly; it does not claim the prototype works on modern Python environments.

## Intended Workflow

The original concept was to select a RAR archive, provide a local list of candidate passwords, and test those candidates against the archive. This approach can only test passwords present in the wordlist and may take a long time for large lists.

The project is intended **only for archives you own or are explicitly authorized to recover**.

## Requirements for a Future Refactor

A working version would need:

- Python 3 and a supported version of the `rarfile` package.
- A compatible external RAR extraction utility, configured according to the library's documentation.
- Validated paths for the archive and wordlist.
- Clear handling for corrupt archives, invalid wordlists, and unsupported archive formats.
- Tests for success, failure, and malformed input.

These are requirements for a future implementation, not a claim that the current script meets them.

## Inspect the Source

Clone the repository to review the prototype:

```bash
git clone https://github.com/kaandgnsh/m-RarBruter.git
cd m-RarBruter
sed -n '1,240p' m-RarBruter/m-RarBruter.py
```

Execution is not recommended until the known issues have been fixed and tested.

## Known Limitations

- The source contains invalid assignment syntax that prevents it from running.
- Some archive operations use incorrect or undefined names.
- Dependency installation is attempted at runtime without robust error handling.
- Paths and file-opening logic are not validated.
- There is no automated test suite or verified compatibility matrix.
- The prototype has no progress controls, recovery checkpointing, or reliable error reporting.

## Roadmap

- [ ] Replace interactive prompts with validated command-line arguments.
- [ ] Correct dependency detection and archive-library integration.
- [ ] Add clear error handling and progress reporting.
- [ ] Add unit tests and a repeatable CI workflow.
- [ ] Document compatibility and performance limits before considering a usable release.

## Responsible Use

Use password-recovery tools only with files you own or have permission to access. Do not use this project to attempt access to other people's archives or data.

## Author

**Kaan DOĞAN** · [GitHub](https://github.com/kaandgnsh) · [LinkedIn](https://www.linkedin.com/in/kaan-do%C4%9Fan-911663280/) · [Instagram](https://instagram.com/kaandgn.sh)

<p align="center">
  <sub>Legacy prototype · Review and test before use</sub>
</p>

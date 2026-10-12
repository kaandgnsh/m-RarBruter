# m-RarBruter

<p align="center">
  <strong>A bounded, local-only wordlist recovery utility for RAR archives.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Scope-Local%20Files%20Only-315C45?style=for-the-badge" alt="Local files only">
  <a href="https://github.com/kaandgnsh/m-RarBruter/actions/workflows/tests.yml">
    <img src="https://github.com/kaandgnsh/m-RarBruter/actions/workflows/tests.yml/badge.svg?branch=main" alt="GitHub Actions">
  </a>
</p>

---

## Overview

**m-RarBruter** tests candidate passwords from a local wordlist against a RAR archive. This refreshed version replaces the broken legacy script with a command-line interface, explicit confirmation, and a hard limit on the number of wordlist lines inspected.

> **Authorized use only:** Use this tool only for archives you own or have explicit permission to recover. It works locally, does not contact remote services, and does not extract archive contents. The default mode is a dry run; candidates are not tested unless you pass `--run` and confirm.

## Features

- **Local files only:** requires paths to an archive and a wordlist on the current device.
- **Dry run by default:** validates paths and previews the selected operation without testing passwords.
- **Explicit confirmation:** requires `--run` and user confirmation by default.
- **Bounded operation:** default maximum is 1,000 wordlist lines; the hard limit is 10,000 lines per run.
- **No candidate logging:** tested candidate values are not printed as progress output.
- **Error reporting:** stops on invalid archives, missing backends, and unexpected archive errors.
- **Automated tests:** GitHub Actions checks the code on Python 3.10, 3.11, and 3.12.

## Requirements

- Python 3.10 or newer
- The `rarfile` Python package
- A compatible RAR utility installed and available on `PATH` (the `unrar` backend is recommended by `rarfile`)
- A local RAR archive and a UTF-8 wordlist

Install the Python dependency:

```bash
python -m pip install -r requirements.txt
```

The `rarfile` package parses archive metadata in Python but uses an external utility for compressed archive testing. Consult the [rarfile documentation](https://rarfile.readthedocs.io/) for supported backends and platform-specific setup.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/kaandgnsh/m-RarBruter.git
cd m-RarBruter
```

First preview the intended operation. This does not test passwords:

```bash
python m-RarBruter/m-RarBruter.py \
  --archive "/path/to/your-archive.rar" \
  --wordlist "/path/to/passwords.txt"
```

When the paths and attempt limit are correct, run with explicit confirmation:

```bash
python m-RarBruter/m-RarBruter.py \
  --archive "/path/to/your-archive.rar" \
  --wordlist "/path/to/passwords.txt" \
  --run
```

The command asks you to confirm authorization before testing candidates. To choose a lower limit:

```bash
python m-RarBruter/m-RarBruter.py \
  --archive "/path/to/your-archive.rar" \
  --wordlist "/path/to/passwords.txt" \
  --max-attempts 500 \
  --run
```

Only skip the prompt when you have reviewed the paths and intend to run the recovery operation:

```bash
python m-RarBruter/m-RarBruter.py \
  --archive "/path/to/your-archive.rar" \
  --wordlist "/path/to/passwords.txt" \
  --max-attempts 500 \
  --run --yes
```

## CLI Reference

| Option | Description |
|:--|:--|
| `--archive PATH` | Local RAR archive path. Required. |
| `--wordlist PATH` | Local UTF-8 wordlist path. Required. |
| `--max-attempts N` | Maximum wordlist lines inspected. Default: 1,000; allowed range: 1–10,000. |
| `--run` | Enable password testing. Without this flag, the command only previews. |
| `--yes` | Skip confirmation; valid only with `--run`. |
| `-h, --help` | Show help and exit. |

Blank lines are skipped but still count against the line limit. The tool only tests candidates present in the selected wordlist; it does not generate passwords or guarantee recovery.

## Limitations

- Password recovery succeeds only if the correct password appears in the selected wordlist and within the configured line limit.
- Performance depends on archive format, compression, backend, and device hardware.
- Incorrect passwords are identified using the backend's `RarWrongPassword` error. Other errors stop the run rather than being silently treated as incorrect candidates.
- The tool does not extract files, modify the archive, or save passwords to disk.
- A RAR utility on `PATH` is required for actual archive testing. Backend behavior can vary by platform.

## Tests

Run the test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

Tests use a fake RAR backend and temporary files; they do not perform real password cracking or require an installed RAR utility. GitHub Actions runs the tests on Python 3.10, 3.11, and 3.12.

## Project Structure

```text
m-RarBruter/
├── .github/
│   └── workflows/
│       └── tests.yml
├── m-RarBruter/
│   └── m-RarBruter.py
├── tests/
│   └── test_rarbruter.py
├── requirements.txt
└── readme.md
```

## Responsible Use

Use this tool only for authorized recovery of files you own or are allowed to access. Do not use it to attempt access to another person's archives or data.

## Author

**Kaan DOĞAN** · [GitHub](https://github.com/kaandgnsh) · [LinkedIn](https://www.linkedin.com/in/kaan-do%C4%9Fan-911663280/) · [Instagram](https://instagram.com/kaandgn.sh)

<p align="center">
  <sub>Local recovery · Bounded attempts · Explicit authorization</sub>
</p>

# pruebaCodex

Prueba de OpenAI codex from scratch

## Work hour tracker

This repository includes `tracker.py`, a small CLI tool to record
working hours and generate reports.

### Usage

Log hours in worker mode:

```bash
python tracker.py worker --worker Alice --date 2023-01-01 --hours 8
```

Generate a report in supervisor mode and send it by email:

```bash
python tracker.py supervisor --worker Alice --supervisor Bob --email alice@example.com
```

The report will also be printed to stdout.

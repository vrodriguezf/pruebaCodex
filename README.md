# pruebaCodex

Prueba de OpenAI codex from scratch

## Work hour tracker webapp

This repo now provides a simple Flask web application for tracking
working hours and generating signed reports.

### Running locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python tracker.py
   ```
3. Navigate to `http://localhost:5000` in your browser.

Workers can log hours via the **Log Hours** page. Supervisors can
use **Generate Report** to sign and optionally email a report.

The email feature relies on a local SMTP server and may fail if one is
not available.

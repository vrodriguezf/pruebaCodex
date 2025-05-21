import argparse
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

DB_NAME = 'worklog.db'


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS worklog (
                    worker TEXT,
                    date TEXT,
                    hours REAL
                )''')
    conn.commit()
    conn.close()


def log_hours(worker, date_str, hours):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO worklog (worker, date, hours) VALUES (?, ?, ?)',
              (worker, date_str, hours))
    conn.commit()
    conn.close()


def fetch_hours(worker):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT date, hours FROM worklog WHERE worker = ? ORDER BY date', (worker,))
    rows = c.fetchall()
    conn.close()
    return rows


def create_report(worker, supervisor):
    rows = fetch_hours(worker)
    total_hours = sum(r[1] for r in rows)
    lines = [f"Report for {worker}", "Date        Hours"]
    for date_str, hrs in rows:
        lines.append(f"{date_str}  {hrs}")
    lines.append(f"Total Hours: {total_hours}")
    lines.append("")
    lines.append(f"Signed by {supervisor}")
    return '\n'.join(lines)


def send_email(to_address, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'no-reply@example.com'
    msg['To'] = to_address

    try:
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


def worker_mode(args):
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        raise SystemExit('Date must be in YYYY-MM-DD format')
    log_hours(args.worker, args.date, args.hours)
    print('Hours logged successfully.')


def supervisor_mode(args):
    report = create_report(args.worker, args.supervisor)
    print(report)
    if args.email:
        send_email(args.email, f"Work report for {args.worker}", report)


def main():
    parser = argparse.ArgumentParser(description='Work hour tracker')
    subparsers = parser.add_subparsers(dest='mode', required=True)

    worker_parser = subparsers.add_parser('worker', help='Worker mode')
    worker_parser.add_argument('--worker', required=True, help='Worker name')
    worker_parser.add_argument('--date', required=True, help='Date YYYY-MM-DD')
    worker_parser.add_argument('--hours', type=float, required=True, help='Hours worked')
    worker_parser.set_defaults(func=worker_mode)

    supervisor_parser = subparsers.add_parser('supervisor', help='Supervisor mode')
    supervisor_parser.add_argument('--worker', required=True, help='Worker name')
    supervisor_parser.add_argument('--supervisor', required=True, help='Supervisor name')
    supervisor_parser.add_argument('--email', help='Worker email')
    supervisor_parser.set_defaults(func=supervisor_mode)

    args = parser.parse_args()
    init_db()
    args.func(args)


if __name__ == '__main__':
    main()

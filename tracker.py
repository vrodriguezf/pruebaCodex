from flask import Flask, request, render_template_string, redirect, url_for, flash
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

DB_NAME = 'worklog.db'

app = Flask(__name__)
app.secret_key = 'change-this-secret'


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
    c.execute('SELECT date, hours FROM worklog WHERE worker = ? ORDER BY date',
              (worker,))
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


@app.route('/')
def index():
    return render_template_string(
        """<!doctype html>
<title>Work Hour Tracker</title>
<h1>Work Hour Tracker</h1>
<ul>
  <li><a href='{{ url_for('log') }}'>Log Hours</a></li>
  <li><a href='{{ url_for('report') }}'>Generate Report</a></li>
</ul>""")


LOG_TEMPLATE = """<!doctype html>
<title>Log Hours</title>
<h1>Log Hours</h1>
<form method=post>
  Worker: <input type=text name=worker required><br>
  Date: <input type=date name=date required><br>
  Hours: <input type=number step=0.1 name=hours required><br>
  <input type=submit value=Log>
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %}
  <ul>
    {% for msg in messages %}<li>{{ msg }}</li>{% endfor %}
  </ul>
  {% endif %}
{% endwith %}
<a href='{{ url_for('index') }}'>Home</a>
"""


@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        worker = request.form['worker']
        date = request.form['date']
        hours = request.form['hours']
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash('Date must be in YYYY-MM-DD format')
            return redirect(url_for('log'))
        log_hours(worker, date, float(hours))
        flash('Hours logged successfully.')
        return redirect(url_for('log'))
    return render_template_string(LOG_TEMPLATE)


REPORT_FORM_TEMPLATE = """<!doctype html>
<title>Generate Report</title>
<h1>Generate Report</h1>
<form method=post>
  Worker: <input type=text name=worker required><br>
  Supervisor: <input type=text name=supervisor required><br>
  Worker Email: <input type=email name=email><br>
  <input type=submit value=Generate>
</form>
<a href='{{ url_for('index') }}'>Home</a>
"""

REPORT_RESULT_TEMPLATE = """<!doctype html>
<title>Report</title>
<h1>Report</h1>
<pre>{{ report }}</pre>
{% if email %}<p>Email sent to {{ email }}.</p>{% endif %}
<a href='{{ url_for('index') }}'>Home</a>
"""


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        worker = request.form['worker']
        supervisor = request.form['supervisor']
        email = request.form.get('email')
        rep = create_report(worker, supervisor)
        if email:
            send_email(email, f"Work report for {worker}", rep)
        return render_template_string(REPORT_RESULT_TEMPLATE, report=rep, email=email)
    return render_template_string(REPORT_FORM_TEMPLATE)


if __name__ == '__main__':
    init_db()
    app.run()

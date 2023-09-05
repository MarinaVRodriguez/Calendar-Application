from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db_file = 'calendar.db'

# Create the SQLite database schema
def create_database():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
create_database()

# Route for scheduling a meeting
@app.route('/', methods=['GET', 'POST'])
def schedule_meeting():
    if request.method == 'POST':
        meeting_date = request.form['meeting_date']
        meeting_time = request.form['meeting_time']
        meeting_subject = request.form['meeting_subject']
        attendees = request.form.getlist('attendees')

        # Perform data validation
        if not meeting_date or not meeting_time or not meeting_subject:
            flash('Please fill in all fields.', 'error')
        else:
            # Example meeting data
            meeting_datetime = f"{meeting_date} {meeting_time}"
            meeting = {
                'date': meeting_datetime,
                'subject': meeting_subject,
            }

            # Save the meeting details to the database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO meetings (date, subject) VALUES (?, ?)", (meeting['date'], meeting['subject']))
            meeting_id = cursor.lastrowid

            # Associate attendees with the meeting
            for attendee_id in attendees:
                cursor.execute("INSERT INTO meeting_attendees (meeting_id, user_id) VALUES (?, ?)", (meeting_id, int(attendee_id)))
            conn.commit()
            conn.close()

            flash('Meeting scheduled successfully!', 'success')

    # Load user data from the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('schedule_meeting.html', users=users)

# Route for viewing the calendar
@app.route('/calendar')
def calendar_view():
    # Retrieve scheduled meetings from the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT date, subject FROM meetings")
    meetings = [{'date': row[0], 'subject': row[1]} for row in cursor.fetchall()]
    conn.close()

    return render_template('calendar_view.html', meetings=meetings)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import schedule
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to send email notifications
def send_email(meeting, attendee):
    # Configure your email settings
    sender_email = "your_email@gmail.com"
    sender_password = "your_email_password"
    
    subject = "Meeting Reminder"
    message = f"Hi {attendee['name']},\n\nYou have a meeting on {meeting['date']} - {meeting['subject']}."

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = attendee['email']

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, attendee['email'], msg.as_string())
    except Exception as e:
        print(f"Email sending error: {str(e)}")

# Function to send text messages
def send_sms(meeting, attendee):
    # Configure your Twilio account credentials
    twilio_account_sid = "your_account_sid"
    twilio_auth_token = "your_auth_token"
    twilio_phone_number = "your_twilio_phone_number"
    
    client = Client(twilio_account_sid, twilio_auth_token)
    
    message = f"Hi {attendee['name']}, you have a meeting on {meeting['date']} - {meeting['subject']}."

    try:
        client.messages.create(
            to=attendee['phone'],
            from_=twilio_phone_number,
            body=message
        )
    except Exception as e:
        print(f"SMS sending error: {str(e)}")

# Function to load user data from a CSV file
def load_user_data(csv_file):
    user_data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_data.append(row)
    return user_data

# Main route for scheduling a meeting
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

            # Example CSV file with user data (email, name, phone)
            csv_file = 'user_data.csv'

            # Load user data from the CSV file
            users = load_user_data(csv_file)

            # Schedule reminders for each attendee
            for attendee_id in attendees:
                try:
                    attendee = users[int(attendee_id)]
                    schedule.every().day.at(meeting_datetime).do(send_email, meeting, attendee)
                    schedule.every().day.at(meeting_datetime).do(send_sms, meeting, attendee)
                except IndexError:
                    flash('Invalid attendee selected.', 'error')

            flash('Meeting scheduled successfully!', 'success')

    return render_template('schedule_meeting.html')

if __name__ == '__main__':
    app.run(debug=True)

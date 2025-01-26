import os
import smtplib
import csv
import time
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
import secrets  # for generating secret key

# Flask Configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Securely generate a secret key
app.secret_key = secrets.token_hex(16)  # Generate a 16-byte hexadecimal secret key

# Carrier SMS Gateways (Simplified list)
CARRIER_GATEWAYS = {
    'Verizon': 'vtext.com',
    'AT&T': 'txt.att.net',
    'T-Mobile': 'tmomail.net',
    'Sprint': 'messaging.sprintpcs.com'
}

# Function to get carrier's SMS gateway
def get_carrier_gateway(carrier_name):
    # Look for the carrier name in the predefined list
    carrier_name = carrier_name.strip().title()  # Normalize input
    return CARRIER_GATEWAYS.get(carrier_name)

# Function to send SMS via SMTP
def send_sms_via_smtp(phone_number, message, smtp_server, smtp_port, smtp_user, smtp_password, carrier_gateway):
    to_email = f"{phone_number}@{carrier_gateway}"
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, message)
            print(f"Message sent to {phone_number}")
    except Exception as e:
        print(f"Failed to send message to {phone_number}: {e}")

# Function to handle CSV file and send SMS with a delay of 45 seconds between each message
def process_csv_and_send_sms(file_path, smtp_server, smtp_port, smtp_user, smtp_password, subject, message, carrier_name):
    # Get the carrier's SMS gateway based on the input carrier name
    carrier_gateway = get_carrier_gateway(carrier_name)

    # Check if the carrier gateway is valid
    if not carrier_gateway:
        return f"Carrier '{carrier_name}' not found or unsupported."

    # Open and read the CSV file using the csv module
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        # Check if the CSV contains a 'phone_number' column
        if 'phone_number' not in csv_reader.fieldnames:
            return "CSV file must have a 'phone_number' column"
        
        # Iterate through the rows in the CSV
        for row in csv_reader:
            phone_number = str(row['phone_number'])
            send_sms_via_smtp(phone_number, message, smtp_server, smtp_port, smtp_user, smtp_password, carrier_gateway)
            print(f"Waiting 45 seconds before sending to the next number...")
            time.sleep(45)  # Wait for 45 seconds before sending the next SMS

# Function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to handle file upload

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Ensure the uploads folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Get SMTP details, subject, message, and carrier from the form
            smtp_server = request.form['smtp_server']
            smtp_port = int(request.form['smtp_port'])
            smtp_user = request.form['smtp_user']
            smtp_password = request.form['smtp_password']
            subject = request.form['subject']
            message = request.form['message']
            carrier_name = request.form['carrier']

            # Process the uploaded CSV file and send SMS
            result = process_csv_and_send_sms(file_path, smtp_server, smtp_port, smtp_user, smtp_password, subject, message, carrier_name)

            if result:
                flash(result)
            else:
                flash(f"Bulk SMS sent successfully!")
            return redirect(url_for('index'))

    return render_template('index.html')

    
if __name__ == '__main__':
    app.run(debug=True)

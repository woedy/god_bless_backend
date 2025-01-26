import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def send_sms_via_smtp(phone_number, carrier_gateway, message, smtp_server, smtp_port, sender_email, sender_password):
    to_email = f"{phone_number}@{carrier_gateway}"
    msg = MIMEText(message)
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "SMS"

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            return True
    except Exception as e:
        return f"Failed to send SMS: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve data from the form
        phone_number = request.form['phone_number']
        carrier_gateway = request.form['carrier_gateway']
        message = request.form['message']
        smtp_server = request.form['smtp_server']
        smtp_port = int(request.form['smtp_port'])
        sender_email = request.form['sender_email']
        sender_password = request.form['sender_password']
        
        # Call the function to send the SMS
        result = send_sms_via_smtp(phone_number, carrier_gateway, message,
                                    smtp_server, smtp_port, sender_email, sender_password)
        
        if result is True:
            return redirect(url_for('success'))
        else:
            return render_template('index.html', error=result)

    return render_template('index.html', error=None)

@app.route('/success')
def success():
    return "SMS sent successfully!"

if __name__ == '__main__':
    app.run(debug=True)

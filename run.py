import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from agent import run_agent

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("EMAIL_FROM")
SENDER_PASSWORD = os.environ.get("EMAIL_PASS")
RECEIVER_EMAIL = os.environ.get("EMAIL_TO")

def send_professional_email(subject, html_content):
    """Sends a beautifully formatted HTML email."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Error: Email credentials missing in Environment Variables.")
        return

    msg = MIMEMultipart()
    msg["From"] = f"Scholarship Bot <{SENDER_EMAIL}>"
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def create_html_body(new_items, reminders):
    """Creates a professional HTML email body."""
    
    # 1. We use a placeholder {DATE_HERE} instead of .format() 
    # This prevents Python from getting confused by the CSS curly braces
    html_template = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; color: #333; }
            .container { width: 100%; max-width: 600px; margin: 0 auto; }
            .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
            .card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; background-color: #f9f9f9; }
            .card h3 { margin-top: 0; color: #2980b9; }
            .button { display: inline-block; padding: 10px 15px; background-color: #27ae60; color: white; text-decoration: none; border-radius: 3px; font-weight: bold; }
            .footer { font-size: 12px; color: #777; text-align: center; margin-top: 30px; }
            .tag { background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
            .urgent { border-left: 5px solid #e74c3c; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Daily Scholarship Report</h2>
                <p>{DATE_HERE}</p>
            </div>
            <div style="padding: 20px;">
    """
    
    # 2. Safely inject the date
    current_date = datetime.now().strftime("%B %d, %Y")
    html = html_template.replace("{DATE_HERE}", current_date)

    if not new_items and not reminders:
        html += "<p>No new fully funded scholarships found today. The bot is still scanning!</p>"
    
    if new_items:
        html += "<h3>New Opportunities Found</h3>"
        for item in new_items:
            degree = item.get('degree', 'Degree Unspecified')
            html += f"""
            <div class="card">
                <h3>{item['name']} <span class="tag">{degree}</span></h3>
                <p>New scholarship detected. Check eligibility criteria.</p>
                <a href="{item['url']}" class="button">View Scholarship</a>
            </div>
            """

    if reminders:
        html += "<h3>Deadline Reminders</h3>"
        for item in reminders:
            html += f"""
            <div class="card urgent">
                <h3>{item['name']}</h3>
                <p><strong>Warning:</strong> Only {item['days']} days left to apply!</p>
                <a href="{item['url']}" class="button">Apply Now</a>
            </div>
            """

    html += """
            </div>
            <div class="footer">
                <p>Automated by your GitHub Actions Bot</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- MAIN LOGIC ---
if __name__ == "__main__":
    print("Starting Agent Run...")
    
    new_items, reminders = run_agent()

    print(f"Report: Found {len(new_items)} new items and {len(reminders)} reminders.")

    if new_items or reminders:
        subject = f"🎓 Update: {len(new_items)} New Scholarships Found"
        if not new_items:
             subject = f"Reminder: {len(reminders)} Deadlines Approaching"
             
        body = create_html_body(new_items, reminders)
        send_professional_email(subject, body)
    else:
        print("No new items or reminders. No email sent.")
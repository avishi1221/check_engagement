import cx_Oracle
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Oracle Database Connection
dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='XE')  # Change if needed
conn = cx_Oracle.connect(user='system', password='prisha', dsn=dsn_tns)
cursor = conn.cursor()

def calculate_interaction_score(last_visit, time_spent, pages_viewed):
    # Convert last visit to datetime object
    last_visit_date = datetime.strptime(last_visit, "%Y/%m/%d")
    days_since_last_visit = (datetime.today() - last_visit_date).days
    
    # Normalize values for interaction score (basic formula)
    score = (time_spent * 0.4) + (pages_viewed * 0.3) - (days_since_last_visit * 0.05)
    score = max(0, min(score, 1))  # Ensure score is between 0 and 1
    return score, days_since_last_visit

def send_email(to_email, subject, message):
    # Mailtrap SMTP Credentials
    SMTP_SERVER = "sandbox.smtp.mailtrap.io"  
    SMTP_PORT = 587
    SMTP_USERNAME = "14c473994bb91e"  # Replace with Mailtrap username
    SMTP_PASSWORD = "your_mailtrap_password"  # Replace with Mailtrap password

    sender_email = "test@example.com"  # Any email for Mailtrap testing

    # Create email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Connect to Mailtrap SMTP Server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# Streamlit UI
st.title("📢 Churn Risk-Based Customer Engagement System")
st.write("Enter customer details to determine engagement status and send retention notifications.")

# User inputs
user_id = st.text_input("User ID", "")
last_visit = st.text_input("Last Visit Date (YYYY/MM/DD)", "2025/04/13")
time_spent = st.number_input("Time Spent (minutes)", min_value=0.0, step=0.1)
pages_viewed = st.number_input("Pages Viewed", min_value=0, step=1)

if st.button("Check Engagement"):
    if user_id and last_visit:
        try:
            interaction_score, days_since_last_visit = calculate_interaction_score(last_visit, time_spent, pages_viewed)
            
            # Fetch the user's email from the database
            cursor.execute("SELECT email FROM Users WHERE user_id = :1", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                st.error("User not found in the database.")
            else:
                user_email = user_data[0]

                # Determine engagement status
                if interaction_score < 0.5 or days_since_last_visit > 3:
                    notification_type = "Email"
                    message = "Hey there! We noticed you haven’t visited in a while. Check out our latest offers!"
        
                    # Insert notification into Oracle
                    cursor.execute(
                        "INSERT INTO Notifications (user_id, notification_type, message) VALUES (:1, :2, :3)",
                        (user_id, notification_type, message)
                    )
                    conn.commit()

                    # Send Email Notification
                    email_sent = send_email(user_email, "We Miss You!", message)
                    
                    if email_sent:
                        st.success(f"📧 Email sent successfully to {user_email}!")
                    else:
                        st.error("❌ Failed to send email.")

                else:
                    notification_type = "None"
                    message = "User is engaged, no notification needed."
                
                # Display results
                st.subheader("📊 Engagement Status")
                st.write(f"**User ID:** {user_id}")
                st.write(f"**Interaction Score:** {interaction_score:.2f}")
                st.write(f"**Days Since Last Visit:** {days_since_last_visit}")
                st.write(f"**Notification Type:** {notification_type}")
                st.write(f"**Message:** {message}")

        except ValueError:
            st.error("Invalid date format. Please use YYYY/MM/DD.")
    else:
        st.warning("Please enter all required details!")

# Close database connection
cursor.close()
conn.close()

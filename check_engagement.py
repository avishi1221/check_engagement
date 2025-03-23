import streamlit as st
from datetime import datetime

def calculate_interaction_score(last_visit, time_spent, pages_viewed):
    # Convert last visit to datetime object
    last_visit_date = datetime.strptime(last_visit, "%Y/%m/%d")
    days_since_last_visit = (datetime.today() - last_visit_date).days
    
    # Normalize values for interaction score (basic formula)
    score = (time_spent * 0.4) + (pages_viewed * 0.3) - (days_since_last_visit * 0.05)
    score = max(0, min(score, 1))  # Ensure score is between 0 and 1
    return score, days_since_last_visit

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
            
            # Determine engagement status
            if interaction_score < 0.5 or days_since_last_visit > 3:
                notification_type = "Email"
                message = "Hey there! We noticed you haven’t visited in a while. Check out our latest offers!"
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

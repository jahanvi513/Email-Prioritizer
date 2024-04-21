import streamlit as st
import threading
import re
from datetime import datetime

class Email:
    def __init__(self, subject="", body=""):
        self.subject = subject
        self.body = body
        self.priority = 0
        self.lock = threading.Lock()

class ThreadArgs:
    def __init__(self, keyword, email):
        self.keyword = keyword
        self.email = email

def is_high_priority(subject, body, keyword):
    match = keyword.lower() in subject.lower() or keyword.lower() in body.lower()
    return match

def has_date_priority(subject, body):
    pattern = r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b'
    match = re.search(pattern, subject) or re.search(pattern, body)
    return match

def extract_emails_from_string(data):
    emails = []
    lines = data.splitlines()
    subject = ""
    body = ""
    body_started = False
    for line in lines:
        if line.startswith("Subject:"):
            if subject and body:
                emails.append(Email(subject, body))
                subject = ""
                body = ""
            subject = line[len("Subject:"):].strip()
        elif "Dear" in line and not body_started:
            body_started = True
        elif ("Thanks" in line or "Regards" in line) and body_started:
            body_started = False
        elif body_started:
            body += line.strip() + " "
    if subject and body:
        emails.append(Email(subject, body))
    return emails

def search_keyword_in_email(args):
    keyword = args.keyword.lower()
    email = args.email
    keyword_present = is_high_priority(email.subject, email.body, keyword)
    date_present = has_date_priority(email.subject, email.body)

    with email.lock:
        if keyword_present and date_present:
            email.priority = max(email.priority, 3)
        elif keyword_present:
            email.priority = max(email.priority, 2)
        elif date_present:
            email.priority = max(email.priority, 1)

def print_emails_by_priority(emails):
    emails.sort(key=lambda x: x.priority, reverse=True)
    priority_labels = {0: "Normal", 1: "Date", 2: "Keyword", 3: "Both Keyword & Date"}
    results = []
    for email in emails:
        results.append(f"Email subject: {email.subject} (Priority: {priority_labels[email.priority]})")
    return results

def main():
    st.title('Email Prioritizer')

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # Read the uploaded file into string
        string_data = uploaded_file.getvalue().decode("utf-8")
        emails = extract_emails_from_string(string_data)

        keywords_input = st.text_input("Enter keywords separated by commas")
        if st.button('Prioritize Emails'):
            if keywords_input:
                keyword_list = [keyword.strip().lower() for keyword in keywords_input.split(',')]
            
                threads = []
                for email in emails:
                    for keyword in keyword_list:
                        arg = ThreadArgs(keyword, email)
                        thread = threading.Thread(target=search_keyword_in_email, args=(arg,))
                        threads.append(thread)
                        thread.start()

                for thread in threads:
                    thread.join()

                results = print_emails_by_priority(emails)
                for result in results:
                    st.write(result)

if __name__ == "__main__":
    main()

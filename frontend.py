import streamlit as st
import threading
import re

class Email:
    def __init__(self, subject="", body=""):
        self.subject = subject
        self.body = body
        self.priority = 0
        self.lock = threading.Lock()
        self.matched_keywords = set()

class ThreadArgs:
    def __init__(self, keyword, email):
        self.keyword = keyword
        self.email = email

def is_high_priority(subject, body, keyword):
    return keyword.lower() in subject.lower() or keyword.lower() in body.lower()

def has_date_priority(subject, body):
    pattern = r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b'
    return re.search(pattern, subject) or re.search(pattern, body)

def extract_emails_from_string(data):
    emails = []
    lines = data.splitlines()
    subject, body = "", ""
    body_started = False
    for line in lines:
        if line.startswith("Subject:"):
            if subject and body:
                emails.append(Email(subject, body))
            subject, body = line[len("Subject:"):].strip(), ""
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
    keyword_present = is_high_priority(args.email.subject, args.email.body, args.keyword)
    date_present = has_date_priority(args.email.subject, args.email.body)
    with args.email.lock:
        if keyword_present:
            args.email.matched_keywords.add(args.keyword)
        if keyword_present and date_present:
            args.email.priority = max(args.email.priority, 3)
        elif keyword_present:
            args.email.priority = max(args.email.priority, 2)
        elif date_present:
            args.email.priority = max(args.email.priority, 1)

def print_emails_by_priority(emails):
    emails.sort(key=lambda x: x.priority, reverse=True)
    st.header("Prioritized Emails")
    
    high_priority_emails = [email for email in emails if len(email.matched_keywords) > 1]
    if high_priority_emails:
        st.subheader("High Priority (Multiple Keywords)")
        for email in high_priority_emails:
            st.info(f"Subject: {email.subject} - Matched Keywords: {', '.join(email.matched_keywords)}")

    for keyword in set(kw for email in emails for kw in email.matched_keywords):
        keyword_emails = [email for email in emails if keyword in email.matched_keywords and email not in high_priority_emails]
        if keyword_emails:
            st.subheader(f"Keyword: {keyword}")
            for email in keyword_emails:
                st.info(f"Subject: {email.subject}")

    normal_emails = [email for email in emails if email.priority == 0]
    if normal_emails:
        st.subheader("Normal Emails")
        for email in normal_emails:
            st.info(f"Subject: {email.subject}")

def main():
    st.title('Email Prioritizer')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        string_data = uploaded_file.getvalue().decode("utf-8")
        emails = extract_emails_from_string(string_data)
        keywords_input = st.text_input("Enter keywords separated by commas")
        if st.button('Prioritize Emails'):
            keyword_list = [keyword.strip() for keyword in keywords_input.split(',')] if keywords_input else []
            threads = []
            for email in emails:
                for keyword in keyword_list:
                    arg = ThreadArgs(keyword, email)
                    thread = threading.Thread(target=search_keyword_in_email, args=(arg,))
                    threads.append(thread)
                    thread.start()
            for thread in threads:
                thread.join()
            print_emails_by_priority(emails)

if __name__ == "__main__":
    main()

#email prioritizer
import threading
import re
from datetime import datetime

MAX_EMAILS = 100
MAX_SUBJECT_LENGTH = 100
MAX_BODY_LENGTH = 400
MAX_KEYWORDS = 10
MAX_KEYWORD_LENGTH = 50

total_threads = 0

class Email:
    def _init_(self, subject="", body=""):
        self.subject = subject
        self.body = body
        self.priority = 0

class ThreadArgs:
    def _init_(self, keyword, email):
        self.keyword = keyword
        self.email = email

def is_high_priority(subject, body, keyword):
    return keyword in subject.lower() or keyword in body.lower()

def has_date_time_priority(subject, body):
    pattern = r'\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4} \d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)\b'
    return re.search(pattern, subject) or re.search(pattern, body)

def extract_emails_from_file(file_path):
    emails = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        subject = ""
        body = ""
        body_started = False  # Initialize body_started variable
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
                body += line.strip() + " "  # Add line to body with a space separator
        if subject and body:
            emails.append(Email(subject, body))

    return emails

def search_keyword_in_email(args):
    global total_threads
    keyword = args.keyword
    email = args.email

    if is_high_priority(email.subject, email.body, keyword) and has_date_time_priority(email.subject, email.body):
        email.priority = 3  # Both keyword and date present
    elif is_high_priority(email.subject, email.body, keyword):
        email.priority = 2  # Only keyword present
    elif has_date_time_priority(email.subject, email.body):
        email.priority = 1  # Only date present
    else:
        email.priority = 0  # Neither keyword nor date present

    total_threads += 1

def print_emails_by_priority(emails):
    emails.sort(key=lambda x: x.priority, reverse=True)
    print("Emails sorted by priority:")
    for email in emails:
        if email.priority == 3:
            priority = "Both"
        elif email.priority == 2:
            priority = "Keyword"
        elif email.priority == 1:
            priority = "Date"
        else:
            priority = "Normal"
        print(f"Email subject: {email.subject} (Priority: {priority})")

def main():
    file_path = "emails.txt"  # Update this with your file path
    emails = extract_emails_from_file(file_path)

    keywords = []
    num_keywords = int(input("Enter the number of keywords: "))
    print("Enter keywords (one per line):")
    for _ in range(num_keywords):
        keyword = input().lower()  # Convert keyword to lowercase
        keywords.append(keyword)

    threads = []
    start = datetime.now()
    for email in emails:
        args = [ThreadArgs(keyword, email) for keyword in keywords]
        for arg in args:
            thread = threading.Thread(target=search_keyword_in_email, args=(arg,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    end = datetime.now()
    total_time_ms = (end - start).total_seconds() * 1000

    print_emails_by_priority(emails)

    print(f"Total number of threads made: {total_threads}")
    print(f"Total time taken: {total_time_ms:.2f} milliseconds")

if _name_ == "_main_":
    main()

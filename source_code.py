import threading
import re
from datetime import datetime

lock = threading.Lock()

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
    # if match:
    #     print(f"Keyword '{keyword}' found in '{subject[:30]}...'")
    return match

def has_date_time_priority(subject, body):
    pattern = r'\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4} \d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)\b'
    match = re.search(pattern, subject) or re.search(pattern, body)
    # if match:
    #     print(f"Date/time found in '{subject[:30]}...'")
    return match

def extract_emails_from_file(file_path):
    emails = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
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
    date_present = has_date_time_priority(email.subject, email.body)

    with email.lock:
        initial_priority = email.priority
        if keyword_present and date_present:
            email.priority = max(email.priority, 3)
        elif keyword_present:
            email.priority = max(email.priority, 2)
        elif date_present:
            email.priority = max(email.priority, 1)
        # if email.priority != initial_priority:
        #     print(f"Priority updated for '{email.subject[:30]}...' from {initial_priority} to {email.priority}")

def print_emails_by_priority(emails):
# print("Final priorities before sorting:")
# for email in emails:
#     print(f"'{email.subject[:30]}...' - Priority: {email.priority}")
    emails.sort(key=lambda x: x.priority, reverse=True)
    print("Emails sorted by priority:")
    for email in emails:
        priority_labels = {0: "Normal", 1: "Date", 2: "Keyword", 3: "Both Keyword & Date"}
        print(f"Email subject: {email.subject} (Priority: {priority_labels[email.priority]})")

def main():
    file_path = "Emails.txt"
    emails = extract_emails_from_file(file_path)

    keywords = []
    num_keywords = int(input("Enter the number of keywords: "))
    print("Enter keywords (one per line):")
    for _ in range(num_keywords):
        keyword = input().strip().lower()
        keywords.append(keyword)

    threads = []
    start = datetime.now()
    for email in emails:
        for keyword in keywords:
            arg = ThreadArgs(keyword, email)
            thread = threading.Thread(target=search_keyword_in_email, args=(arg,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    end = datetime.now()
    total_time_ms = (end - start).total_seconds() * 1000

    print_emails_by_priority(emails)
    print(f"Total number of threads made: {len(threads)}")
    print(f"Total time taken: {total_time_ms:.2f} milliseconds")

if __name__ == "__main__":
    main()

import streamlit as st
import threading
from datetime import datetime
# Import your existing functions and classes here

def main():
    st.title('Email Prioritizer')

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # Assuming the file is in plain text format and reads like your Email.txt
        file_path = uploaded_file.name
        # Instead of using a filepath, read directly into string
        string_data = uploaded_file.getvalue().decode("utf-8")

        # Assuming a function that handles string data instead of file paths
        emails = extract_emails_from_string(string_data)

        keywords = st.text_input("Enter keywords separated by commas")
        if keywords:
            keyword_list = [keyword.strip().lower() for keyword in keywords.split(',')]
        
            threads = []
            start = datetime.now()
            for email in emails:
                for keyword in keyword_list:
                    arg = ThreadArgs(keyword, email)
                    thread = threading.Thread(target=search_keyword_in_email, args=(arg,))
                    threads.append(thread)
                    thread.start()

            for thread in threads:
                thread.join()

            end = datetime.now()
            total_time_ms = (end - start).total_seconds() * 1000

            print_emails_by_priority(emails)
            st.write(f"Total number of threads made: {len(threads)}")
            st.write(f"Total time taken: {total_time_ms:.2f} milliseconds")

if __name__ == "__main__":
    main()

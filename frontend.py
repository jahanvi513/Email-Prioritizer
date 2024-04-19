'''import tkinter as tk
from tkinter import filedialog

def upload_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def create_blocks():
    keyword_list = keyword_entry.get().split(',')
    for keyword in keyword_list:
        if keyword:
            block_text = f"{keyword.upper()}\nEmail: {email_entry.get()}"
            block = tk.Text(window, width=50, height=5)
            block.insert(tk.END, block_text)
            block.pack(side=tk.LEFT, padx=10, pady=10)

# Create the main window
window = tk.Tk()
window.title("Email Prioritizer")

# Add text entry for email (larger size)
email_label = tk.Label(window, text="Enter Email:")
email_label.pack()
email_entry = tk.Entry(window, width=50)
email_entry.pack()

# Add text entry for file path
file_path_label = tk.Label(window, text="File Path:")
file_path_label.pack()
file_path_entry = tk.Entry(window, width=50)
file_path_entry.pack()
upload_button = tk.Button(window, text="Upload File", command=upload_file)
upload_button.pack()

# Add keyword entry
keyword_label = tk.Label(window, text="Enter Keywords (comma-separated):")
keyword_label.pack()
keyword_entry = tk.Entry(window, width=50)
keyword_entry.pack()

# Add button to create keyword blocks
create_button = tk.Button(window, text="Segregate Mails", command=create_blocks)
create_button.pack()

# Run the main loop
window.mainloop()
'''

import tkinter as tk
from tkinter import filedialog
import subprocess
import os

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def create_blocks():
    file_path = file_path_entry.get()
    keywords = keyword_entry.get().split(',')
    if not file_path or not keywords:
        result_text.config(text="Please upload a file and enter keywords.")
        return
    
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    email_script = os.path.join(script_dir, "email.py")

    process = subprocess.Popen(["python", email_script, file_path, ",".join(keywords)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    
    if error:
        result_text.config(text=f"Error: {error}")
        return
    
    blocks = output.split("\n\n")
    for block_text in blocks:
        block = tk.Text(window, width=50, height=5)
        block.insert(tk.END, block_text)
        block.pack(side=tk.LEFT, padx=10, pady=10)

# Create the main window
window = tk.Tk()
window.title("Email Prioritizer")

# Add text entry for file path
file_path_label = tk.Label(window, text="Upload File:")
file_path_label.pack()
file_path_entry = tk.Entry(window, width=50)
file_path_entry.pack()
upload_button = tk.Button(window, text="Upload", command=upload_file)
upload_button.pack()

# Add keyword entry
keyword_label = tk.Label(window, text="Enter Keywords (comma-separated):")
keyword_label.pack()
keyword_entry = tk.Entry(window, width=50)
keyword_entry.pack()

# Add button to create keyword blocks
create_button = tk.Button(window, text="Segregate Emails", command=create_blocks)
create_button.pack()

# Result text display
result_text = tk.Label(window, text="")
result_text.pack()

# Run the main loop
window.mainloop()


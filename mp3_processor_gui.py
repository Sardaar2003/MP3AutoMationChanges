import os
import json
import base64
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess

class SimpleMP3Processor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Batch Processor")
        self.root.geometry("500x400")
        
        # Password configuration
        self.config_file = "mp3_config.json"
        self.password = self.load_or_create_password()
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Password Frame
        self.pw_frame = tk.Frame(self.root)
        self.pw_frame.pack(pady=20)
        
        tk.Label(self.pw_frame, text="Enter Password:").pack(side=tk.LEFT)
        self.pw_entry = tk.Entry(self.pw_frame, show="*", width=30)
        self.pw_entry.pack(side=tk.LEFT, padx=5)
        self.pw_entry.bind("<Return>", self.check_password)
        
        # Main Frame (initially hidden)
        self.main_frame = tk.Frame(self.root)
        
        # Input Folder
        tk.Label(self.main_frame, text="Input Folder:").pack(pady=(20,5))
        self.input_path = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.input_path, width=50).pack()
        tk.Button(self.main_frame, text="Browse...", 
                 command=lambda: self.browse_folder(self.input_path)).pack(pady=5)
        
        # Output Folder
        tk.Label(self.main_frame, text="Output Folder:").pack(pady=(20,5))
        self.output_path = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.output_path, width=50).pack()
        tk.Button(self.main_frame, text="Browse...", 
                 command=lambda: self.browse_folder(self.output_path)).pack(pady=5)
        
        # Process Button
        tk.Button(self.main_frame, text="Process MP3 Files", 
                 command=self.process_files, bg="green", fg="white").pack(pady=20)
        
        # Status
        self.status = tk.Text(self.main_frame, height=8, width=60)
        self.status.pack(pady=10)
        
    def browse_folder(self, path_var):
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)
            
    def load_or_create_password(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('password', self.generate_password())
        else:
            new_pw = self.generate_password()
            self.save_password(new_pw)
            return new_pw
            
    def generate_password(self):
        # Simple password generation
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))
        
    def save_password(self, password):
        with open(self.config_file, 'w') as f:
            json.dump({'password': password}, f)
            
    def check_password(self, event=None):
        if self.pw_entry.get() == self.password:
            self.pw_frame.pack_forget()
            self.main_frame.pack(expand=True, fill='both')
            self.root.geometry("600x500")  # Resize for main interface
        else:
            messagebox.showerror("Error", "Incorrect password")
            
    def process_files(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()
        
        if not input_folder or not output_folder:
            messagebox.showerror("Error", "Please select both input and output folders")
            return
            
        if not os.path.exists(input_folder):
            messagebox.showerror("Error", "Input folder does not exist")
            return
            
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Process files
        processed = 0
        failed = 0
        
        for filename in os.listdir(input_folder):
            if filename.lower().endswith('.mp3'):
                input_file = os.path.join(input_folder, filename)
                output_file = os.path.join(output_folder, filename)
                
                try:
                    cmd = [
                        'ffmpeg',
                        '-i', input_file,
                        '-map_metadata', '-1',
                        '-metadata', 'encoder=',
                        '-write_id3v2', '0',
                        '-fflags', '+bitexact',
                        '-flags:a', '+bitexact',
                        '-c', 'copy',
                        output_file
                    ]
                    subprocess.run(cmd, check=True, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
                    self.status.insert(tk.END, f"Processed: {filename}\n")
                    self.status.see(tk.END)
                    self.root.update()
                    processed += 1
                except Exception as e:
                    self.status.insert(tk.END, f"Failed to process {filename}: {str(e)[:100]}...\n")
                    self.status.see(tk.END)
                    self.root.update()
                    failed += 1
                    
        messagebox.showinfo("Complete", 
                          f"Processing complete!\n"
                          f"Successfully processed: {processed} files\n"
                          f"Failed: {failed} files")
        self.status.delete(1.0, tk.END)

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == "__main__":
    if not check_ffmpeg():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error",
            "FFmpeg is not installed or not in system PATH.\n"
            "Please install FFmpeg and add it to your system PATH."
        )
    else:
        root = tk.Tk()
        app = SimpleMP3Processor(root)
        # Show password in console for first-time users
        print(f"Password: {app.password}")
        root.mainloop()
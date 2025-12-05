import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from datetime import datetime, timedelta
import sys
from pathlib import Path
import hashlib

class MP3Processor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Batch Processor")
        self.root.geometry("700x600")
        
        # Version and update settings
        self.app_version = "1.0"
        self.version_url = "https://your-website.com/version.json"  # Update this URL
        self.embedded_password = "MP3@Secure#2023!v1"  # Change this for each version
        
        # Configuration
        self.config_file = "mp3_config.json"
        self.password_info = self.initialize_password()
        
        # Check for updates
        self.check_for_updates()
        
        # Check password expiry
        if self.is_password_expired():
            messagebox.showerror(
                "Version Expired",
                "This version has expired. Please download the latest version."
            )
            self.root.after(1000, self.root.quit)
            return
            
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Password Frame
        self.pw_frame = tk.Frame(self.root)
        self.pw_frame.pack(pady=50)
        
        tk.Label(self.pw_frame, text="Enter Password:", font=('Arial', 12)).pack(pady=5)
        self.pw_entry = tk.Entry(self.pw_frame, show="*", font=('Arial', 12), width=30)
        self.pw_entry.pack(pady=5)
        self.pw_entry.bind("<Return>", self.check_password)
        tk.Button(self.pw_frame, text="Login", command=self.check_password).pack(pady=10)
        
        # Main Frame (initially hidden)
        self.main_frame = tk.Frame(self.root)
        
        # Input/Output Frames
        tk.Label(self.main_frame, text=f"MP3 Batch Processor v{self.app_version}", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Input Folder
        input_frame = tk.Frame(self.main_frame)
        input_frame.pack(pady=5, fill='x', padx=20)
        tk.Label(input_frame, text="Input Folder:").pack(side='left')
        self.input_path = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.input_path, width=50).pack(side='left', padx=5)
        tk.Button(input_frame, text="Browse...", 
                 command=lambda: self.browse_folder(self.input_path)).pack(side='left')
        
        # Output Folder
        output_frame = tk.Frame(self.main_frame)
        output_frame.pack(pady=5, fill='x', padx=20)
        tk.Label(output_frame, text="Output Folder:").pack(side='left')
        self.output_path = tk.StringVar()
        tk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side='left', padx=5)
        tk.Button(output_frame, text="Browse...", 
                 command=lambda: self.browse_folder(self.output_path)).pack(side='left')
        
        # Process Button
        tk.Button(self.main_frame, text="Process MP3 Files", 
                 command=self.process_files, 
                 bg="#4CAF50", fg="white", 
                 font=('Arial', 12, 'bold'),
                 padx=20, pady=10).pack(pady=20)
        
        # Status
        self.status = tk.Text(self.main_frame, height=10, width=70, wrap=tk.WORD)
        self.status.pack(pady=10, padx=20)
        
        # Scrollbar for status
        scrollbar = tk.Scrollbar(self.status)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status.yview)
        
        # Show password expiry info
        expiry_date = datetime.strptime(self.password_info['expiry_date'], '%Y-%m-%d').date()
        days_left = (expiry_date - datetime.now().date()).days
        self.status.insert(tk.END, f"Password expires in: {days_left} days\n")
        self.status.see(tk.END)

    def check_for_updates(self):
        try:
            import requests
            from packaging import version
            
            response = requests.get(self.version_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('latest_version', self.app_version)
                
                if version.parse(self.app_version) < version.parse(latest_version):
                    download_url = data.get('download_url', '')
                    messagebox.showinfo(
                        "Update Available",
                        f"Version {latest_version} is available.\n\n"
                        f"Please download the latest version to continue."
                    )
                    self.root.after(1000, self.root.quit)
        except Exception as e:
            print(f"Version check failed: {e}")  # Silently fail if can't check

    def browse_folder(self, path_var):
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)
    
    def initialize_password(self):
        # Default config
        expiry_date = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        default_config = {
            'password': self.embedded_password,
            'expiry_date': expiry_date,
            'version': self.app_version
        }
        
        # Load existing config or create new
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Only use existing config if it's for this version
                    if config.get('version') == self.app_version:
                        return config
            except:
                pass
                
        # Save new config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
            
        return default_config
    
    def is_password_expired(self):
        return datetime.now().date() > datetime.strptime(self.password_info['expiry_date'], '%Y-%m-%d').date()
    
    def check_password(self, event=None):
        if self.pw_entry.get() == self.password_info['password']:
            self.pw_frame.pack_forget()
            self.main_frame.pack(expand=True, fill='both')
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
        mp3_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.mp3')]
        
        if not mp3_files:
            messagebox.showwarning("Warning", "No MP3 files found in the input folder")
            return
        
        self.status.delete(1.0, tk.END)
        self.status.insert(tk.END, "Starting MP3 processing...\n")
        self.root.update()
        
        for filename in mp3_files:
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
                self.status.insert(tk.END, f"✅ Processed: {filename}\n")
                processed += 1
            except Exception as e:
                self.status.insert(tk.END, f"❌ Failed {filename}: {str(e)[:100]}...\n")
                failed += 1
            
            self.status.see(tk.END)
            self.root.update()
        
        # Show completion message
        self.status.insert(tk.END, "\n" + "="*50 + "\n")
        self.status.insert(tk.END, f"Processing Complete!\n")
        self.status.insert(tk.END, f"Successfully processed: {processed} files\n")
        self.status.insert(tk.END, f"Failed: {failed} files\n")
        self.status.see(tk.END)

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == "__main__":
    # Set working directory to the directory containing the executable
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    
    if not check_ffmpeg():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error - FFmpeg Not Found",
            "FFmpeg is required but not found in your system PATH.\n\n"
            "Please install FFmpeg and add it to your system PATH.\n"
            "Download from: https://ffmpeg.org/download.html"
        )
    else:
        root = tk.Tk()
        app = MP3Processor(root)
        root.mainloop()
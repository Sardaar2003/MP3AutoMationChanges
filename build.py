import os
from PyInstaller import __main__ as pyi

# Read password from environment variable
password = os.getenv("MP3_PROCESSOR_PASSWORD", "DEFAULT_PASSWORD")

# Create a modified version of the script with UTF-8 encoding
with open("mp3_processor.py", "r", encoding='utf-8') as f:
    content = f.read()

# Replace the password
content = content.replace(
    'self.embedded_password = "MP3@Secure#2023!v1"',  # Must match exactly
    f'self.embedded_password = "{password}"'
)

with open("mp3_processor_temp.py", "w", encoding='utf-8') as f:
    f.write(content)

# Build with PyInstaller (FIX: Added hidden imports)
pyi.run([
    "mp3_processor_temp.py",
    "--onefile",
    "--windowed",
    "--name=MP3_Processor_v1.0",
    "--hidden-import=encodings",
    "--hidden-import=encodings.aliases"
])

# Clean up
os.remove("mp3_processor_temp.py")

import os
import subprocess
import datetime

# Directory where ffmpeg.exe is located
FFMPEG_PATH = r"ffmpeg.exe"

# Function to convert AVI to MP4
def convert_avi_to_mp4(avi_file):
    base_name = os.path.splitext(avi_file)[0]
    mp4_file = f"{base_name}.mp4"

    # Get the last modified time of the original file
    last_modified_time = os.path.getmtime(avi_file)
    last_modified_datetime = datetime.datetime.fromtimestamp(last_modified_time)

    # Run the ffmpeg command
    ffmpeg_command = [
        FFMPEG_PATH,
        "-hwaccel", "cuda",
        "-i", avi_file,
        "-c:v", "hevc_nvenc",
        "-b:v", "6M",
        "-maxrate", "6M",
        "-bufsize", "12M",
        "-c:a", "aac",
        "-map_metadata", "0",
        mp4_file
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Set the last modified time of the new file to match the original file
    os.utime(mp4_file, (last_modified_time, last_modified_time))

# Loop through all .avi files in the current directory
for file in os.listdir("."):
    if file.lower().endswith(".avi"):
        convert_avi_to_mp4(file)

print("Conversion complete!")
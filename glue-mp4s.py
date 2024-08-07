import os
import subprocess

# Directory where ffmpeg.exe is located
FFMPEG_PATH = r"ffmpeg.exe"

# Function to glue MP4 files
def glue_mp4_files():
    # Get all MP4 files in the current directory
    mp4_files = [file for file in os.listdir(".") if file.lower().endswith(".mp4")]

    # Sort the MP4 files by their creation datetime
    mp4_files.sort(key=lambda x: os.path.getctime(x))
    last_modified_time = os.path.getmtime(mp4_files[0])

    # Create a temporary text file to store the list of MP4 files
    file_list = "file_list.txt"
    with open(file_list, "w") as f:
        for file in mp4_files:
            f.write(f"file '{file}'\n")

    # Get the metadata of the first MP4 file
    first_file = mp4_files[0]

    # Run the ffmpeg command to concatenate the MP4 files
    ffmpeg_command = [
        FFMPEG_PATH,
        "-f", "concat",
        "-safe", "0",
        "-i", file_list,
        "-c", "copy",
        "-map_metadata", "0",
        "output.mp4"
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Remove the temporary file list
    os.remove(file_list)
    os.utime("output.mp4", (last_modified_time, last_modified_time))

# Call the function to glue MP4 files
glue_mp4_files()
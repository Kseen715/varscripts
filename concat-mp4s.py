import os
import subprocess
from datetime import datetime
import argparse

def get_sorted_videos(directory):
    # Get all mp4 files in the directory
    video_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]
    
    # Get file paths and their modification times
    video_files_with_time = [(os.path.join(directory, f), os.path.getmtime(os.path.join(directory, f))) for f in video_files]
    
    # Sort files by modification time
    sorted_videos = sorted(video_files_with_time, key=lambda x: x[1])
    
    return [video[0] for video in sorted_videos]

def concatenate_videos(video_list, output_file):
    # Create a temporary text file to list the videos in order
    with open('video_list.txt', 'w') as f:
        for video in video_list:
            f.write(f"file '{video}'\n")
    
    # Use ffmpeg to concatenate the videos
    ffmpeg_command = [
        'ffmpeg', 
        '-f', 'concat', 
        '-safe', '0', 
        '-i', 'video_list.txt', 
        '-c', 'copy', 
        output_file
    ]
    
    # Execute the ffmpeg command
    subprocess.run(ffmpeg_command)
    
    # Clean up the temporary file
    os.remove('video_list.txt')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate multiple mp4 files into a single video.")
    parser.add_argument("directory", type=str, help="Directory containing the mp4 files.")
    parser.add_argument("output_file", type=str, help="Output file name.")
    
    args = parser.parse_args()

    directory = args.directory
    output_file = args.output_file

    # Get sorted video files by modification datetime
    sorted_videos = get_sorted_videos(directory)
    
    # Concatenate the videos
    concatenate_videos(sorted_videos, output_file)
    
    print(f"Videos concatenated into {output_file}")

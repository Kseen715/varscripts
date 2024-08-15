import os
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def encode_audio(input_path, output_folder, input_format, output_format, bitrate, max_workers=4):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    files_to_process = []

    # Check if the input path is a single file or a directory
    if os.path.isfile(input_path):
        # Process single file
        files_to_process.append(input_path)
    else:
        # Process all files in the directory with the specified input format
        for filename in os.listdir(input_path):
            if filename.endswith(f".{input_format}"):
                input_file = os.path.join(input_path, filename)
                files_to_process.append(input_file)

    # Use ThreadPoolExecutor to process files concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_file, file, output_folder, output_format, bitrate): file 
            for file in files_to_process
        }

        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                future.result()
                print(f"Successfully encoded {file}")
            except Exception as exc:
                print(f"Error encoding {file}: {exc}")

def process_file(input_file, output_folder, output_format, bitrate):
    # Generate the output filename and path
    output_filename = os.path.splitext(os.path.basename(input_file))[0] + f".{output_format}"
    output_file = os.path.join(output_folder, output_filename)

    # Use ffmpeg to encode the file
    command = [
        "ffmpeg", 
        "-i", input_file,  # Input file
        "-b:a", bitrate,   # Bitrate
        output_file        # Output file
    ]
    subprocess.run(command, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode audio files using FFmpeg asynchronously. You can specify a single file or a folder.")
    parser.add_argument("input_path", type=str, help="Path to the input file or folder containing audio files.")
    parser.add_argument("output_folder", type=str, help="Path to the output folder where encoded files will be saved.")
    parser.add_argument("input_format", type=str, choices=["mp3", "wav", "aac", "flac", "ogg"], help="Input format (e.g., 'mp3', 'wav').")
    parser.add_argument("output_format", type=str, choices=["mp3", "wav", "aac", "flac", "ogg"], help="Output format (e.g., 'mp3', 'wav').")
    parser.add_argument("bitrate", type=str, help="Bitrate for the output files (e.g., '192k').")
    parser.add_argument("--max-workers", type=int, default=os.cpu_count(), help="Maximum number of threads to use (default: os.cpu_count()).")

    args = parser.parse_args()

    encode_audio(args.input_path, args.output_folder, args.input_format, args.output_format, args.bitrate, args.max_workers)

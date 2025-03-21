import argparse
import os
import subprocess
import json
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Cut videos into chunks of up to 2GB using ffmpeg')
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--input', help='Input video file')
    input_group.add_argument('-d', '--directory', help='Input directory with video files')
    
    parser.add_argument('-o', '--output', required=True, help='Output directory for cut videos')
    parser.add_argument('-s', '--size', type=float, default=2, help='Maximum size of each chunk in GB (default: 2)')
    
    return parser.parse_args()

def check_ffmpeg_installed():
    """Check if ffmpeg and ffprobe are installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_video_info(video_path):
    """Get video information using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        # Extract relevant information
        format_info = info.get('format', {})
        duration = float(format_info.get('duration', 0))
        bit_rate = format_info.get('bit_rate')
        
        # If bit_rate is not available in format, calculate from size and duration
        if not bit_rate:
            size = int(format_info.get('size', 0))
            if duration > 0 and size > 0:
                bit_rate = str(int(size * 8 / duration))
            else:
                bit_rate = '0'
        
        return {
            'duration': duration,
            'bit_rate': int(bit_rate),
            'size': int(format_info.get('size', 0))
        }
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"Error getting video info for {video_path}: {e}")
        return None

def calculate_cut_points(video_info, max_size_gb=2):
    """Calculate cut points based on video bitrate and maximum size"""
    duration = video_info['duration']
    bit_rate = video_info['bit_rate']
    
    # Calculate how many seconds of video fit into max_size_bytes
    # bit_rate is in bits per second, so we divide by 8 to get bytes per second
    max_size_bytes = max_size_gb * 1024 * 1024 * 1024
    seconds_per_chunk = max_size_bytes / (bit_rate / 8)
    
    # Create cut points
    cut_points = []
    current_time = 0
    
    while current_time < duration:
        start_time = current_time
        end_time = min(current_time + seconds_per_chunk, duration)
        
        cut_points.append((start_time, end_time))
        current_time = end_time
    
    return cut_points

def format_time(seconds):
    """Convert seconds to HH:MM:SS.mmm format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds_remainder:06.3f}"

def cut_video(input_path, output_dir, cut_points, base_name=None):
    """Cut video at specified cut points using ffmpeg"""
    if base_name is None:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    total_parts = len(cut_points)
    
    for i, (start_time, end_time) in enumerate(cut_points):
        output_filename = f"{base_name}_p{i+1:03d}of{total_parts:03d}{os.path.splitext(input_path)[1]}"
        output_path = os.path.join(output_dir, output_filename)
        
        start_time_fmt = format_time(start_time)
        end_time_fmt = format_time(end_time)
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-ss', start_time_fmt,
            '-to', end_time_fmt,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-avoid_negative_ts', '1',
            '-y',  # Overwrite output files without asking
            output_path
        ]
        
        print(f"Cutting part {i+1}/{total_parts}: {start_time_fmt} to {end_time_fmt}")
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                results.append(output_path)
                print(f"Created: {output_path}")
            else:
                print(f"Error cutting part {i+1}:")
                print(process.stderr)
        except subprocess.SubprocessError as e:
            print(f"Error running ffmpeg: {e}")
    
    return results

def process_video_file(input_path, output_dir, max_size_gb):
    """Process a single video file"""
    print(f"Processing file: {input_path}")
    
    # Get video information
    video_info = get_video_info(input_path)
    if not video_info:
        print(f"Skipping {input_path} due to error getting video info")
        return []
    
    print(f"Duration: {video_info['duration']:.2f}s, Bitrate: {video_info['bit_rate']/1024/1024:.2f} Mbps")
    
    # If file is already under the maximum size, just copy it
    max_size_bytes = max_size_gb * 1024 * 1024 * 1024
    if video_info['size'] < max_size_bytes:
        output_filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, output_filename)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"File is already under {max_size_gb}GB, copying to output directory")
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c', 'copy',
            '-y',
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Copied: {output_path}")
            return [output_path]
        except subprocess.SubprocessError as e:
            print(f"Error copying file: {e}")
            return []
    
    # Calculate cut points
    cut_points = calculate_cut_points(video_info, max_size_gb)
    print(f"Video will be split into {len(cut_points)} parts")
    
    # Cut video
    return cut_video(input_path, output_dir, cut_points)

def find_video_files(directory):
    """Find all video files in a directory"""
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.ts', '.webm')
    video_files = []
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(video_extensions):
            video_files.append(os.path.join(directory, filename))
    
    return video_files

def main():
    args = parse_arguments()
    
    # Check if ffmpeg and ffprobe are installed
    if not check_ffmpeg_installed():
        print("Error: ffmpeg or ffprobe is not installed or not in PATH. Please install them and try again.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    if args.input:
        # Process single file
        if not os.path.isfile(args.input):
            print(f"Error: Input file '{args.input}' does not exist")
            sys.exit(1)
        process_video_file(args.input, args.output, args.size)
    else:
        # Process all video files in directory
        if not os.path.isdir(args.directory):
            print(f"Error: Input directory '{args.directory}' does not exist")
            sys.exit(1)
            
        video_files = find_video_files(args.directory)
        if not video_files:
            print(f"No video files found in {args.directory}")
            sys.exit(0)
            
        print(f"Found {len(video_files)} video files")
        for file_path in video_files:
            process_video_file(file_path, args.output, args.size)

if __name__ == "__main__":
    main()
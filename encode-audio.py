import os
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# To drop the following imports and whole requirements.txt file:
# ==============================================================================
# Part of colorama.py module
# ==============================================================================
# colorama's LICENSE:
"""
Copyright (c) 2010 Jonathan Hartley
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holders, nor those of its contributors
  may be used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
# 
# 
CSI = '\033['
# 
# 
def code_to_chars(code):
    return CSI + str(code) + 'm'
# 
# 
class colorama:
    class AnsiCodes(object):
        def __init__(self):
            # the subclasses declare class attributes which are numbers.
            # Upon instantiation we define instance attributes, which are the 
            # same as the class attributes but wrapped with the ANSI escape 
            # sequence
            for name in dir(self):
                if not name.startswith('_'):
                    value = getattr(self, name)
                    setattr(self, name, code_to_chars(value))
    # 
    # 
    class AnsiFore(AnsiCodes):
        BLACK           = 30
        RED             = 31
        GREEN           = 32
        YELLOW          = 33
        BLUE            = 34
        MAGENTA         = 35
        CYAN            = 36
        WHITE           = 37
        RESET           = 39
    # 
        # These are fairly well supported, but not part of the standard.
        LIGHTBLACK_EX   = 90
        LIGHTRED_EX     = 91
        LIGHTGREEN_EX   = 92
        LIGHTYELLOW_EX  = 93
        LIGHTBLUE_EX    = 94
        LIGHTMAGENTA_EX = 95
        LIGHTCYAN_EX    = 96
        LIGHTWHITE_EX   = 97
    # 
    # 
    class AnsiStyle(AnsiCodes):
        BRIGHT    = 1
        DIM       = 2
        NORMAL    = 22
        RESET_ALL = 0
    # 
    # 
    Fore   = AnsiFore()
    Style  = AnsiStyle()
# ==============================================================================
# End of colorama.py module
# ==============================================================================


class Logger:
    LOG_LEVELS = {
        'NONE': 0,
        'ERROR': 1,
        'WARNING': 2,
        'SUCCESS': 3,
        'INFO': 4,
        'DEBUG': 5,
    }

    LOG_LEVEL = LOG_LEVELS['DEBUG']

    @staticmethod
    def debug(msg):
        """Log debug message

        Args:
            msg (str): Debug message
        """
        if Logger.LOG_LEVEL >= Logger.LOG_LEVELS['DEBUG']:
            print(f'{colorama.Fore.CYAN}{datetime.datetime.now()} ' \
                  + f'[DEBUG] {msg}{colorama.Style.RESET_ALL}')

    @staticmethod
    def info(msg):
        """Log info message

        Args:
            msg (str): Info message
        """
        if Logger.LOG_LEVEL >= Logger.LOG_LEVELS['INFO']:
            print(f'{colorama.Style.RESET_ALL}{datetime.datetime.now()} ' \
                  + f'[INFO] {msg}{colorama.Style.RESET_ALL}')

    @staticmethod
    def happy(msg):
        """Log happy message

        Args:
            msg (str): Happy message
        """
        if Logger.LOG_LEVEL >= Logger.LOG_LEVELS['SUCCESS']:
            print(f'{colorama.Fore.GREEN}{datetime.datetime.now()} ' \
                  + f'[SUCCESS] {msg}{colorama.Style.RESET_ALL}')

    @staticmethod
    def warning(msg):
        """Log warning message

        Args:
            msg (str): Warning message
        """
        if Logger.LOG_LEVEL >= Logger.LOG_LEVELS['WARNING']:
            print(f'{colorama.Fore.YELLOW}{datetime.datetime.now()} ' \
                  + f'[WARNING] {msg}{colorama.Style.RESET_ALL}')

    @staticmethod
    def error(msg):
        """Log error message

        Args:
            msg (str): Error message
        """
        if Logger.LOG_LEVEL >= Logger.LOG_LEVELS['ERROR']:
            print(f'{colorama.Fore.RED}{datetime.datetime.now()} ' \
                  + f'[ERROR] {msg}{colorama.Style.RESET_ALL}')

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

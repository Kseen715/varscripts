#!/usr/bin/env python3

import os, argparse, subprocess
import datetime

# Directory where ffmpeg.exe is located
FFMPEG_PATH = r"ffmpeg"

# ==============================================================================
# Logger class
# by Kseen715
# v1.5.2
# ==============================================================================
import datetime, inspect

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

LOG_LEVELS = {
        'NONE': 0,
        'ERROR': 1,
        'WARNING': 2,
        'SUCCESS': 3,
        'INFO': 4,
        'DEBUG': 5,
    }

# Log level for stdout/stderr. 
# Will be saved to the log file regardless of this setting.
LOG_LEVEL = 5

# Log file, stdout only if empty
LOG_FILE = './.logs/log.log'
LOG_FILE_MAX_SIZE = 1024 * 1024  # 1 MB


class Logger:
    @staticmethod
    def __custom_print__(msg: str, level: str, style: str = None, 
                         do_inspect: bool = False, 
                         inspect_stack_offset: int = 1, 
                         do_write_file: bool = True,
                         do_write_stdout: bool = True):
        """Log custom message

        Args:
            msg (str): Custom message
            level (int): Log level
            color (str): Color
        """
        while msg.endswith('\n'):
            msg = msg[:-1]
        if do_inspect:
            frame = inspect.stack()[inspect_stack_offset]
            file_name = frame.filename
            line_number = frame.lineno
            msg = f"{msg} ({file_name}:{line_number})"
        if LOG_FILE and do_write_file:
            if not os.path.exists(os.path.dirname(LOG_FILE)):
                os.makedirs(os.path.dirname(LOG_FILE))
            with open(LOG_FILE, 'a') as f:
                f.write(f'{datetime.datetime.now()} ' \
                        + f'[{level}] {msg}\n')
            if os.path.getsize(LOG_FILE) > LOG_FILE_MAX_SIZE * 0.9:
                with open(LOG_FILE, 'rb') as f:
                    f.seek(-int(LOG_FILE_MAX_SIZE * 0.9), os.SEEK_END)
                    data = f.read()
                with open(LOG_FILE, 'wb') as f:
                    f.write(data)
        if do_write_stdout:
            print(f'{style}{datetime.datetime.now()} ' \
                + f'[{level}] {msg}{colorama.Style.RESET_ALL}')
        

    @staticmethod
    def __custom_input__(msg: str, level: str, style: str,
                         do_write_file: bool = True):
        """Log custom message

        Args:
            msg (str): Custom message
            color (str): Color
        """
        inpt = input(f'{style}{datetime.datetime.now()} ' \
                  + f'[{level}] {msg}{colorama.Style.RESET_ALL}')
        if LOG_FILE and do_write_file:
            if not os.path.exists(os.path.dirname(LOG_FILE)):
                os.makedirs(os.path.dirname(LOG_FILE))
            with open(LOG_FILE, 'a') as f:
                f.write(f'{style}{datetime.datetime.now()} ' \
                        + f'[{level}] {msg}{colorama.Style.RESET_ALL}' \
                        + inpt + '\n')
            if os.path.getsize(LOG_FILE) > LOG_FILE_MAX_SIZE * 0.9:
                with open(LOG_FILE, 'rb') as f:
                    f.seek(-int(LOG_FILE_MAX_SIZE * 0.9), os.SEEK_END)
                    data = f.read()
                with open(LOG_FILE, 'wb') as f:
                    f.write(data)
        return inpt


    @staticmethod
    def debug(msg, do_inspect=True):
        """Log debug message

        Args:
            msg (str): Debug message
        """
        Logger.__custom_print__(msg, 'DEBUG', \
                                colorama.Fore.LIGHTMAGENTA_EX, \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['DEBUG'])
            


    @staticmethod
    def info(msg, do_inspect=False):
        """Log info message

        Args:
            msg (str): Info message
        """
        Logger.__custom_print__(msg, 'INFO', \
                                colorama.Style.RESET_ALL, \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['INFO'])


    @staticmethod
    def happy(msg, do_inspect=False):
        """Log happy message

        Args:
            msg (str): Happy message
        """
        Logger.__custom_print__(msg, 'SUCCESS', \
                                colorama.Fore.GREEN, \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['SUCCESS'])


    @staticmethod
    def warning(msg, do_inspect=False):
        """Log warning message

        Args:
            msg (str): Warning message
        """
        Logger.__custom_print__(msg, 'WARNING', \
                                colorama.Fore.YELLOW, \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['WARNING'])


    @staticmethod
    def error(msg, do_inspect=True):
        """Log error message

        Args:
            msg (str): Error message
        """
        Logger.__custom_print__(msg, 'ERROR', \
                                colorama.Fore.RED, \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['ERROR'])


    @staticmethod
    def input(msg, do_inspect=False):
        """Log input message

        Args:
            msg (str): Input message
        """
        return Logger.__custom_input__(msg, 'INPUT', \
                                        colorama.Fore.CYAN, \
                                        do_inspect, 2)

# ==============================================================================
# End of Logger class
# ==============================================================================

def get_video_bitrate(video_file):
    Logger.debug(f"Getting bitrate of {video_file}...")
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', \
        'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', \
        video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return int(result.stdout.decode().strip())


def get_video_audio_codec(video_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', \
        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', \
        video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode().strip()

# Function to convert AVI to MP4
def convert(filename, output_folder, output_format, codec, bitrate, 
            audio_codec, scale=None, fps=None, rewrite=False):
    base_name = os.path.splitext(os.path.basename(filename))[0]
    # if output_folder is folder 

    if '.' in output_format:
        output_format = output_format.split('.')[-1]

    if os.path.isdir(output_folder):
        output_file = f"{os.path.join(output_folder, base_name)}.{output_format}"
    else:
        output_file = output_folder
    Logger.debug(f"Filename: {filename}")
    Logger.debug(f"Base name: {base_name}")
    Logger.debug(f"Output folder: {output_folder}")
    Logger.debug(f"Output file: {output_file}")

    # Get the last modified time of the original file
    last_modified_time = os.path.getmtime(filename)

    if not bitrate:
        # Get the bitrate of the original file
        bitrate = get_video_bitrate(filename)
        # bitrate = subprocess.run([
        #     FFMPEG_PATH,
        #     "-i", filename,
        #     "-f", "null",
        #     "-"
        # ], stderr=subprocess.PIPE)
        # bitrate = bitrate.stderr.decode()
        # bitrate = bitrate[bitrate.find("bitrate"):].split()[1]
        # bitrate += "k"
        Logger.debug(f"Bitrate: {bitrate}")

    if not audio_codec:
        audio_codec = get_video_audio_codec(filename)
        Logger.debug(f"Audio codec: {audio_codec}")


    # Check if the codec is NVENC
    nvenc = False
    if 'nvenc' in codec:
        nvenc = True

    # Run the ffmpeg command
    ffmpeg_command = [
        FFMPEG_PATH,
        '-hide_banner',
        '-loglevel', *(['error'] if LOG_LEVEL < 5 else ['info']),
        '-stats',
        '-y' if rewrite else '-n',
        '-hwaccel', 'cuda' if nvenc else 'auto',
        "-i", filename,
        "-c:v", codec,
        *(["-vf", f"scale={scale}"] if scale else []),
        *(["-r", str(fps)] if fps else []),
        "-b:v", str(bitrate),
        "-c:a", audio_codec,
        '-strict', 'experimental',
        "-map_metadata", "0",
        output_file
    ]
    ffmpeg_command = [arg for arg in ffmpeg_command if arg]
    Logger.debug(f"ffmpeg_command: {ffmpeg_command}")
    result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    if result.stdout:
        Logger.info(result.stdout.decode())
    if result.stderr:
        Logger.info(result.stderr.decode())
    if result.returncode != 0:
        Logger.error('Process returned: ' + str(result.returncode))
        exit(result.returncode)

    # Set the last modified time of the new file to match the original file
    os.utime(output_file, (last_modified_time, last_modified_time))

# Loop through all .avi files in the current directory
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert video files to a different format using ffmpeg.')

    parser.add_argument(
        "input_path", type=str, 
        help="Path to the input file or folder containing video files.")
    parser.add_argument(
        "--output-folder", type=str, default="",
        help="Path to the output folder where encoded files will be saved.")
    parser.add_argument(
        "--input-format", type=str, 
        help="Input format (e.g., 'mp4', 'avi').")
    parser.add_argument(
        "--output-format", type=str,
        help="Output format (e.g., 'mp4', 'avi').")
    # codec
    parser.add_argument(
        "--codec", type=str, default="h264",
        help="Video codec for the output files (e.g., 'hevc_nvenc', 'h264').")
    parser.add_argument(
        "--bitrate", type=str, default="",
        help="Bitrate for the output files (e.g., '192k', '2M').")
    parser.add_argument(
        "--audio-codec", type=str, default="aac",
        help="Audio codec for the output files (e.g., 'aac').")
    parser.add_argument(
        "--log-level", type=str, default="INFO", choices=LOG_LEVELS.keys(),
        help="Log level. Default: 'INFO'.")
    parser.add_argument(
        "--log-file", type=str, default="./.logs/encode-video.log", 
        help="Log file path. Default: './.logs/encode-video.log'. " \
            + "To disable logging to a file, set to an empty string.")
    parser.add_argument(
        "--resolution", type=str, default="",
        help="Resolution for the output files (e.g., '1920x1080').")
    parser.add_argument(
        "--fps", type=int, default=None,
        help="Frames per second for the output files (e.g., 30).")
    parser.add_argument(
        "--rewrite", action='store_true', 
        help="Rewrite the output file if it already exists.")
    parser.add_argument(
        "-j", "--jobs", type=int, default=1,
        help="Number of jobs to run in parallel. Default is 1.")
    
    args = parser.parse_args()

    LOG_LEVEL = LOG_LEVELS[args.log_level]
    args.resolution = args.resolution.replace('_', '-')
    
    Logger.debug(f"Input path: {args.input_path}")
    Logger.debug(f"Output folder: {args.output_folder}")
    Logger.debug(f"Input format: {args.input_format}")
    Logger.debug(f"Output format: {args.output_format}")
    Logger.debug(f"Resolution: {args.resolution}")
    Logger.debug(f"FPS: {args.fps}")
    Logger.debug(f"Codec: {args.codec}")
    Logger.debug(f"Bitrate: {args.bitrate}")
    Logger.debug(f"Audio codec: {args.audio_codec}")

    import concurrent.futures

    # if no output folder is specified, save in the same folder as the input file
    if not args.output_folder:
        args.output_folder = args.input_path


    # If input is a single file
    if os.path.isfile(args.input_path):
        if not args.log_file:
            # if file, save log file in the same folder as the input file
            LOG_FILE = args.log_file = os.path.join(
                os.path.dirname(args.input_path), '.logs', 'encode-video.log')
        else:
            LOG_FILE = args.log_file
        if args.input_path.lower().endswith(f".{args.input_format}") \
            or not args.input_format:
            args.input_format = args.input_path.split('.')[-1]
            Logger.debug(f"Converting \"{os.path.isfile(args.input_path)}\"...")
            convert(
                args.input_path, args.output_folder, 
                args.output_format, args.codec, args.bitrate, 
                audio_codec=args.audio_codec,
                scale=args.resolution.replace('x', ':') \
                    if args.resolution else None,
                fps=args.fps,
                rewrite=args.rewrite)
    else:
        if not args.log_file:
            LOG_FILE = args.log_file = os.path.join(
                args.input_path, '.logs', 'encode-video.log')
        else:
            LOG_FILE = args.log_file
        
        def convert_file(file, args):
            try:
                if (file.lower().endswith(f".{args.input_format}") \
                    and os.path.isfile(os.path.join(args.input_path, file))) \
                    or not args.input_format:
                    # get full filename
                    file = os.path.join(args.input_path, file)
                    Logger.debug(f"Converting \"{file}\"...")
                    convert(
                        file, args.output_folder,
                        args.output_format, args.codec, args.bitrate,
                        audio_codec=args.audio_codec,
                        scale=args.resolution.replace('x', ':') \
                            if args.resolution else None,
                        fps=args.fps,
                        rewrite=args.rewrite)
                Logger.debug(f"Thread finished: {file}")
            except Exception as e:
                Logger.error(f"Error converting {file}: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=int(args.jobs)) as executor:
            futures = []
            for file in os.listdir(args.input_path):
                # if file is folder
                if not os.path.isfile(os.path.join(args.input_path, file)):
                    continue
                futures.append(executor.submit(convert_file, file, args))
            
            # Wait for all futures to complete
            concurrent.futures.wait(futures)

            
    Logger.happy("Conversion complete!")
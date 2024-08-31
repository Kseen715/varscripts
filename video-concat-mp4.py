#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# concat-mp4s.py
#
# Concatenate multiple MP4 files into a single video.
# ==============================================================================
# *Python 3.12 is used
# ==============================================================================

import os
import subprocess
import datetime
import argparse
from collections import Counter
import concurrent.futures

# ==============================================================================
# Logger class
# by Kseen715
# v1.5
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
                    f.seek(-LOG_FILE_MAX_SIZE, os.SEEK_END)
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
                    f.seek(-LOG_FILE_MAX_SIZE, os.SEEK_END)
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



def get_sorted_videos(directory, fextension='.mp4'):
    try:
        video_files = [f for f in os.listdir(directory) if f.lower().endswith(fextension.lower())]
    except FileNotFoundError:
        Logger.error(f"Files with extension '{fextension}' not found in {directory}")
        exit(1)
    video_files_with_time = [(os.path.join(directory, f), os.path.getmtime(os.path.join(directory, f))) for f in video_files]
    sorted_videos = sorted(video_files_with_time, key=lambda x: x[1])
    return [video[0] for video in sorted_videos]


def get_video_codec(video_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', \
        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', \
        video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode().strip()


def get_audio_codec(video_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', \
        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', \
        video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode().strip()


def get_video_resolution(video_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', \
        'stream=width,height', '-of', 'csv=p=0', video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    width, height = result.stdout.decode().strip().split(',')
    return int(width), int(height)


def get_video_bitrate(video_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', \
        'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', \
        video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return int(result.stdout.decode().strip())


def get_audio_bitrate(video_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', \
        'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', 
        video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return int(result.stdout.decode().strip())


def find_most_common_video_codec(video_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        codecs = list(executor.map(get_video_codec, video_list))
    most_common_codec = Counter(codecs).most_common(1)[0][0]
    return most_common_codec

def find_most_common_audio_codec(video_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        codecs = list(executor.map(get_audio_codec, video_list))
    most_common_codec = Counter(codecs).most_common(1)[0][0]
    return most_common_codec


def count_video_codecs(video_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        codecs = list(executor.map(get_video_codec, video_list))
    return Counter(codecs)

def count_audio_codecs(video_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        codecs = list(executor.map(get_audio_codec, video_list))
    return Counter(codecs)


def convert_to(filename, bitrate, new_file_extension='mp4', v_codec='h264', a_codec='aac', scale='scale=1280:720'):
    # Get video folder to save the new video
    video_folder = os.path.dirname(filename)
    video_folder = os.path.join(video_folder, '.temp')
    # Create temp folder if it doesn't exist
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    # Convert the video to new format
    new_filename = os.path.join(video_folder, os.path.basename(filename))
    new_filename = os.path.splitext(new_filename)[0] + '.' + new_file_extension
    ffmpeg_command = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'error',
        '-stats',
        '-y',  # Overwrite output file if it exists
        '-i', filename,
        '-vf', f'{scale}',
        '-c:v', v_codec,
        "-b:v", str(bitrate),
        '-c:a', a_codec,
        new_filename
    ]
    result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    if result.stdout:
        Logger.info(result.stdout.decode())
    if result.stderr:
        Logger.info(result.stderr.decode())
    if result.returncode != 0:
        Logger.error('Process returned: ' + str(result.returncode))
        exit(result.returncode)
    return new_filename


def many_convert_to(video_list, bitrate, new_file_extension, v_codec='h264', a_codec='aac', scale='scale=1280:720'):
    raws = []
    for video in video_list:
        raw_filename = convert_to(video, bitrate, new_file_extension, v_codec, a_codec, scale)
        raws.append(raw_filename)
    return raws


def save_file_modif_datetime(filename):
    # Get the last modified time of the original file
    last_modified_time = os.path.getmtime(filename)
    return last_modified_time


def set_file_modif_datetime(filename, last_modified_time):
    # Set the last modified time of the new file to match the original file
    os.utime(filename, (last_modified_time, last_modified_time))


def concatenate_videos(video_list, output_file, codec, bitrate, audio_codec):
    temp_folder = os.path.dirname(video_list[0])
    # Create temp folder if it doesn't exist
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    # Create a temporary text file to list the videos in order
    video_list_file = os.path.join(temp_folder, 'video_list.txt')
    with open(video_list_file, 'w') as f:
        for video in video_list:
            f.write(f"file '{video}'\n")
    # Check if the codec is NVENC
    nvenc = False
    if 'nvenc' in codec:
        nvenc = True
    # Use ffmpeg to concat the videos into a single file
    ffmpeg_command = [
        'ffmpeg', 
        '-hide_banner', 
        '-loglevel', 'warning',
        '-stats',
        '-hwaccel', 'cuda' if nvenc else 'auto',
        '-y',  # Overwrite output file if it exists
        '-f', 'concat', 
        '-safe', '0', 
        '-i', video_list_file,
        # '-filter_complex', 'concat=n={}:v=1:a=1 [v] [a]'.format(len(video_list)),
        # '-map', '[v]',
        # '-map', '[a]',
        '-c:v', codec,  # Video codec
        '-b:v', str(bitrate),  # Use the same bitrate as the input videos
        # resolution as scale=1280:720
        '-c:a', audio_codec,  # Audio codec
        '-strict', 'experimental',
        '-fps_mode', 'vfr',  # Variable frame rate to handle frame timing correctly
        '-preset', 'fast',  # Use a fast preset for encoding
        '-movflags', '+faststart',  # Optimize for streaming
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    # Execute the ffmpeg command
    result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    if result.stdout:
        Logger.info(result.stdout.decode())
    if result.stderr:
        Logger.info(result.stderr.decode())
    if result.returncode != 0:
        Logger.error('Process returned: ' + str(result.returncode))
        exit(result.returncode)
    # Clean up the temporary file
    os.remove(video_list_file)


def fancy_int(number):
    return "{:_}".format(number)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description="Concatenate multiple mp4 files into a single video.")
        parser.add_argument(
            "directory", 
            type=str, 
            help="Directory containing the mp4 files.")
        parser.add_argument(
            "output_file", 
            type=str, 
            help="Output file name.")
        # choose codec
        parser.add_argument(
            "--v-codec", type=str, default="libx264", 
            help="Video codec to use for encoding. " \
                + "[libx264, h264_nvenc, hevc, hevc_nvenc, etc.]")
        parser.add_argument(
            "--a-codec", type=str, default="aac", 
            help="Audio codec to use for encoding.")
        # -y --yes flag
        parser.add_argument(
            "-y", "--yes", action="store_true", 
            help="Automatically answer yes to all prompts.")
        # --log-level
        parser.add_argument(
            "--log-level", type=str, default="INFO", choices=LOG_LEVELS.keys(),
            help="Log level. Default: 'INFO'.")
        parser.add_argument(
            "--log-file", type=str, default="./.logs/concat-mp4s.log", 
            help="Log file path. Default: './.logs/concat-mp4s.log'. " \
                + "To disable logging to a file, set to an empty string.")
        parser.add_argument(
            "--file-extension", type=str, default=".mp4",
            help="File extension to search for. Default: '.mp4'.")
        

        args = parser.parse_args()

        LOG_LEVEL = LOG_LEVELS[args.log_level]
        LOG_FILE = os.path.join(args.directory, '.logs', 'video-concat-mp4.log')

        v_codec = args.v_codec
        a_codec = args.a_codec

        directory = args.directory
        output_file = args.output_file

        if args.file_extension:
            if args.file_extension[0] != '.': 
                args.file_extension = '.' + args.file_extension

        output_extension = output_file.split('.')[-1]

        sorted_videos = get_sorted_videos(directory, args.file_extension)
        if len(sorted_videos) == 0:
            Logger.error(f"No videos found in {directory} with extension '{args.file_extension}'")
            exit(1)
        last_datetime = save_file_modif_datetime(sorted_videos[-1])
        if not args.v_codec:
            most_common_video_codec = find_most_common_video_codec(sorted_videos)
        else:
            most_common_video_codec = args.v_codec
        if not args.a_codec:
            most_common_audio_codec = find_most_common_audio_codec(sorted_videos)
        else:
            most_common_audio_codec = a_codec
        video_codecs = dict(count_video_codecs(sorted_videos))
        audio_codecs = dict(count_audio_codecs(sorted_videos))
        Logger.info(f"=== Stats: ==========")
        Logger.info(f"Video codecs: {video_codecs}")
        Logger.info(f"Audio codecs: {audio_codecs}")

        resolution = get_video_resolution(sorted_videos[0])
        resolution = f"scale={resolution[0]}:{resolution[1]}"
        video_bitrate = get_video_bitrate(sorted_videos[0])
        audio_bitrate = get_audio_bitrate(sorted_videos[0])
        
        Logger.info(f"=== Using: ==========")
        Logger.info(f"Video codec: {most_common_video_codec}")
        Logger.info(f"Audio codec: {most_common_audio_codec}")
        Logger.info(f"Resolution: {resolution}")
        Logger.info(f"Video bitrate: {fancy_int(video_bitrate)}")
        Logger.info(f"Audio bitrate: {fancy_int(audio_bitrate)}")
        Logger.info(f"Output file: {output_file}")
        Logger.info(f"=====================")


        ok = ''
        if not args.yes:
            ok = Logger.input(f"OK? [Y/n]")
        if (ok.lower() != 'y' \
            and ok.lower() != 'yes' \
            and ok != '') \
            and not args.yes:
            Logger.error("User aborted")
            exit()

        raws = many_convert_to(sorted_videos, video_bitrate, output_extension, v_codec, a_codec, scale=resolution)
        concatenate_videos(raws, output_file, v_codec, video_bitrate, a_codec)
        
        for video in raws:
            os.remove(video)

        set_file_modif_datetime(output_file, last_datetime)
        Logger.info("Output file's last modified datetime set to the latest video's datetime")

        Logger.happy(f"Output file: {output_file}")

    except Exception as e:
        Logger.error(str(e), do_inspect=True)
    except KeyboardInterrupt:
        Logger.error("KeyboardInterrupt")

    if os.path.exists(os.path.join(directory, '.temp')):
        files = os.listdir(os.path.join(directory, '.temp'))
        for file in files:
            os.remove(os.path.join(directory, '.temp', file))
        os.rmdir(os.path.join(directory, '.temp'))
        Logger.info("Removed temp folder")

    exit()

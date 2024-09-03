# ==============================================================================
# Logger class
# by Kseen715
# v1.5.3
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

LOGGER_COLOR_MAP = {
    'DEBUG': colorama.Fore.LIGHTMAGENTA_EX,
    'INFO': colorama.Style.RESET_ALL,
    'SUCCESS': colorama.Fore.GREEN,
    'WARNING': colorama.Fore.YELLOW,
    'ERROR': colorama.Fore.RED,
    'INPUT': colorama.Fore.CYAN,
}

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
        Logger.__custom_print__(str(msg), 'DEBUG', \
                                LOGGER_COLOR_MAP['DEBUG'], \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['DEBUG'])
            


    @staticmethod
    def info(msg, do_inspect=False):
        """Log info message

        Args:
            msg (str): Info message
        """
        Logger.__custom_print__(str(msg), 'INFO', \
                                LOGGER_COLOR_MAP['INFO'], \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['INFO'])


    @staticmethod
    def happy(msg, do_inspect=False):
        """Log happy message

        Args:
            msg (str): Happy message
        """
        Logger.__custom_print__(str(msg), 'SUCCESS', \
                                LOGGER_COLOR_MAP['SUCCESS'], \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['SUCCESS'])


    @staticmethod
    def warning(msg, do_inspect=False):
        """Log warning message

        Args:
            msg (str): Warning message
        """
        Logger.__custom_print__(str(msg), 'WARNING', \
                                LOGGER_COLOR_MAP['WARNING'], \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['WARNING'])


    @staticmethod
    def error(msg, do_inspect=True):
        """Log error message

        Args:
            msg (str): Error message
        """
        Logger.__custom_print__(str(msg), 'ERROR', \
                                LOGGER_COLOR_MAP['ERROR'], \
                                do_inspect, 2, True, \
                                LOG_LEVEL >= LOG_LEVELS['ERROR'])


    @staticmethod
    def input(msg, do_inspect=False):
        """Log input message

        Args:
            msg (str): Input message
        """
        return Logger.__custom_input__(str(msg), 'INPUT', \
                                        LOGGER_COLOR_MAP['INPUT'], \
                                        do_inspect, 2)

# ==============================================================================
# End of Logger class
# ==============================================================================

import os, argparse, subprocess
import json

def read_file_label(filepath: str) -> list:
    """Read label from file. Label contains in the name of the file.
    'filename [l1,l2,...,ln].ext'

    Args:
        filepath (str): File path

    Returns:
        list: Label
    """
    filename = os.path.basename(filepath)
    if '[' not in filename or ']' not in filename:
        return []
    label = filename.split('[')[1].split(']')[0].split(',')
    return label

def generate_video_data(filepath: str) -> dict:
    """Generate video label. Using ffprobe to get video metadata.

    Args:
        directory (str): Directory with video files

    Returns:
        dict: Video label (resolution, fps, codec, bitrate)
    """
    try:
        # Run ffprobe to get video metadata
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,codec_name,bit_rate', '-of', 'json', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Parse the JSON output
        metadata = json.loads(result.stdout)
        stream = metadata['streams'][0]
        
        # Extract required information
        resolution = f"{stream['width']}x{stream['height']}"
        fps = eval(stream['r_frame_rate'])
        codec = stream['codec_name']
        bitrate = int(stream['bit_rate']) // 1000  # Convert to kbps
        
        Logger.debug(f"File: '{filepath}', resolution: {resolution}, fps: {fps}, codec: {codec}, bitrate: {bitrate}Kbps")
        return {
            'resolution': resolution,
            'fps': fps,
            'codec': codec,
            'bitrate': f"{bitrate} kbps"
        }
    except Exception as e:
        print(f"Error generating video label: {e}")
        return {}
    

def generate_video_label(filepath: str) -> str:
    """Generate video label. Using ffprobe to get video metadata.

    Args:
        directory (str): Directory with video files

    Returns:
        str: Video label
    """
    data = generate_video_data(filepath)
    data['resolution'] = data['resolution'].split('x')[1]
    data['bitrate'] = data['bitrate'].replace(' kbps', 'Kbps')
    bitrate = int(data['bitrate'].replace('Kbps', ''))

    delta = 5 # percentage

    if abs(bitrate % 1000) <= (1000 * delta / 100):
        bitrate = round(bitrate / 1000) * 1000
    # if bitrate can be displayed in Mbit/s
    if (bitrate % 1000 == 0 and bitrate >= 1000) or bitrate >= 10000:
        data['bitrate'] = f"{bitrate // 1000}Mbps" 
    elif bitrate == 0:
        data['bitrate'] = 'VBR'
    data['fps'] = round(data['fps'], 1)
    if data['fps'] % 1 == 0:
        data['fps'] = int(data['fps'])
    return f"[{data['resolution']}p,{data['fps']}fps,{data['codec']},{data['bitrate']}]"
    

def write_video_label(filepath: str, label: str):
    """Write label to file.

    Args:
        filepath (str): File path
        label (str): Label
    """
    filename = os.path.basename(filepath)
    Logger.debug(f"Old filename: '{filename}'")
    if '[' not in filename or ']' not in filename:
        new_filename = filename.split('.')[0] + ' ' + label + '.' + filename.split('.')[1]
    else:
        new_filename = filename.split('[')[0] + label + filename.split(']')[1]
    new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
    os.rename(filepath, new_filepath)
    Logger.debug(f"Renamed file: '{filepath}' -> '{new_filepath}'")


def get_write_video_label(filepath: str):
    """Get and write video label to file.

    Args:
        filepath (str): File path
    """
    # is file exists
    if not os.path.exists(filepath):
        Logger.error(f"File not found: '{filepath}'")
        return
    old_label = read_file_label(filepath)
    old_label = '[' + ','.join(old_label) + ']'
    label = generate_video_label(filepath)

    Logger.info(f"File: '{filepath}'")
    if old_label != label:
        write_video_label(filepath, label)
        Logger.info(f"File: '{filepath}'")
        Logger.info(f"Label changed: '{old_label}' -> '{label}'")
    else:
        Logger.info(f"Label correct: '{label}', skipping...")


def get_list_of_files(directory: str, ext: str) -> list:
    """Get list of files with specified extension in directory.

    Args:
        directory (str): Directory with video files
        ext (str): File extension

    Returns:
        list: List of files
    """
    files = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            files.append(os.path.join(directory, file))
    return files

import concurrent.futures
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get and write video label to file')

    parser.add_argument(
        'filepath',
        type=str,
        help='File path'
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO", choices=LOG_LEVELS.keys(),
        help="Log level. Default: 'INFO'.")
    parser.add_argument(
        "--log-file", type=str, default=LOG_FILE,
        help="Log file. Default: './.logs/log.log'.")
    parser.add_argument(
        "-j", "--jobs", type=int, default=os.cpu_count(),
    )
    parser.add_argument(
        "--file-ext", type=str, default='.mp4',
        help="File extension. Default: '.mp4'."
    )

    args = parser.parse_args()

    LOG_LEVEL = LOG_LEVELS[args.log_level]

    if os.path.isdir(args.filepath):
        files = get_list_of_files(args.filepath, args.file_ext)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [executor.submit(get_write_video_label, file) for file in files]

        concurrent.futures.wait(futures)
    else:
        get_write_video_label(args.filepath)

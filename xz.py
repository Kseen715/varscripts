# from command line get the file name or folder name, and compress it
# also accept the -d option to decompress the file
# also accept the -e option to specify the extension of the file
# then xz -T0 -9 all files

import os
import sys
import getopt
import subprocess
import argparse
import time


def compress_file(file_name, threads):
    print('Compressing file: {}'.format(file_name))
    cmd = ['xz', '-T{}'.format(threads), file_name]
    print(' '.join(cmd[:len(cmd) - 1] + ['"{}"'.format(file_name)]))

    start = time.time()
    subprocess.call(cmd)
    end = time.time()

    print('Compressed file: {} in {} seconds'.format(file_name, end - start))


def decompress_file(file_name, threads):
    print('Decompressing file: {}'.format(file_name))
    cmd = ['xz', '-T0', '-d', file_name]
    print(' '.join(cmd[:len(cmd) - 1] + ['"{}"'.format(file_name)]))

    start = time.time()
    subprocess.call(cmd)
    end = time.time()

    print('Decompressed file: {} in {} seconds'.format(file_name, end - start))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compress or decompress file')
    parser.add_argument(
        'path', help='file/folder with files to compress or decompress')
    parser.add_argument('-d', action='store_true', help='decompress file')
    parser.add_argument('-e', help='specify the extension of the file')
    parser.add_argument('-t', help='threads')
    args = parser.parse_args()

    threads = 1
    if args.t:
        threads = args.t

    files = []
    if os.path.isfile(args.path):
        files.append(args.path)
    elif os.path.isdir(args.path):
        for root, dirs, fs in os.walk(args.path):
            for f in fs:
                files.append(os.path.join(root, f))

    if args.d:
        for f in files:
            if f.endswith('.xz'):
                decompress_file(f, threads)

    else:
        for f in files:
            if args.e:
                if f.endswith(args.e):
                    compress_file(f, threads)
            else:
                compress_file(f, threads)

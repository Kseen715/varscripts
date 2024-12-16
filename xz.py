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

total_size_before = 0
total_size_after = 0

def compress_file(file_name, threads):
    global total_size_before, total_size_after
    cmd = ['xz', '-T{}'.format(threads), file_name]
    print(' '.join(cmd[:len(cmd) - 1] + ['"{}"'.format(file_name)]))
    file_size_before = os.path.getsize(file_name)
    total_size_before += file_size_before

    start = time.time()
    subprocess.call(cmd)
    end = time.time()

    file_size_after = os.path.getsize(file_name + '.xz')
    total_size_after += file_size_after
    ratio = 100 - (file_size_after / file_size_before * 100)
    print('\t> Took {:.6f}s'.format(end - start))
    print('\t> Compression ratio: {:.3f}%'.format(ratio))


def decompress_file(file_name, threads):
    cmd = ['xz', '-T{}'.format(threads), '-d', file_name]
    print(' '.join(cmd[:len(cmd) - 1] + ['"{}"'.format(file_name)]))

    start = time.time()
    subprocess.call(cmd)
    end = time.time()

    print('\t> Took {:.6f}s'.format(end - start))


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
            if not f.endswith('.xz'):
                if args.e:
                    if f.endswith(args.e):
                        compress_file(f, threads)
                else:
                    compress_file(f, threads)
        files = [f for f in files if not f.endswith('.xz')]
        if len(files) > 1:
            def get_size_str(size):
                if size < 1024:
                    return '{:.3f}B'.format(size)
                elif size < 1024 * 1024:
                    return '{:.3f}KB'.format(size / 1024)
                elif size < 1024 * 1024 * 1024:
                    return '{:.3f}MB'.format(size / 1024 / 1024)
                else:
                    return '{:.3f}GB'.format(size / 1024 / 1024 / 1024)
            print('Total size before: {}'.format(get_size_str(total_size_before)))
            print('Total size after: {}'.format(get_size_str(total_size_after)))
            print('Total compression ratio: {:.3f}%'.format(100 - (total_size_after / total_size_before * 100)))


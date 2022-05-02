import contextlib
import os
import time

from ppm.ppm_compress import compress
from ppm.arithmeticcoding import BitOutputStream, BitInputStream
from ppm.ppm_decompress import decompress


def compressing(file, filepath):
    start = time.time()
    start_file_size = len(file.read())
    with contextlib.closing(BitOutputStream(open(filepath, "wb"))) as bitout:
        compress(file, bitout)
    work_time = time.time() - start
    end_file_size = os.stat(filepath).st_size
    return work_time, start_file_size, end_file_size


def decompressing(file, filepath):
    with open(filepath, "wb") as out:
        bitin = BitInputStream(file)
        decompress(bitin, out)

import contextlib

from ppm.ppm_compress import compress
from ppm.arithmeticcoding import BitOutputStream


def compressing(file, filepath):
    with open(file.filename, "rb") as inp,\
            contextlib.closing(BitOutputStream(filepath, "wb")) as bitout:
        compress(inp, bitout)

"""
mp3.py : do mp3 things
"""

from enum import Enum

class MP3Header(object):
    """
    Parse an MP3 header according to the following bit order:
    AAAAAAAA AAABBCCD EEEEFFGH IIJJKLMM

    A: sync_word (1-11)
    B: mpeg_version (12-13)
    C: layer (14-15)
    D: error_protection (16)
    E: bit_rate (17-20)
    F: frequency (21-22)
    G: pad_bit (23)
    H: priv_bit (24)
    I: channel (25-26)
    J: mode_extention (27-28)
    K: copy (29)
    L: original (30)
    M: emphasis (31-32)

    Attributes:
        sync_word: should always be 12-bit string of 1s
        mpeg_version: 00 - mpeg v2.5 (unofficial)
                      01 - reserved
                      10 - mpeg v2
                      11 - mpeg v1
        layer: 00 - reserved
               01 - layer III
               10 - layer II
               11 - layer I
        error_protection: whether or not a 16-bit CRC follows
        bit_rate: 1111 = bad
        frequency: ever have a hz donut?
        pad_bit: single bit for representing if this frame has had thai recently
        priv_bit: unknown
        channel: 00 - stereo
                 01 - joint stereo
                 10 - dual channel
                 11 - mono
        mode_extention: only present if mode is "joint stereo"
        copy: single bit to determine if this is copyrighted
        original: "copy of original media", they say
        emphasis: pretty self-explanatory
    """

    def __init__(self, raw_bytes):
        self.bitstring = ''
        for i in raw_bytes:
            bit_str = pad_to_eight_bits(bin(i))
            self.bitstring += bit_str
        self.sync_word = self.bitstring[:11]

        for i in MPEGVersionEncodings:
            if i.value == self.bitstring[11:13]:
                self.mpeg_version = i

        for i in LayerEncodings:
            if i.value == self.bitstring[13:15]:
                self.layer = i

        self.error_protection = self.bitstring[15]
        self.bit_rate = self.bitstring[16:20]
        self.frequency = self.bitstring[20:22]
        self.pad_bit = self.bitstring[22]
        self.priv_bit = self.bitstring[23]

        for i in ChannelEncodings:
            if i.value == self.bitstring[24:26]:
                self.channel = i

        self.mode_extention = self.bitstring[26:28]
        self.copy = self.bitstring[28]
        self.original = self.bitstring[29]
        self.emphasis = self.bitstring[30:]

class ChannelEncodings(Enum):
    """
    channel: 00 - stereo
             01 - joint stereo
             10 - dual channel
             11 - mono
    """
    STEREO = '00'
    JOINT_STEREO = '01'
    DUAL_CHANNEL = '10'
    MONO = '11'

class LayerEncodings(Enum):
    """
    layer: 00 - reserved
           01 - layer III
           10 - layer II
           11 - layer I
    """
    RESERVED = '00'
    ONE = '11'
    TWO = '10'
    THREE = '01'

class MPEGVersionEncodings(Enum):
    """
    mpeg_version: 00 - mpeg v2.5 (unofficial)
                  01 - reserved
                  10 - mpeg v2
                  11 - mpeg v1
    """
    MPEG_V1 = '11'
    MPEG_V2 = '10'
    MPEG_V2_5 = '00'
    RESERVED = '01'

def pad_to_eight_bits(bitstr: str) -> str:
    """
    pad_to_eight_bits : expects a binary string like those produced by bin()
    """
    bitstr = bitstr[2:]
    zeros = '0' * (8 - len(bitstr))
    return zeros + bitstr


class MP3File(object):
    """
    MP3File : look for frames and break them up into headers and data or whatever
    maybe include utilities for playing songs too

    support reading data chunks and getting other kinds of information as well

    The side information is 17 bytes for mono, 32 bytes otherwise.
    """

    def __init__(self, mp3_file):
        self.filename = mp3_file
        self.position = 0
        # open file, read data into header and data frame objects
        with open(mp3_file, 'rb') as audio:
            # read audio data into a buffer. stop once we've reached the first mp3 frame
            buf = audio.read(2)
            while not self._is_frame_start(buf[-2], buf[-1]):
                buf += audio.read(1)
            # should we save the start location of the mp3 data? Yesy
            self.position = audio.tell() - 2
        return

    def read_frames(self, nframes: int) -> (list, list):
        """
        read_frames
        return two equal-length arrays:
          - headers for the number of frames read
          - data of each frame
        """
        headers = []
        data = []
        if nframes == 0:
            return headers, data
        with open(self.filename, 'rb') as audio:
            still_reading = True
            audio.seek(self.position)
            while still_reading:
                buf = audio.read(4)
                header = MP3Header(buf)
                headers.append(header)
                if header.error_protection == '1':
                    # who cares about the 16-bit crc? let's get to the freakin MUSIC!
                    audio.read(2)
                if header.channel == ChannelEncodings.MONO:
                    # side info is 17 bytes!
                    side_info = audio.read(17)
                else:
                    # side info is 32 bytes!
                    side_info = audio.read(32)
                if audio.peek(1) == b'':
                    break
                frame = audio.read(1)
                while True:
                    new_byte = audio.peek(1)
                    if new_byte == b'':
                        still_reading = False
                        break
                    frame += audio.read(1)
                    if self._is_frame_start(frame[-2], frame[-1]):
                        # we've stumbled upon a new 
                        audio.seek(audio.tell() - 2)
                        frame = frame[:-2]
                        break
                data.append(frame)
            self.position = audio.tell()
        return headers, data
    
    def _is_frame_start(self, byte1, byte2):
        return (byte1 == 255 and (byte2 & 0xF0 != 240 or byte2 & 0xE0 != 224))

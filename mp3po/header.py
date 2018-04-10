"""
header.py : all things MP3 headers
"""

from enum import Enum
from .util.utils import Bits

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
        emphasis: 00 - none
                  01 - 50/15 ms
                  10 - reserved
                  11 - CCIT J.17

        Frame Size = ( (Samples Per Frame / 8 * Bitrate) / Sampling Rate) + Padding Size
    """

    bitrate_table = {
        LayerEncodings.ONE : {
            '0001' : 32000,
            '0010' : 64000,
            '0011' : 96000,
            '0100' : 128000,
            '0101' : 160000,
            '0110' : 192000,
            '0111' : 224000,
            '1000' : 256000,
            '1001' : 288000,
            '1010' : 320000,
            '1011' : 352000,
            '1100' : 384000,
            '1101' : 416000,
            '1110' : 448000,
        },
        LayerEncodings.TWO : {
            '0001' : 32000,
            '0010' : 48000,
            '0011' : 56000,
            '0100' : 64000,
            '0101' : 80000,
            '0110' : 96000,
            '0111' : 112000,
            '1000' : 128000,
            '1001' : 160000,
            '1010' : 192000,
            '1011' : 224000,
            '1100' : 256000,
            '1101' : 320000,
            '1110' : 384000,
        },
        LayerEncodings.THREE : {
            '0001' : 32000,
            '0010' : 40000,
            '0011' : 48000,
            '0100' : 56000,
            '0101' : 64000,
            '0110' : 80000,
            '0111' : 96000,
            '1000' : 112000,
            '1001' : 128000,
            '1010' : 160000,
            '1011' : 192000,
            '1100' : 224000,
            '1101' : 256000,
            '1110' : 320000,
        },
    }

    frequency_table = {
        MPEGVersionEncodings.MPEG_V1 : {
            '00' : 44100,
            '01' : 48000,
            '10' : 32000,
        },
        MPEGVersionEncodings.MPEG_V2 : {
            '00' : 22050,
            '01' : 24000,
            '10' : 16000,
        },
        MPEGVersionEncodings.MPEG_V2_5 : {
            '00' : 11025,
            '01' : 12000,
            '10' : 8000,
        },
    }

    padding_table = {
        LayerEncodings.ONE : 4,
        LayerEncodings.TWO : 1,
        LayerEncodings.THREE : 1,
    }

    samples_per_frame_table = {
        LayerEncodings.ONE : {
            MPEGVersionEncodings.MPEG_V1 : 384,
            MPEGVersionEncodings.MPEG_V2 : 384,
            MPEGVersionEncodings.MPEG_V2_5 : 384,
        },
        LayerEncodings.TWO : {
            MPEGVersionEncodings.MPEG_V1 : 1152,
            MPEGVersionEncodings.MPEG_V2 : 1152,
            MPEGVersionEncodings.MPEG_V2_5 : 1152,
        },
        LayerEncodings.THREE : {
            MPEGVersionEncodings.MPEG_V1 : 1152,
            MPEGVersionEncodings.MPEG_V2 : 576,
            MPEGVersionEncodings.MPEG_V2_5 : 576,
        },
    }

    def __init__(self, raw_bytes):
        self._bits = Bits()
        for i in raw_bytes:
            self._bits.add_bits(i)
        self.sync_word = self._bits.read(11)

        mpeg_bits = self._bits.read(2)
        for i in MPEGVersionEncodings:
            if i.value == mpeg_bits:
                self.mpeg_version = i

        layer_bits = self._bits.read(2)
        for i in LayerEncodings:
            if i.value == layer_bits:
                self.layer = i

        self.error_protection = self._bits.read(1)
        self._bit_rate_bits = self._bits.read(4)
        self._frequency_bits = self._bits.read(2)
        self.pad_bit = self._bits.read(1)
        self.priv_bit = self._bits.read(1)

        channel_bits = self._bits.read(2)
        for i in ChannelEncodings:
            if i.value == channel_bits:
                self.channel = i

        self.mode_extention = self._bits.read(2)
        self.copy = self._bits.read(1)
        self.original = self._bits.read(1)
        self.emphasis = self._bits.read(2)

        self.bitrate = self._check_for_valid_value(self.bitrate_table,
                                                   'layer',
                                                   self.layer,
                                                   'bitrate',
                                                   self._bit_rate_bits)

        self.frequency = self._check_for_valid_value(self.frequency_table,
                                                     'mpeg_version',
                                                     self.mpeg_version,
                                                     'frequency',
                                                     self._frequency_bits)

        self.padding = self.padding_table[self.layer]

        self.samples_per_frame = self._check_for_valid_value(self.samples_per_frame_table,
                                                             'layer',
                                                             self.layer,
                                                             'mpeg_version',
                                                             self.mpeg_version)
        # calculate the frame size in bytes
        self.frame_size = (((144 * self.bitrate)/self.frequency)
                           + (int(self.pad_bit, 2) * self.padding))

    def _check_for_valid_value(self, lookup_table, key1, value1, key2, value2):
        if (value1 not in lookup_table or value2 not in lookup_table[value1]):
            raise InvalidFieldEncodingException('Invalid combination: cannot have value {0} for'
                                                'field {1} with {2} for {3}'.format(value1, key1,
                                                                                    value2, key2))
        return lookup_table[value1][value2]

    @staticmethod
    def _pad_to_eight_bits(bitstr: str) -> str:
        """
        _pad_to_eight_bits : expects a binary string like those produced by bin()
        """
        bitstr = bitstr[2:]
        zeros = '0' * (8 - len(bitstr))
        return zeros + bitstr

class InvalidFieldEncodingException(Exception):
    """
    InvalidFieldEncodingException : throw this when you find invalid fields in MP3 headers
    """
    pass

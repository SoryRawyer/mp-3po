"""
sideinfo.py : get the side information for an MP3 frame
"""

import json

from collections import defaultdict
from .util.bits import Bits
from .header import ChannelEncodings, MP3Header

class ChannelSideInfo(object):
    """
    ChannelSideInfo : container for all that pesky side information per channel

    Attributes :
    - part2_3_length : 1 value
    - big_values : 1 value
    - global_gain : 1 value
    - scalefac_compress : 1 value
    - window_switching_flag : 1 value
    - block_type : 1 value
    - mixed_block_flag : 1 value
    - table_select : 2 values
    - region0_count : 1 value
    - region0_count : 1 value
    - sub_block_gain : 3 values
    - preflag : 1 value
    - scalefac_scale : 1 value
    - count1_table_select : 1 value
    """

    def __init__(self, index: int, bits: Bits):
        self.index = index
        # self.bits = bits # do we actually want to keep a copy of the bitstring here?

        self.part2_3_length = bits.read_bits_as_int(12)
        self.big_values = bits.read_bits_as_int(9)
        self.global_gain = bits.read_bits_as_int(8)
        self.scalefac_compress = bits.read_bits_as_int(4)
        self.window_switch_flag = bits.read_bits_as_int(1)
        self.table_select = [0] * 3
        self.sub_block_gain = [0] * 3
        if self.window_switch_flag == 1:
            self.block_type = bits.read_bits_as_int(2)
            self.mixed_block_flag = bits.read_bits_as_int(1)
            for i in range(0, 2):
                self.table_select[i] = bits.read_bits_as_int(5)
            for i in range(0, 3):
                self.sub_block_gain[i] = bits.read_bits_as_int(3)
            # the below code is present in
            # https://github.com/hajimehoshi/go-mp3/blob/master/internal/sideinfo/sideinfo.go
            # but it's making my tests fail so (shrug)

            # UPDATE: I think it's time to bring this back
            if (self.block_type == 2 and self.mixed_block_flag == 0):
                self.region0_count = 8
            else:
                self.region0_count = 7
            # TODO: come back and look at this later if stuff starts failing
            self.region1_count = 20 - self.region0_count
        else:
            for i in range(0, 3):
                self.table_select[i] = bits.read_bits_as_int(5)
            self.region0_count = bits.read_bits_as_int(4)
            self.region1_count = bits.read_bits_as_int(3)
            # I don't think we need to set block_type or mixed_blog_flag
            # if window_switch_flag isn't set
            self.block_type = 0
            self.mixed_block_flag = 0
            for _ in range(0, 3):
                self.sub_block_gain[i] = 0
        self.preflag = bits.read_bits_as_int(1)
        self.scalefac_scale = bits.read_bits_as_int(1)
        self.count1_table_select = bits.read_bits_as_int(1)

    def __str__(self):
        """
        __str__ : string representation of a channel
        """
        return json.dumps({
            'part2_3_length' : self.part2_3_length,
            'big_values' : self.big_values,
            'global_gain' : self.global_gain,
            'scalefac_compress' : self.scalefac_compress,
            'window_switch_flag' : self.window_switch_flag,
            'block_type' : self.block_type,
            'mixed_block_flag' : self.mixed_block_flag,
            'table_select' : self.table_select,
            'region0_count' : self.region0_count,
            'region0_count' : self.region0_count,
            'sub_block_gain' : self.sub_block_gain,
            'preflag' : self.preflag,
            'scalefac_scale' : self.scalefac_scale,
            'count1_table_select' : self.count1_table_select,
        })

class Granule(object):
    """
    Granule : basically just a container for a two-tuple of Channels
    """

    def __init__(self, index, bits):
        self.index = index
        self.bits = bits
        self.channels = []
        self.channels.append(ChannelSideInfo(0, self.bits))
        self.channels.append(ChannelSideInfo(1, self.bits))

    def collect_channel_values(self, key):
        """
        collect_channel_values : collect all the channel values associated with the given key
        """
        result = []
        for chan in self.channels:
            result.append(chan.__getattribute__(key))
        return result

    def __str__(self):
        """
        __str__ : string representation of a granule
        """
        return json.dumps({
            'index' : self.index,
            'channels' : [str(c) for c in self.channels],
        })

class SideInfo(object):
    """
    SideInfo : parse the side information for an MP3 frame

    Attributes:
        main_data_begin - 9 bits
        private_bits - 5 bites for mono; 3 bits for stereo
        scfsi
        granule_one:
        - part2_3_length
        - big_values
        - global_gain
        - scalefac_compress
        - window_switching_flag
        - block_type
        side_info for gr2 (granule 2)
    """

    def __init__(self, header: MP3Header, raw_bytes):
        """
        __init__ : read the given mp3_file and parse the side information
        this expected the mp3_file file object to already be pointing to the side information
        this will modify the mp3_file file object to point to the first byte
            after the side information
        """
        channels = 1
        if header.channel != ChannelEncodings.MONO:
            channels = 2
        bits = Bits()
        for i in raw_bytes:
            bits.add_bits(i)
        self._bitstring = bits
        # each entry into the two granules object will be an array with each index
        # corresponding to the channel - 1
        self.granules = {
            0 : defaultdict(list),
            1 : defaultdict(list),
        }
        self.main_data_begin = self._bitstring.read_bits_as_int(9)
        if header.channel == ChannelEncodings.MONO:
            self.private_bits = self._bitstring.read_bits_as_int(5)
        else:
            self.private_bits = self._bitstring.read_bits_as_int(3)
        self.scfsi_band = [0] * channels
        for i in range(0, channels):
            self.scfsi_band[i] = [0] * 4
            for j in range(0, 4):
                self.scfsi_band[i][j] = self._bitstring.read_bits_as_int(1)
        for i in range(0, 2):
            self.granules[i] = Granule(i, self._bitstring)

    def __str__(self):
        """
        __str__ : string representation of each thing
        """
        return json.dumps({
            'granules' : [str(self.granules[g]) for g in self.granules],
            'main_data_begin' : self.main_data_begin,
            'private_bits' : self.private_bits,
            'scfsi_band' : self.scfsi_band,
        }).replace('"', '')

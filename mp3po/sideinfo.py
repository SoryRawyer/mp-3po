"""
sideinfo.py : get the side information for an MP3 frame
"""

from collections import defaultdict
from .util.utils import Bits
from .header import ChannelEncodings, MP3Header

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
        self.scfsi_band = []
        for i in range(0, channels):
            self.scfsi_band.append([])
            for j in range(0, 4):
                self.scfsi_band[-1].append(self._bitstring.read_bits_as_int(1))
        for i in range(0, 2):
            for j in range(0, channels):
                # print(self.granules)
                self.granules[i]['part2_3_length'].append(self._bitstring.read_bits_as_int(12))
                self.granules[i]['big_values'].append(self._bitstring.read_bits_as_int(9))
                self.granules[i]['global_gain'].append(self._bitstring.read_bits_as_int(8))
                self.granules[i]['scalefac_compress'].append(self._bitstring.read_bits_as_int(4))
                self.granules[i]['window_switch_flag'].append(self._bitstring.read_bits_as_int(1))
                if self.granules[i]['window_switch_flag'][j] == 1:
                    self.granules[i]['block_type'].append(self._bitstring.read_bits_as_int(2))
                    self.granules[i]['mixed_block_flag'].append(self._bitstring.read_bits_as_int(1))
                    self.granules[i]['table_select'].append([])
                    for _ in range(0, 2):
                        self.granules[i]['table_select'][-1].append(self._bitstring.read_bits_as_int(5))
                    self.granules[i]['sub_block_gain'].append([])
                    for _ in range(0, 3):
                        self.granules[i]['sub_block_gain'][-1].append(self._bitstring.read_bits_as_int(3))
                    if (self.granules[i]['block_type'][j] == 2
                            and self.granules[i]['mixed_block_flag'][j] == 0):
                        self.granules[i]['region0_count'].append(8)
                    else:
                        self.granules[i]['region0_count'].append(7)
                    self.granules[i]['region1_count'].append(20 -
                                                             self.granules[i]['region0_count'][j])
                else:
                    self.granules[i]['table_select'].append([])
                    for _ in range(0, 3):
                        self.granules[i]['table_select'][-1].append(self._bitstring.read_bits_as_int(5))
                    self.granules[i]['region0_count'].append(self._bitstring.read_bits_as_int(4))
                    self.granules[i]['region1_count'].append(self._bitstring.read_bits_as_int(3))
                    self.granules[i]['block_type'] = [0]
                    self.granules[i]['mixed_block_flag'] = [0]
                self.granules[i]['preflag'].append(self._bitstring.read_bits_as_int(1))
                self.granules[i]['scalefac_scale'].append(self._bitstring.read_bits_as_int(1))
                self.granules[i]['count1_table_select'].append(self._bitstring.read_bits_as_int(1))

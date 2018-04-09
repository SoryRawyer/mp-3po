"""
sideinfo.py : get the side information for an MP3 frame
"""

from collections import defaultdict
from util.utils import Bits
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

    def __init__(self, header: MP3Header, mp3_file):
        """
        __init__ : read the given mp3_file and parse the side information
        this expected the mp3_file file object to already be pointing to the side information
        this will modify the mp3_file file object to point to the first byte
            after the side information
        """
        self.side_info_length = 17
        channels = 1
        if header.channel != ChannelEncodings.MONO:
            self.side_info_length = 32
            channels = 2
        self.side_info_bytes = mp3_file.read(self.side_info_length)
        bitstring = bin(self.side_info_bytes).split('b')[1]
        self._bitstring = Bits((((self.side_info_length * 8) - len(bitstring)) * '0') + bitstring)
        # each entry into the two granules object will be an array with each index
        # corresponding to the channel - 1
        self.granules = {
            0 : defaultdict(list),
            1 : defaultdict(list),
        }
        for i in range(0, 2):
            for j in range(0, channels):
                self.granules[i]['part2_3_length'].append(self._bitstring.read(12))
                self.granules[i]['big_values'].append(self._bitstring.read(9))
                self.granules[i]['global_gain'].append(self._bitstring.read(8))
                self.granules[i]['scalefac_compress'].append(self._bitstring.read(4))
                self.granules[i]['window_switch_flag'].append(self._bitstring.read(1))
                if int(self.granules[i]['window_switch_flag'][j], 2) == 1:
                    self.granules[i]['block_type'].append(self._bitstring.read(2))
                    self.granules[i]['mixed_block_flag'].append(self._bitstring.read(1))
                    self.granules[i]['table_select'].append([])
                    for _ in range(0, 2):
                        self.granules[i]['table_select'][j].append(self._bitstring.read(5))
                    self.granules[i]['sub_block_gain'].append([])
                    for _ in range(0, 3):
                        self.granules[i]['sub_block_gain'][j].append(self._bitstring.read(3))
                    if (self.granules[i]['block_type'][j] == 2
                            and self.granules[i]['mixed_block_flag'][j] == 0):
                        self.granules[i]['region0_count'].append(8)
                    else:
                        self.granules[i]['region0_count'].append(7)
                    self.granules[i]['region1_count'].append(20 -
                                                             self.granules[i]['region0_count'][j])
                else:
                    for _ in range(0, 3):
                        self.granules[i]['table_select'].append(self._bitstring.read(5))
                    self.granules[i]['region0_count'].append(self._bitstring.read(4))
                    self.granules[i]['region1_count'].append(self._bitstring.read(3))
                    self.granules[i]['block_type'] = 0
                self.granules[i]['preflag'].append(self._bitstring.read(1))
                self.granules[i]['scalefac_scale'].append(self._bitstring.read(1))
                self.granules[i]['count1_table_select'].append(self._bitstring.read(1))

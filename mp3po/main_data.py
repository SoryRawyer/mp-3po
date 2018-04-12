"""
main_data.py : a place for all things main data
"""

from .header import MP3Header, ChannelEncodings
from .sideinfo import SideInfo
from .util.utils import Bits

class MainData(object):
    """
    MainData : store operations related to the main data
    """

    scalefac_sizes = [
        (0, 0), (0, 1), (0, 2), (0, 3), (3, 0), (1, 1), (1, 2), (1, 3),
        (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3), (4, 2), (4, 3),
    ]

    def __init__(self, header: MP3Header, side_info: SideInfo, raw_bytes):
        self._bits = Bits()
        self.side_info = side_info
        for i in raw_bytes:
            self._bits.add_bits(i)
        channels = 1
        if header.channel != ChannelEncodings.MONO:
            channels = 2

        self.unpack_scale_factors(channels)
        self.unpack_huffman()


    def unpack_scale_factors(self, channels):
        """
        unpack_scale_factors : use the side information to determine how many bits
        to read for each scale factor band. the side information will also tell us
        whether or not scale factors are shared between granules for any bands
        """
        self.scalefac_l = [0] * 2
        self.scalefac_s = [0] * 2
        # i: granule; j: channel
        for gran in range(0, 2):
            granule = self.side_info.granules[gran]
            self.scalefac_l[gran] = [0] * 2
            self.scalefac_s[gran] = [0] * 2
            for chan in range(0, channels):
                slen1 = self.scalefac_sizes[granule['scalefac_compress'][chan]][0]
                slen2 = self.scalefac_sizes[granule['scalefac_compress'][chan]][1]
                self.scalefac_l[gran][chan] = [0] * 22
                self.scalefac_s[gran][chan] = [0] * 13
                if granule['window_switch_flag'] == 1 and granule['block_type'][chan] == 2:
                    if granule['mixed_block_flag'][chan] != 0:
                        # mixed blocks
                        for k in range(0, 8):
                            self.scalefac_l[gran][chan][k] = self._bits.read(slen1)
                        for k in range(3, 6):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for l in range(0, 3):
                                self.scalefac_s[gran][chan][k][l] = self._bits.read(slen1)
                        for k in range(6, 12):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for l in range(0, 3):
                                self.scalefac_s[gran][chan][k][l] = self._bits.read(slen2)
                    else:
                        for k in range(3, 6):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for l in range(0, 3):
                                self.scalefac_s[gran][chan][k][l] = self._bits.read(slen1)
                        for k in range(6, 12):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for l in range(0, 3):
                                self.scalefac_s[gran][chan][k][l] = self._bits.read(slen2)
                else:
                    # scale factors for long blocks
                    if gran == 0:
                        for sfb in range(0, 11):
                            self.scalefac_l[gran][chan][sfb] = self._bits.read(slen1)
                        for sfb in range(11, 21):
                            self.scalefac_l[gran][chan][sfb] = self._bits.read(slen2)
                    else:
                        # reuse the scale factors from the first granule (maybe)
                        indices = [(0, 6), (6, 11), (11, 16), (16, 21)]
                        for k in range(0, 2):
                            start, end = indices[k]
                            for sfb in range(start, end):
                                if self.side_info.scfsi_band[chan][k] == 1:
                                    self.scalefac_l[gran][chan][sfb] = self.scalefac_l[gran-1][chan][sfb]
                                else:
                                    self.scalefac_l[gran][chan][sfb] = self._bits.read(slen1)
                        for k in range(2, 4):
                            start, end = indices[k]
                            for sfb in range(start, end):
                                if self.side_info.scfsi_band[chan][k] == 1:
                                    self.scalefac_l[gran][chan][sfb] = self.scalefac_l[gran-1][chan][sfb]
                                else:
                                    self.scalefac_l[gran][chan][sfb] = self._bits.read(slen2)
                    self.scalefac_l[gran][chan][21] = 0

    def unpack_huffman(self):
        """
        unpack_huffman : unpack the huffman samples contained in ye olde maine data
        """
        pass

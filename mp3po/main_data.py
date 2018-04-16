"""
main_data.py : a place for all things main data
"""

from .header import MP3Header, ChannelEncodings
from .huffman import decode_big_values, decode_quadruples
from .sideinfo import SideInfo
from .util.bits import Bits

class MainData(object):
    """
    MainData : store operations related to the main data
    """

    scalefac_sizes = [
        (0, 0), (0, 1), (0, 2), (0, 3), (3, 0), (1, 1), (1, 2), (1, 3),
        (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3), (4, 2), (4, 3),
    ]

    scale_band_indicies = {
        44100: {
            'L': [0, 4, 8, 12, 16, 20, 24, 30, 36, 44, 52, 62, 74, 90, 110,
                  134, 162, 196, 238, 288, 342, 418, 576],
    		'S': [0, 4, 8, 12, 16, 22, 30, 40, 52, 66, 84, 106, 136, 192],
        },
        48000: {
            'L': [0, 4, 8, 12, 16, 20, 24, 30, 36, 42, 50, 60, 72, 88, 106,
                  128, 156, 190, 230, 276, 330, 384, 576],
            'S': [0, 4, 8, 12, 16, 22, 28, 38, 50, 64, 80, 100, 126, 192],
        },
        32000: {
            'L': [0, 4, 8, 12, 16, 20, 24, 30, 36, 44, 54, 66, 82, 102, 126,
                  156, 194, 240, 296, 364, 448, 550, 576],
            'S': [0, 4, 8, 12, 16, 22, 30, 42, 58, 78, 104, 138, 180, 192],
        },
    }

    def __init__(self, header: MP3Header, side_info: SideInfo, raw_bytes):
        self._bits = Bits()
        self.header = header
        self.side_info = side_info
        print(len(raw_bytes))
        for i in raw_bytes:
            self._bits.add_bits(i)
        channels = 1
        if header.channel != ChannelEncodings.MONO:
            channels = 2

        self.unpack_scale_factors(channels)
        self.unpack_huffman(channels)


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
                            for sfb in range(0, 3):
                                self.scalefac_s[gran][chan][k][sfb] = self._bits.read(slen1)
                        for k in range(6, 12):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for sfb in range(0, 3):
                                self.scalefac_s[gran][chan][k][sfb] = self._bits.read(slen2)
                    else:
                        for k in range(3, 6):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for sfb in range(0, 3):
                                self.scalefac_s[gran][chan][k][sfb] = self._bits.read(slen1)
                        for k in range(6, 12):
                            self.scalefac_s[gran][chan][k] = [0] * 3
                            for sfb in range(0, 3):
                                self.scalefac_s[gran][chan][k][sfb] = self._bits.read(slen2)
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

    def unpack_huffman(self, channels):
        """
        unpack_huffman : unpack the huffman samples contained in ye olde maine data
        5 regions:
        - big values
        - big values
        - big values
        - count1/quadruple
        - zero

        we're assuming here that self.bits() has been put at the right location
        for us to just start reading
        """

        samples_per_granule = 576
        self.frequency_lines = [0] * 2
        for gran in range(0, 2):
            self.frequency_lines[gran] = [0] * 2
            granule = self.side_info.granules[gran]
            for chan in range(0, channels):
                self.frequency_lines[gran][chan] = [0] * 576
                print(chan, granule)
                if granule['window_switch_flag'][chan] == 1 and granule['block_type'][chan] == 2:
                    region_1_start = 36
                    region_2_start = samples_per_granule
                else:
                    sampling_freq = self.header.frequency
                    long_bands = self.scale_band_indicies[sampling_freq]['L']
                    region_1_start = long_bands[granule['region0_count'][chan] + 1]

                    region_2_idx = (granule['region0_count'][chan] +
                                    granule['region1_count'][chan] + 2)
                    region_2_start = long_bands[region_2_idx]
                print(granule['big_values'][chan] * 2)
                for i in range(0, granule['big_values'][chan] * 2, 2):
                    if self._bits.peek(1) == b'':
                        break
                    elif i >= len(self.frequency_lines[gran][chan]):
                        # if we have enough samples, then I think the rest of the bit
                        # are just stuffing
                        return
                    table_num = 0
                    if i < region_1_start:
                        table_num = granule['table_select'][chan][0]
                    elif i < region_2_start:
                        table_num = granule['table_select'][chan][1]
                    else:
                        table_num = granule['table_select'][chan][2]
                    if table_num == 0:
                        self.frequency_lines[gran][chan][i] = 0.0
                    x, y = decode_big_values(self._bits, table_num)
                    self.frequency_lines[gran][chan][i] = float(x)
                    self.frequency_lines[gran][chan][i+1] = float(y)

                # we're done with the big values regions
                # now, bring on the quadruples!
                table_num = granule['count1_table_select'][chan]
                # iterate until we're either out of bits or we have 576 samples
                for i in range(granule['big_values'][chan] * 2, 576, 4):
                    # If we're out of bits, break out!
                    if self._bits.peek(1) == b'':
                        break
                    v, w, x, y = decode_quadruples(self._bits, table_num)
                    self.frequency_lines[gran][chan][i] = float(v)
                    self.frequency_lines[gran][chan][i+1] = float(w)
                    self.frequency_lines[gran][chan][i+2] = float(x)
                    self.frequency_lines[gran][chan][i+3] = float(y)
                i += 1
                while i < 576:
                    self.frequency_lines[gran][chan][i] = 0
                    i += 1

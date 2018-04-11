"""
test_side_info.py : test decoding MP3 side information
"""

import sys
sys.path.append('../mp3po')

from mp3po.sideinfo import SideInfo
from mp3po.header import MP3Header, ChannelEncodings

def test_side_info_decoding():
    """
    test_side_info_decoding : test the initialization of the side info class
    """
    # header_str = b'\xff\xfb\xb0\x00'
    # header = MP3Header(header_str)
    with open('tests/02 - undercurrent.mp3', 'rb') as f:
        buf = f.read(2)
        while (buf[-2] != 255 or (buf[-1] & 0xF0 != 240 and buf[-1] & 0xE0 != 224)):
            buf += f.read(1)
        buf = buf[-2:]
        buf += f.read(2)
        header = MP3Header(buf)
        pos = f.tell()
        f.seek(pos + 2)
        side_info_len = 17
        if header.channel != ChannelEncodings.MONO:
            side_info_len = 32
        side_info_bytes = f.read(side_info_len)
        side_info = SideInfo(header, side_info_bytes)
        assert side_info.main_data_begin == 8
        assert side_info.private_bits == 0
        assert side_info.scfsi_band[0] == [0, 0, 0, 0,]
        assert side_info.scfsi_band[1] == [1, 0, 0, 0,]
        
        # validate granule 1
        granule_1 = side_info.granules[0]
        assert granule_1['part2_3_length'] == [1741, 1228,]
        assert granule_1['big_values'] == [60, 428,]
        assert granule_1['global_gain'] == [108, 132,]
        assert granule_1['scalefac_compress'] == [0, 8,]
        assert granule_1['window_switch_flag'] == [0, 0,]
        assert granule_1['table_select'] == [[0, 2, 16,], [0, 2, 19]]
        assert granule_1['region0_count'] == [6, 15,]
        assert granule_1['region1_count'] == [7, 2,]
        assert granule_1['preflag'] == [0, 0,]
        assert granule_1['scalefac_scale'] == [0, 1,]
        assert granule_1['count1_table_select'] == [0, 0,]

        #validate granule 2
        granule_2 = side_info.granules[1]
        assert granule_2['part2_3_length'] == [3021, 2767,]
        assert granule_2['big_values'] == [300, 62,]
        assert granule_2['global_gain'] == [222, 206,]
        assert granule_2['scalefac_compress'] == [0, 0,]
        assert granule_2['window_switch_flag'] == [0, 0,]
        assert granule_2['table_select'] == [[0, 0, 17,], [0, 2, 5]]
        assert granule_2['region0_count'] == [4, 0,]
        assert granule_2['region1_count'] == [4, 0,]
        assert granule_2['preflag'] == [0, 0,]
        assert granule_2['scalefac_scale'] == [1, 0,]
        assert granule_2['count1_table_select'] == [1, 0,]


def main():
    """
    main : run tests
    """
    test_side_info_decoding()

if __name__ == '__main__':
    main()

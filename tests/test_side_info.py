"""
test_side_info.py : test decoding MP3 side information
"""

import sys
sys.path.append('../mp3po')

from mp3po.sideinfo import SideInfo
from mp3po.header import MP3Header, ChannelEncodings

EXPECTED_RESULTS = [
    {
        'main_data_begin' : 8,
        'private_bits' : 0,
        'scfsi_band' : [[0, 0, 0, 0,], [1, 0, 0, 0,]],
        'granules' : [
            {
                'part2_3_length' : [1741, 1228,],
                'big_values' : [60, 428,],
                'global_gain' : [108, 132,],
                'scalefac_compress' : [0, 8,],
                'window_switch_flag' : [0, 0,],
                'table_select' : [[0, 2, 16,], [0, 2, 19]],
                'region0_count' : [6, 15,],
                'region1_count' : [7, 2,],
                'preflag' : [0, 0,],
                'scalefac_scale' : [0, 1,],
                'count1_table_select' : [0, 0,],
            },
            {
                'part2_3_length' : [3021, 2767,],
                'big_values' : [300, 62,],
                'global_gain' : [222, 206,],
                'scalefac_compress' : [0, 0,],
                'window_switch_flag' : [0, 0,],
                'table_select' : [[0, 0, 17,], [0, 2, 5]],
                'region0_count' : [4, 0,],
                'region1_count' : [4, 0,],
                'preflag' : [0, 0,],
                'scalefac_scale' : [1, 0,],
                'count1_table_select' : [1, 0,],
            }
        ]
    },
    {
        'main_data_begin' : 456,
        'private_bits' : 1,
        'scfsi_band' : [[0, 1, 0, 1,], [0, 0, 1, 0,],],
        'granules' : [
            {
                'part2_3_length' : [2763, 2764,],
                'big_values' : [302, 310,],
                'global_gain' : [222, 176,],
                'scalefac_compress' : [4, 12,],
                'window_switch_flag' : [0, 0,],
                'table_select' : [[0, 0, 16,], [27, 0, 15]],
                'region0_count' : [6, 10,],
                'region1_count' : [0, 4,],
                'preflag' : [0, 0,],
                'scalefac_scale' : [1, 1,],
                'count1_table_select' : [0, 0,],
            },
            {
                'part2_3_length' : [2380, 3149,],
                'big_values' : [38, 54,],
                'global_gain' : [178, 152,],
                'scalefac_compress' : [15, 2,],
                'window_switch_flag' : [0, 1,],
                'table_select' : [[19, 16, 15,], [8, 6, 0]],
                'region0_count' : [9, 8],
                'region1_count' : [6, 12],
                'preflag' : [0, 1,],
                'scalefac_scale' : [1, 0,],
                'count1_table_select' : [1, 1,],
                'sub_block_gain' : [[0, 0, 0], [4, 1, 6]],
                'block_type' : [0, 2],
                'mixed_block_flag' : [0, 0],
            }
        ]
    },
]

def test_side_info(side_info, wanted_results):
    """
    test_side_info : test the initialization of the side info class
    """
    assert side_info.main_data_begin == wanted_results['main_data_begin']
    assert side_info.private_bits == wanted_results['private_bits']
    assert side_info.scfsi_band == wanted_results['scfsi_band']

    # validate granule 1
    granule_1 = side_info.granules[0]
    granule_1_expected = wanted_results['granules'][0]
    for key in granule_1_expected:
        try:
            got_granule_values = granule_1.collect_channel_values(key)
            assert got_granule_values == granule_1_expected[key]
        except AssertionError as err:
            print('got: {}'.format(got_granule_values))
            print('want: {}'.format(granule_1_expected[key]))
            raise err

    #validate granule 2
    granule_2 = side_info.granules[1]
    granule_2_expected = wanted_results['granules'][1]
    for key in granule_2_expected:
        try:
            got_granule_values = granule_2.collect_channel_values(key)
            assert got_granule_values == granule_2_expected[key]
        except AssertionError as err:
            print('got: {}'.format(got_granule_values))
            print('want: {}'.format(granule_2_expected[key]))
            raise err


def main():
    """
    main : run tests
    """
    header_one_bytes = b'\xff\xfb\xb0\x00'
    header_one = MP3Header(header_one_bytes)
    side_info_one_bytes = b'\x04\x00\x86\xcd\x1e6\x00\x02\x83p\x99\x9a\xc8H\x00S\xf4\xaf6Y\xbc\x00\x02)\x1dg\x8f\xb3\x80\x01\x14\x00'
    side_info_one = SideInfo(header_one, side_info_one_bytes)
    test_side_info(side_info_one, EXPECTED_RESULTS[0])

    header_two_bytes = b'\xff\xfb\xb2\x00'
    header_two = MP3Header(header_two_bytes)
    side_info_two_bytes = b'\xe4\x15*\xcb\x97o \x00\x83\x05Y\x93k\x0cl\x0f\xa8\xa50Me\xe9\xc1\xf3\x9e&\x8d\xa6\x0b\x10hu'
    side_info_two = SideInfo(header_two, side_info_two_bytes)
    test_side_info(side_info_two, EXPECTED_RESULTS[1])


if __name__ == '__main__':
    main()

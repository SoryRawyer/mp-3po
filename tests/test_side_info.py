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
    f = open('tests/02 - undercurrent.mp3', 'rb')
    buf = f.read(2)
    while (buf[-2] != 255 or (buf[-1] & 0xF0 != 240 and buf[-1] & 0xE0 != 224)):
        buf += f.read(1)
    buf = buf[-2:]
    buf += f.read(2)
    h = MP3Header(buf)
    crc = f.read(2)
    side_info_len = 17
    if h.channel != ChannelEncodings.MONO:
        side_info_len = 32
    side_info_bytes = f.read(side_info_len)
    side_info = SideInfo(h, side_info_bytes)
    print(side_info)


def main():
    """
    main : run tests
    """
    test_side_info_decoding()

if __name__ == '__main__':
    main()

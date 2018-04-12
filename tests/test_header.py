"""
test_header.py : test decoding MP3 headers
"""

import sys
sys.path.append('../mp3po')

from mp3po.header import MP3Header, MPEGVersionEncodings, ChannelEncodings, LayerEncodings

def test_header_decoding():
    """
    test_header_decoding : test header decoding!
    """
    header_str = b'\xff\xfb\xb0\x00'
    header = MP3Header(header_str)
    assert int(header.sync_word, 2) == 2047
    assert header.mpeg_version == MPEGVersionEncodings.MPEG_V1
    assert header.layer == LayerEncodings.THREE
    assert header.error_protection == '1'
    assert header.bitrate == 192000
    assert header.frequency == 44100
    assert header.pad_bit == '0'
    assert header.priv_bit == '0'
    assert header.channel == ChannelEncodings.STEREO
    assert header.mode_extention == '00'
    assert header.copy == '0'
    assert header.original == '0'
    assert header.emphasis == '00'
    assert header.padding == 1
    assert int(header.frame_size) == 626

def main():
    """
    main : run tests
    """
    test_header_decoding()

if __name__ == '__main__':
    main()

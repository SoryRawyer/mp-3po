import sys
sys.path.append('../mp3po')

from mp3po.sideinfo import SideInfo
from mp3po.header import MP3Header, ChannelEncodings

def print_frame_information():
    frame_num = 1
    with open('tests/02 - undercurrent.mp3', 'rb') as f:
        buf = find_next_frame(f)
        # while len(buf) != 0:
        bytes_read = 0
        header = MP3Header(buf)
        bytes_read += 4
        if header.error_protection:
            f.read(2)
            bytes_read += 2
        side_info_len = 17
        if header.channel != ChannelEncodings.MONO:
            side_info_len = 32
        bytes_read += side_info_len
        side_info_bytes = f.read(side_info_len)
        side_info = SideInfo(header, side_info_bytes)
        print('frame number: {}\t main_data_begin: {}'.format(frame_num,
                                                              side_info.main_data_begin))
        print(side_info.granules)
        print(side_info.scfsi_band)
        frame_num += 1
        pos = f.tell()
        print(pos, header.frame_size)
        f.seek(pos + int(header.frame_size) - bytes_read)
        bytes_read = 0
        buf = find_next_frame(f)

def find_next_frame(f):
    buf = f.read(2)
    while (buf[-2] != 255 or (buf[-1] & 0xF0 != 240 and buf[-1] & 0xE0 != 224)):
        buf += f.read(1)
    buf = buf[-2:]
    buf += f.read(2)
    return buf

if __name__ == '__main__':
    print_frame_information()

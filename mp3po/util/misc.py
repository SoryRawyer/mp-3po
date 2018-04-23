import sys
sys.path.append('../mp3po')

from mp3po.sideinfo import SideInfo
from mp3po.header import MP3Header, ChannelEncodings
from mp3po.mp3 import MP3File

def print_frame_information():
    frame_num = 1
    with open('tests/02 - undercurrent.mp3', 'rb') as f:
        buf = find_next_frame(f)
        print(f.tell())
        return
        while len(buf) != 0:
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
            print('frame number: {}\t frame size: {}\t main_data_begin: {}'.format(frame_num,
                                                                header.frame_size,
                                                                side_info.main_data_begin))
            # print(side_info.granules)
            # print(side_info.scfsi_band)
            frame_num += 1
            pos = f.tell()
            # print(pos, header.frame_size)
            f.seek(pos + int(header.frame_size) - bytes_read)
            bytes_read = 0
            buf = find_next_frame(f)
            print(buf)

def find_next_frame(f):
    buf = f.read(2)
    while (buf[-2] != 255 or (buf[-1] & 0xF0 != 240 and buf[-1] & 0xE0 != 224)):
        char = f.read(1)
        # print('char: {}', char)
        if char == b'':
            print('(shrug)')
            sys.exit()
        buf += char
    buf = buf[-2:]
    buf += f.read(2)
    return buf

def try_mp3(filename):
    mp3file = MP3File(filename)
    frames = mp3file.read_frames(10)
    print(str(frames[0]))

if __name__ == '__main__':
    # print_frame_information()
    try_mp3('tests/02 - undercurrent.mp3')
    # try_mp3('/Users/rorysawyer/media/audio/toe/the book about my idle plot on a vague anxiety/music for you.mp3')

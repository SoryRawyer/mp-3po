"""
mp3.py : do mp3 things
"""

from .header import MP3Header, ChannelEncodings
from .sideinfo import SideInfo

class MP3File(object):
    """
    MP3File : look for frames and break them up into headers and data or whatever
    maybe include utilities for playing songs too

    support reading data chunks and getting other kinds of information as well

    The side information is 17 bytes for mono, 32 bytes otherwise.
    """

    def __init__(self, mp3_file):
        self.filename = mp3_file
        self.position = 0
        # open file, read data into header and data frame objects
        with open(mp3_file, 'rb') as audio:
            # read audio data into a buffer. stop once we've reached the first mp3 frame
            buf = audio.read(2)
            while not self._is_frame_start(buf[-2], buf[-1]):
                buf += audio.read(1)
            # should we save the start location of the mp3 data? Yesy
            self.position = audio.tell() - 2
        return

    def read_frames(self, nframes: int) -> (list, list):
        """
        read_frames
        return two equal-length arrays:
          - headers for the number of frames read
          - data of each frame
        """
        headers = []
        data = []
        if nframes == 0:
            return headers, data
        with open(self.filename, 'rb') as audio:
            still_reading = True
            audio.seek(self.position)
            while still_reading:
                buf = audio.read(4)
                header = MP3Header(buf)
                headers.append(header)
                if header.error_protection == '1':
                    # who cares about the 16-bit crc? let's get to the freakin MUSIC!
                    audio.read(2)
                if header.channel == ChannelEncodings.MONO:
                    # side info is 17 bytes!
                    side_info_bytes = audio.read(17)
                    side_info = SideInfo(header, side_info_bytes)
                else:
                    # side info is 32 bytes!
                    side_info_bytes = audio.read(32)
                    side_info = SideInfo(header, side_info_bytes)
                if audio.peek(1) == b'':
                    break
                frame = audio.read(1)
                while True:
                    new_byte = audio.peek(1)
                    if new_byte == b'':
                        still_reading = False
                        break
                    frame += audio.read(1)
                    if self._is_frame_start(frame[-2], frame[-1]):
                        # we've stumbled upon a new 
                        audio.seek(audio.tell() - 2)
                        frame = frame[:-2]
                        break
                data.append(frame)
            self.position = audio.tell()
        return headers, data
    
    def _is_frame_start(self, byte1, byte2):
        return (byte1 == 255 and (byte2 & 0xF0 != 240 or byte2 & 0xE0 != 224))

"""
mp3.py : do mp3 things
"""

from .header import MP3Header, ChannelEncodings
from .main_data import MainData
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
            # should we save the start location of the mp3 data? Yes
            self.position = audio.tell() - 2
        self.previous_frame_size = 0
        # keep a buffer of main data from previous frames. when we need to read main data
        # we will follow one of the following:
        #   - read all of the main data from the buffer
        #   - read the rest of the buffer, then some of the main data in the current physical frame
        #   - read the main data from immediately after the side information
        self.main_data_buffer = b''

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
                non_main_data_len = 4

                if header.error_protection == '1':
                    # who cares about the 16-bit crc? let's get to the freakin MUSIC!
                    audio.read(2)
                    non_main_data_len += 2

                side_info_length = 17
                if header.channel != ChannelEncodings.MONO:
                    side_info_length = 32
                side_info_bytes = audio.read(side_info_length)
                side_info = SideInfo(header, side_info_bytes)

                # read until the next header so we have all the main data we could possibly want
                while True:
                    new_byte = audio.peek(1)
                    if new_byte == b'':
                        still_reading = False
                        break
                    self.main_data_buffer += audio.read(1)
                    if self._is_frame_start(self.main_data_buffer[-2], self.main_data_buffer[-1]):
                        # we've stumbled upon a new frame. return the file back to the start
                        # of the header and remove the last two bytes from the main data buffer
                        audio.seek(audio.tell() - 2)
                        self.main_data_buffer = self.main_data_buffer[:-2]
                        break
                # At this point, we now have all the main data up until the start of the next frame

                # calculate the position at which to start reading the main data
                # then read the main data into a buffer and send that buffer somewhere
                # so that we might one day hope to know the scaling factors
                non_main_data_len += side_info_length
                main_data_length = header.frame_size - non_main_data_len
                main_data_bytes = self.main_data_buffer[:main_data_length]
                self.main_data_buffer = self.main_data_buffer[main_data_length:]
                main_data = MainData(header, side_info, main_data_bytes)
            self.position = audio.tell()
        return headers, data

    def _is_frame_start(self, byte1, byte2):
        return byte1 == 255 and (byte2 & 0xF0 != 240 or byte2 & 0xE0 != 224)

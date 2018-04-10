"""
utils.py : helpful things for mp3po
"""

class Bits(object):
    """
    utility for reading parts of bit strings
    """
    def __init__(self, bits=''):
        self._bits = bits
        self._position = 0

    def read(self, num_bits) -> str:
        """
        read : return the number of bits starting at the current position
        update the position in the object to the end of the string just read
        """
        if self._position >= len(self._bits):
            raise Exception('no more bits to read!')
        result = self._bits[self._position:self._position+num_bits]
        self._position += num_bits
        return result

    def read_bits_as_int(self, num_bits) -> int:
        """
        read_bits_as_int : read the number of bits requested and then return those in integer form
        the bits are interpreted as an unsigned integer
        """
        return int(self.read(num_bits), 2)

    def seek(self, position):
        """
        seek : change the position from which we start reading the bitstring
        """
        self._position = position

    def add_bits(self, num: int):
        """
        add_bits : take an integer and add those bits to the bitstring
        if len(bin(num)) is not a multiple of 8, pad it out to 8 bits
        """
        num_binary = bin(num).split('b')[1]
        pad_length = (8 - len(num_binary) % 8) if (8 - len(num_binary) % 8) != 8 else 0
        self._bits += (pad_length * '0') + num_binary

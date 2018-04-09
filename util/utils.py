"""
utils.py : helpful things for mp3po
"""

class Bits(object):
    """
    utility for reading parts of bit strings
    """
    def __init__(self, bits):
        self._bits = bits
        self._position = 0

    def read(self, num_bits):
        """
        read : return the number of bits starting at the current position
        update the position in the object to the end of the string just read
        """
        if self._position >= len(self._bits):
            raise Exception('no more bits to read!')
        result = self._bits[self._position:self._position+num_bits]
        self._position += num_bits
        return result

    def seek(self, position):
        """
        seek : change the position from which we start reading the bitstring
        """
        self._position = position

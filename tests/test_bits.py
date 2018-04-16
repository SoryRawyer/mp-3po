"""
test_bits.py : test the bits utility class
"""

import sys
sys.path.append('../mp3po')

from mp3po.util.bits import Bits

def test_read_first_bit():
    """
    test_read_first_bit : test that the first bit read is 0
    """
    test_bits = Bits(bin(123))
    assert test_bits.read(1) == '0'
    assert test_bits._position == 1

def main():
    """
    main : run tests
    """
    test_bits = Bits(bin(123))
    test_read_first_bit()

if __name__ == '__main__':
    main()

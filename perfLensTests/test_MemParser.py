from unittest import TestCase

from perfLens.parsers.MemParser import MemParser
from pathlib import Path

class TestMemParser(TestCase):
    test_path = Path(__file__).parent / "test_data"
    test_data = test_path / "host_mem.mem"

    def test_parse_mem(self):
        info = MemParser.get_mem_data(self.test_data)
        print(info)
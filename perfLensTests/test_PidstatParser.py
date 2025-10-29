from unittest import TestCase
from pathlib import Path
from perfLens.parsers.PidstatParser import PidstatParser

class TestPidstatParser(TestCase):
    test_path = Path(__file__).parent / "test_data"
    test_data = test_path / "pidstat.pstat"
    def test_parse_cpu_file(self):
        info = PidstatParser.get_pidstat_data_cpu(self.test_data)
        print(info)

    def test_parse(self):
        instance = PidstatParser(rundir=self.test_path)
        instance.parse()
        self.assertEqual(instance.avail_results(), ['pidstat.pstat'])
        result = instance.get_results("pidstat.pstat")
        self.assertEqual(len(result.columns), 10)


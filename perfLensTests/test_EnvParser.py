from unittest import TestCase

from perfLens.parsers.EnvParser import EnvParser
from perfLens.parserManager import ParserManager
from pathlib import Path

class TestEnvParser(TestCase):
    test_path = Path(__file__).parent / "test_data"
    test_data = test_path / "env.log"
    print("Available parsers:", ParserManager.available())

    def test_parse_file(self):
        print("Using env.log @", self.test_data)
        d = EnvParser._parse_env_data(self.test_data)
        self.assertEqual(d['nodes'], 8)
        self.assertEqual(d['mpi'], 110)
        self.assertEqual(d['omp'], 1)
        self.assertEqual(d['tasks'], 880)

    def test_integration(self):
        manager = ParserManager("envparser")
        manager.add_input(self.test_path)
        manager.list_results()
        manager.parse()
        r = manager.get_results("slurm_data")
        print(r)

    def test_integration_explore(self):

        manager = ParserManager("envparser")
        manager.explore(self.test_path)
        manager.list_results()
        manager.parse()
        r = manager.get_results("slurm_data")
        print(r)


import tempfile
import unittest
from pathlib import Path

import pandas as pd

from perfLens.parsers import PARSERS
from perfLens.parsers.env import EnvParser
from perfLens.parsers.jsonl import JsonlParser
from perfLens.parsers.mem import MemParser
from perfLens.parsers.pidstat import PidstatParser

DATA = Path(__file__).parent / "data"


class TestEnvParser(unittest.TestCase):
    def test_slurm_setup(self):
        self.assertEqual(EnvParser.slurm_setup(DATA / "env.log"),
                         {"nodes": 8, "mpi": 110, "omp": 1, "tasks": 880})

    def test_missing_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / "env.log"
            env.write_text("SLURM_NNODES=2\nOTHER=1\n")
            self.assertEqual(EnvParser.slurm_setup(env),
                             {"nodes": 2, "mpi": -1, "omp": -1, "tasks": -1})

    def test_parse(self):
        parser = EnvParser(DATA)
        self.assertEqual(parser.available(), ["slurm"])
        df = parser.parse()["slurm"]
        self.assertEqual(list(df.columns), ["nodes", "mpi", "omp", "tasks"])
        self.assertEqual(len(df), 1)


class TestMemParser(unittest.TestCase):
    def test_read_free(self):
        df = MemParser.read_free(DATA / "host_mem.mem")
        self.assertEqual(df.shape, (5, 9))
        first = df.iloc[0]
        self.assertEqual(first["host"], "host_mem")
        self.assertEqual(first["time"], 0)
        self.assertAlmostEqual(first["total"], 15.31)
        self.assertAlmostEqual(first["used"], 4.97)
        self.assertAlmostEqual(first["used_perc"], 32.46)
        self.assertEqual(list(df["time"]), [0, 1, 2, 3, 4])


class TestPidstatParser(unittest.TestCase):
    def test_read_pidstat(self):
        df = PidstatParser.read_pidstat(DATA / "pidstat.pstat")
        self.assertEqual(list(df.columns),
                         ["file", "time", "UID", "PID", "%usr", "%system",
                          "%guest", "%wait", "%CPU", "CPU", "Command"])
        self.assertEqual(len(df), 224)
        first = df.iloc[0]
        self.assertEqual(first["time"], "19:18:05")
        self.assertEqual(first["PID"], 16)
        self.assertAlmostEqual(first["%CPU"], 0.99)
        self.assertEqual(first["Command"], "rcu_preempt")

    def test_12h_clock_and_spaces_in_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            pstat = Path(tmp) / "run.pstat"
            pstat.write_text(
                "Linux 6.5.0 (host) \t07/14/24 \t_x86_64_\t(12 CPU)\n\n"
                "07:18:04 PM   UID       PID    %usr %system  %CPU   CPU  Command\n"
                "07:18:05 PM  1001      2482    0.98    0.98  1.96     6  Web Content\n"
                "\nAverage:     UID       PID    %usr %system  %CPU   CPU  Command\n"
                "Average:    1001      2482    0.98    0.98  1.96     -  Web Content\n")
            df = PidstatParser.read_pidstat(pstat)
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]["time"], "07:18:05 PM")
            self.assertEqual(df.iloc[0]["Command"], "Web Content")


class TestJsonlParser(unittest.TestCase):
    def test_read_jsonl(self):
        with self.assertLogs("perfLens", level="WARNING") as logs:
            df = JsonlParser.read_jsonl(DATA / "sample.jsonl")
        self.assertEqual(len(logs.output), 3)  # not json, not an object, truncated
        self.assertEqual(df.columns[0], "file")
        self.assertEqual(set(df.columns),
                         {"file", "step", "elapsed_s", "mem.rss_mb", "tags", "io"})
        self.assertEqual(df["step"].tolist(), [1, 2, 3])
        self.assertEqual(df["file"].unique().tolist(), ["sample.jsonl"])
        self.assertAlmostEqual(df["mem.rss_mb"].iloc[2], 810.5)
        self.assertTrue(pd.isna(df["mem.rss_mb"].iloc[1]))  # missing key
        self.assertEqual(df["tags"].iloc[0], ["a", "b"])

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty.jsonl"
            empty.write_text("\n")
            df = JsonlParser.read_jsonl(empty)
            self.assertEqual(len(df), 0)
            self.assertEqual(list(df.columns), ["file"])

    def test_parse(self):
        parser = JsonlParser(DATA)
        self.assertEqual(parser.available(), ["records"])
        self.assertEqual(len(parser.parse()["records"]), 3)


class TestRegistry(unittest.TestCase):
    def test_modes(self):
        self.assertEqual(sorted(PARSERS), ["env", "jsonl", "mem", "pidstat"])

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from perfLens import collect
from perfLens.cli import main
from perfLens.core import select

DATA = Path(__file__).parent / "data"


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(["-q"] + [str(a) for a in argv])
    return code, out.getvalue()


class TestCli(unittest.TestCase):
    def test_list(self):
        code, out = run("env", DATA, "--list")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), f"{DATA}: slurm")

    def test_show(self):
        code, out = run("env", DATA)
        self.assertEqual(code, 0)
        self.assertIn("# slurm", out)
        self.assertIn("880", out)

    def test_explore(self):
        code, out = run("mem", DATA.parent, "--explore", "--list")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), f"{DATA}: mem")

    def test_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = run("mem", DATA, "--cols", "host", "used",
                          "--sort", "used", "--desc", "--save", tmp)
            self.assertEqual(code, 0)
            df = pd.read_csv(str(Path(tmp) / "mem.csv"))
            self.assertEqual(list(df.columns), ["host", "used"])
            self.assertTrue(df["used"].is_monotonic_decreasing)

    def test_no_rundirs(self):
        code, _ = run("env", DATA / "missing")
        self.assertEqual(code, 1)


class TestApi(unittest.TestCase):
    def test_collect(self):
        results = collect("pidstat", [DATA])
        self.assertEqual(list(results), ["cpu"])
        self.assertEqual(results["cpu"]["rundir"].unique().tolist(), [str(DATA)])

    def test_select_unknown_columns(self):
        df = pd.DataFrame({"a": [2, 1], "b": [3, 4]})
        self.assertEqual(list(select(df, cols=["a", "x"]).columns), ["a"])
        self.assertEqual(select(df, sort=["a"])["a"].tolist(), [1, 2])

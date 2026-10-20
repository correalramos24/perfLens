import tempfile
import unittest
from pathlib import Path

from perfLens.utils import find_dirs, leading_int


class TestUtils(unittest.TestCase):
    def test_leading_int(self):
        self.assertEqual(leading_int("110(x8)"), 110)
        self.assertEqual(leading_int("8"), 8)
        self.assertEqual(leading_int("abc"), -1)
        self.assertEqual(leading_int(None), -1)
        self.assertEqual(leading_int("", default=0), 0)

    def test_find_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("a", "a/b", "c"):
                (root / d).mkdir()
            (root / "a" / "env.log").touch()
            (root / "a" / "b" / "x.mem").touch()
            (root / "c" / "other.txt").touch()
            self.assertEqual(find_dirs(root, ["env.log"]), [root / "a"])
            self.assertEqual(find_dirs(root, ["*.mem", "env.log"]),
                             [root / "a", root / "a" / "b"])
            self.assertEqual(find_dirs(root, ["*.pstat"]), [])

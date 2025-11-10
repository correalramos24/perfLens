from unittest import TestCase
from perfLens.parsers.NEMO import Nemo
from pathlib import Path


class TestAbstractNemo(TestCase):
    test_path = Path(__file__).parent / "test_data"
    test_nml = test_path / "test_namelist_cfg"

    def test_sim_secs(self):
        info = Nemo.sim_secs(self.test_nml)
        print(info)
        self.assertEqual(info, 5400)

    def test_timesteps(self):
        info = Nemo.exec_timesteps(self.test_path / "invalid_ts_file")
        print(info)
        info = Nemo.exec_timesteps(self.test_path / "time.step")
        print(info)
        info = Nemo.sim_timesteps(self.test_nml)
        print("Simulation ts", info)


    def test_get_nml_value(self):
        info = Nemo._nml_value(self.test_nml, "namdom", "rn_Dt")
        print(info)
        info = Nemo._nml_value(self.test_nml, "namdom2", "rn_Dt")
        print(info)
        info = Nemo._nml_value(self.test_nml, "namdom", "rn_Dtss")
        print(info)
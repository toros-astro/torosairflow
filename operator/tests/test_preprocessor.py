import unittest
import torosmanager
from torosmanager import preprocessor as p
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        from astropy.io import fits
        import numpy as np

        small_data = np.array([[0, 1], [1, 0]])
        self.outdir = os.path.join(BASE_DIR, "observation-2020-03-01")
        os.makedirs(self.outdir, exist_ok=True)
        ndarks = 3
        for index in range(ndarks):
            phdu = fits.PrimaryHDU(small_data)
            head = phdu.header
            head["EXPTIME"] = 60
            head["IMAGETYP"] = "DARK"
            head["FILTER"] = "i"
            fname = "dark_{:02d}.fits".format(index)
            phdu.writeto(os.path.join(self.outdir, fname), overwrite=True)

        nflats = 3
        for index in range(nflats):
            phdu = fits.PrimaryHDU(small_data)
            head = phdu.header
            head["EXPTIME"] = 60
            head["IMAGETYP"] = "FLAT"
            head["FILTER"] = "i"
            fname = "flat_{:02d}.fits".format(index)
            phdu.writeto(os.path.join(self.outdir, fname), overwrite=True)

        nlight = 3
        for index in range(nlight):
            phdu = fits.PrimaryHDU(small_data)
            head = phdu.header
            head["EXPTIME"] = 60
            head["IMAGETYP"] = "LIGHT"
            head["FILTER"] = "i"
            fname = "light_{:02d}.fits".format(index)
            phdu.writeto(os.path.join(self.outdir, fname), overwrite=True)

    def tearDown(self):
        fitsfiles = [
            os.path.join(self.outdir, f) for f in os.listdir(self.outdir) if ".fit" in f
        ]
        for afile in fitsfiles:
            os.remove(afile)
        os.rmdir(self.outdir)

    def test_load_night_bundle(self):
        p.load_night_bundle(self.outdir)


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""
Preprocessor Module

(c) TOROS Dev Team
"""
import logging
from pony import orm
from . import models
from .models import EXP_TYPE_CODES
from astropy.io import fits
import os


@orm.db_session
def load_night_bundle(url):
    from datetime import datetime

    logger = logging.getLogger("load_night_bundle")

    nb = models.NightBundle(
        telescope_night_bundle_id=1,
        datetime=datetime.now(),
        directory_path=os.path.abspath(url),
    )
    fits_files = [os.path.join(url, f) for f in os.listdir(url) if ".fit" in f]

    for afile in fits_files:
        hdulist = fits.open(afile)
        head = hdulist[0].header
        t = models.Exposure(
            night_bundle=nb,
            filename=os.path.basename(afile),
            exposure_type=EXP_TYPE_CODES[head["IMAGETYP"].upper()],
            naxis=head["NAXIS"],
            naxis1=head["NAXIS1"],
            naxis2=head["NAXIS2"],
            exptime=head["EXPTIME"],
        )
        hdulist.close()
        logger.debug(
            "Uploading {} to database".format(os.path.basename(afile))
        )


@orm.db_session
def make_dark_master():
    """for each group of (filter, exptime) do:
    stack all dark exposures
    save fits to file
    add entry in database for each file (stack) generated"""
    import ccdproc

    logger = logging.getLogger("make_dark_master")

    nb = models.NightBundle.get(telescope_night_bundle_id=1)
    nb_dir = nb.directory_path
    dark_list_q = nb.exposures.select(
        lambda d: d.exposure_type == models.EXP_TYPE_CODES["DARK"]
    )
    dark_list = [os.path.join(nb_dir, f.filename) for f in dark_list_q]
    logger.debug("List of dark files retrieved: {}".format(dark_list))

    # Create dark master and save to file
    logger.debug("Creating dark master")
    master_dark = ccdproc.combine(dark_list, method="median", unit="adu")
    dark_hdu = fits.PrimaryHDU(master_dark)
    dark_hdu.header["IMAGETYP"] = "DARKM"
    dark_hdu.header["EXPTIME"] = 60.0
    file_path = os.path.join(nb_dir, "products", "dark_master.fits")
    makedirs = os.path.dirname(file_path)
    if makedirs:
        os.makedirs(makedirs, exist_ok=True)
    dark_hdu.writeto(file_path)

    # Add entry to database
    logger.debug("Adding dark master info to database")
    dark_comb = models.ExposureCombination(
        night_bundle=nb,
        filename="dark_master.fits",
        combination_type=models.COMB_TYPE_CODES["DARKM"],
        exposures=dark_list_q,
    )


@orm.db_session
def make_flat_master():
    """for each filter do:
    stack all flat exposures
    save fits to file
    add entry in database for each file (stack) generated"""
    import ccdproc

    logger = logging.getLogger("make_flat_master")

    nb = models.NightBundle.get(telescope_night_bundle_id=1)
    nb_dir = nb.directory_path
    flat_list_q = nb.exposures.select(
        lambda d: d.exposure_type == models.EXP_TYPE_CODES["FLAT"]
    )
    flat_list = [os.path.join(nb_dir, f.filename) for f in flat_list_q]
    logger.debug("List of flat files retrieved: {}".format(flat_list))

    # Create dark master and save to file
    logger.debug("Creating flat master")
    master_flat = ccdproc.combine(flat_list, method="average", unit="adu")
    flat_hdu = fits.PrimaryHDU(master_flat)
    flat_hdu.header["IMAGETYP"] = "FLATM"
    flat_hdu.header["EXPTIME"] = 60.0
    file_path = os.path.join(nb_dir, "products", "flat_master.fits")
    makedirs = os.path.dirname(file_path)
    if makedirs:
        os.makedirs(makedirs, exist_ok=True)
    logger.debug("Writing flat master to file")
    flat_hdu.writeto(file_path)

    # Add entry to database
    logger.debug("Adding flat master info to database")
    flat_comb = models.ExposureCombination(
        night_bundle=nb,
        filename="flat_master.fits",
        combination_type=models.COMB_TYPE_CODES["FLATM"],
        exposures=flat_list_q,
    )


@orm.db_session
def make_flatdark_correction():
    """for each light exposure do:
    subtract dark from light
    divide by dark-subtracted flat
    save fits to file
    add entry in database for each calibrated file generated"""
    # Eventually should be done as described in:
    # https://ccdproc.readthedocs.io/en/latest/reduction_toolbox.html
    # Or here:
    # https://mwcraig.github.io/ccd-as-book
    import ccdproc
    from astropy.nddata import CCDData
    from astropy import units as u

    logger = logging.getLogger("make_flatdark_correction")
    nb = models.NightBundle.get(telescope_night_bundle_id=1)
    nb_dir = nb.directory_path
    light_list_q = nb.exposures.select(
        lambda d: d.exposure_type == models.EXP_TYPE_CODES["LIGHT"]
    )
    light_list = [os.path.join(nb_dir, f.filename) for f in light_list_q]

    master_dark_q = nb.combinations.select(
        lambda d: d.combination_type == models.COMB_TYPE_CODES["DARKM"]
    ).get()
    master_dark_path = os.path.join(nb_dir, "products", master_dark_q.filename)
    master_flat_q = nb.combinations.select(
        lambda d: d.combination_type == models.COMB_TYPE_CODES["FLATM"]
    ).get()
    master_flat_path = os.path.join(nb_dir, "products", master_flat_q.filename)

    # Reduce every light exposure individually
    master_dark = CCDData.read(master_dark_path, unit="adu")
    master_flat = CCDData.read(master_flat_path, unit="adu")
    reduced_dir = os.path.join(nb_dir, "products")
    os.makedirs(reduced_dir, exist_ok=True)
    logger.debug("Reducing each light frame...")
    for light_q, light_fname in zip(light_list_q, light_list):
        raw_data = CCDData.read(light_fname, unit="adu")
        # import astroscrappy
        # cr_cleaned = ccdproc.cosmicray_lacosmic(
        #     raw_data,
        #     satlevel=np.inf,
        #     sepmed=False,
        #     cleantype="medmask",
        #     fsmode="median",
        # )
        # crmask, cr_cleaned = astroscrappy.detect_cosmics(
        #     raw_data,
        #     inmask=None,
        #     satlevel=np.inf,
        #     sepmed=False,
        #     cleantype="medmask",
        #     fsmode="median",
        # )
        # cr_cleaned.unit = "adu"
        cr_cleaned = raw_data
        dark_subtracted = ccdproc.subtract_dark(
            cr_cleaned,
            master_dark,
            exposure_time="EXPTIME",
            exposure_unit=u.second,
            scale=True,
        )
        reduced_image = ccdproc.flat_correct(
            dark_subtracted, master_flat, min_value=0.9
        )
        reduced_filename = "calib_{}".format(os.path.basename(light_fname))
        reduced_path = os.path.join(makedirs, reduced_filename)

        reduced_image.write(reduced_path, overwrite=True)
        reduced_comb = models.ExposureCombination(
            night_bundle=nb,
            filename=reduced_filename,
            combination_type=models.COMB_TYPE_CODES["CALIB_LIGHT"],
            exposures=light_q,
            uses_combinations=[master_flat_q, master_dark_q],
        )

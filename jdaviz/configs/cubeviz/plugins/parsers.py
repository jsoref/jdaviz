from astropy.io import fits
from spectral_cube import SpectralCube
from spectral_cube.io.fits import FITSReadError
import logging
import numpy as np
import os
from jdaviz.core.registries import data_parser_registry
from specutils import Spectrum1D

EXT_TYPES = dict(flux=['flux', 'sci'],
                 uncert=['ivar', 'err', 'var', 'uncert'],
                 mask=['mask', 'dq'])


@data_parser_registry("cubeviz-data-parser")
def parse_data(app, file_obj, data_type=None, data_label=None):
    """
    Attempts to parse a data file and auto-populate available viewers in
    cubeviz.

    Parameters
    ----------
    app : `~jdaviz.app.Application`
        The application-level object used to reference the viewers.
    file_path : str
        The path to a cube-like data file.
    """
    if data_type is not None and data_type.lower() not in ['flux', 'mask', 'uncert']:
        msg = "Data type must be one of 'flux', 'mask', or 'uncertainty'."
        logging.error(msg)
        return msg

    if isinstance(file_obj, fits.hdu.hdulist.HDUList):
        _parse_hdu(app, file_obj)
    elif isinstance(file_obj, str) and os.path.exists(file_obj):
        file_name = os.path.basename(file_obj)

        with fits.open(file_obj) as hdulist:
            hdulist = fits.open(file_obj)
            _parse_hdu(app, hdulist, file_name)
    elif isinstance(file_obj, SpectralCube):
        _parse_spectral_cube(app, file_obj, data_type or 'flux', data_label)
    elif isinstance(file_obj, Spectrum1D):
        _parse_spectrum1d(app, file_obj)


def _parse_hdu(app, hdulist, file_name=None):
    if hasattr(hdulist, 'file_name'):
        file_name = hdulist.file_name

    file_name = file_name or "Unknown HDU object"

    wcs = None

    for hdu in hdulist:
        data_label = f"{file_name}[{hdu.name}]"

        if hdu.data is None:
            continue

        # This will fail on attempting to load anything that
        # isn't cube-shaped
        try:
            sc = SpectralCube.read(hdu)
            wcs = sc.wcs
        except ValueError:
            # This will fail if the parsing of the wcs does not provide
            # proper celestial axes
            try:
                hdu.header.update(wcs.to_header())
                sc = SpectralCube.read(hdu)
            except ValueError as e:
                logging.error(e)
                continue
        except FITSReadError as e:
            logging.error(e)
            continue

        app.data_collection[data_label] = sc

        # If the data type is some kind of integer, assume it's the mask/dq
        if hdu.data.dtype in (np.int, np.uint, np.uint32) or \
                any(x in hdu.name.lower() for x in EXT_TYPES['mask']):
            app.add_data_to_viewer('mask-viewer', data_label)

        if 'errtype' in [x.lower() for x in hdu.header.keys()] or \
                any(x in hdu.name.lower() for x in EXT_TYPES['uncert']):
            app.add_data_to_viewer('uncert-viewer', data_label)

        if any(x in hdu.name.lower() for x in EXT_TYPES['flux']):
            app.add_data_to_viewer('flux-viewer', data_label)
            app.add_data_to_viewer('spectrum-viewer', data_label)


def _parse_spectral_cube(app, file_obj, data_type='flux', data_label=None):
    data_label = data_label or f"Unknown spectral cube[{data_type.upper()}]"

    app.data_collection[f"{data_label}"] = file_obj

    if data_type == 'flux':
        app.add_data_to_viewer('flux-viewer', f"{data_label}")
        app.add_data_to_viewer('spectrum-viewer', f"{data_label}")
    elif data_type == 'mask':
        app.add_data_to_viewer('mask-viewer', f"{data_label}")
    elif data_type == 'uncert':
        app.add_data_to_viewer('uncert-viewer', f"{data_label}")

    # TODO: SpectralCube does not store mask information
    # TODO: SpectralCube does not store data quality information


def _parse_spectrum1d(app, file_obj):
    data_label = "Unknown spectrum object"

    # TODO: glue-astronomy translators only look at the flux property of
    #  specutils Spectrum1D objects. Fix to support uncertainties and masks.

    app.data_collection[f"{data_label}[FLUX]"] = file_obj
    app.add_data_to_viewer('spectrum-viewer', f"{data_label}[FLUX]")

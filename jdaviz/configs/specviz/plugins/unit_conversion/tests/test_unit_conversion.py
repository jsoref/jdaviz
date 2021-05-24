import numpy as np
from .. import unit_conversion as uc
from astropy.nddata import (VarianceUncertainty, StdDevUncertainty,
                            InverseVariance, UnknownUncertainty)


SPECTRUM_SIZE = 10  # length of spectrum

unit_exponents = {StdDevUncertainty: 1,
                  InverseVariance: -2,
                  VarianceUncertainty: 2}

RESULT_SPECTRAL_AXIS = [0.6, 0.62222222, 0.64444444, 0.66666667,
                        0.68888889, 0.71111111, 0.73333333,
                        0.75555556, 0.77777778, 0.8]

RESULT_FLUX = [1.04067240e-07, 9.52912307e-08, 9.77144651e-08,
               1.00212528e-07, 8.55573341e-08, 8.29285448e-08,
               9.05651431e-08, 8.33870526e-08, 7.47628902e-08,
               7.74896053e-08]

RESULT_UNCERTAINTY = [3.85914248e-09, 3.60631495e-09, 1.74661581e-09,
                      1.29057072e-08, 1.08965936e-08, 3.33352891e-09,
                      5.64618219e-09, 1.65028707e-09, 4.49994292e-09,
                      6.61559372e-09]


def test_value_error_spec_axis_exception(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "fail"
    new_flux = "erg / (s cm2 um)"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux,
                                   new_spectral_axis=new_spectral_axis)

    assert converted_spectrum is None


def test_value_error_flux_exception(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "None"
    new_flux = "fail"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux,
                                   new_spectral_axis=new_spectral_axis)

    assert converted_spectrum is None


def test_spec_axis_value_error_flux_exception(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"
    new_flux = "fail"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux,
                                   new_spectral_axis=new_spectral_axis)

    assert converted_spectrum is None


def test_no_spec_no_flux_no_uncert(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    spectrum1d.uncertainty = None

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d)

    assert converted_spectrum.flux.unit == spectrum1d.flux.unit
    assert converted_spectrum.spectral_axis.unit == spectrum1d.spectral_axis.unit
    assert converted_spectrum.uncertainty is None


def test_spec_no_flux_no_uncert(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"

    spectrum1d.uncertainty = None

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_spectral_axis=new_spectral_axis)

    assert np.allclose(converted_spectrum.spectral_axis.value,
                       RESULT_SPECTRAL_AXIS, atol=1e-5)
    assert converted_spectrum.flux.unit == spectrum1d.flux.unit
    assert converted_spectrum.spectral_axis.unit == new_spectral_axis
    assert converted_spectrum.uncertainty is None


def test_no_spec_no_flux_uncert(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d)

    assert converted_spectrum.flux.unit == spectrum1d.flux.unit
    assert np.allclose(converted_spectrum.uncertainty.quantity,
                       spectrum1d.uncertainty.quantity, atol=1e-5)


def test_no_spec_no_flux_uncert_unit_exp_none(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    spectrum1d.uncertainty = UnknownUncertainty(np.abs(
        np.random.randn(len(spectrum1d.spectral_axis.value))))

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d)

    assert converted_spectrum.flux.unit == spectrum1d.flux.unit
    assert converted_spectrum.spectral_axis.unit == spectrum1d.spectral_axis.unit
    assert converted_spectrum.uncertainty is None


def test_no_spec_flux_no_uncert(specviz_app, spectrum1d):
    np.random.seed(42)
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    spectrum1d.uncertainty = None
    new_flux = "erg / (s cm2 um)"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux)

    assert np.allclose(converted_spectrum.flux.value,
                       RESULT_FLUX, atol=1e-5)
    assert converted_spectrum.spectral_axis.unit == spectrum1d.spectral_axis.unit
    assert converted_spectrum.uncertainty is None


def test_no_spec_flux_unit_exp_not_none(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_flux = "erg / (s cm2 um)"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux)

    assert np.allclose(converted_spectrum.flux.value,
                       RESULT_FLUX, atol=1e-5)
    assert np.allclose(converted_spectrum.uncertainty.quantity.value,
                       RESULT_UNCERTAINTY, atol=1e-5)


def test_spec_flux_no_uncert(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"
    new_flux = "erg / (s cm2 um)"

    spectrum1d.uncertainty = None

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux,
                                   new_spectral_axis=new_spectral_axis)

    assert np.allclose(converted_spectrum.flux.value,
                       RESULT_FLUX, atol=1e-5)
    assert np.allclose(converted_spectrum.spectral_axis.value,
                       RESULT_SPECTRAL_AXIS, atol=1e-5)
    assert converted_spectrum.uncertainty is None


def test_spec_no_flux_uncert_no_unit_exp(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"

    spectrum1d.uncertainty = UnknownUncertainty(np.abs(
        np.random.randn(len(spectrum1d.spectral_axis.value))))

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_spectral_axis=new_spectral_axis)

    assert converted_spectrum.flux.unit == spectrum1d.flux.unit
    assert np.allclose(converted_spectrum.spectral_axis.value,
                       RESULT_SPECTRAL_AXIS, atol=1e-5)
    assert converted_spectrum.uncertainty is None


def test_no_spec_flux_uncert_no_unit_exp(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_flux = "erg / (s cm2 um)"

    spectrum1d.uncertainty = UnknownUncertainty(np.abs(
        np.random.randn(len(spectrum1d.spectral_axis.value))))

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux)

    assert converted_spectrum.spectral_axis.unit == spectrum1d.spectral_axis.unit
    assert np.allclose(converted_spectrum.flux.value,
                       RESULT_FLUX, atol=1e-5)
    assert converted_spectrum.uncertainty is None


def test_spec_no_flux_uncert_unit_exp(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_spectral_axis=new_spectral_axis)

    assert np.allclose(converted_spectrum.spectral_axis.value,
                       RESULT_SPECTRAL_AXIS, atol=1e-5)
    assert np.allclose(converted_spectrum.uncertainty.quantity,
                       spectrum1d.uncertainty.quantity, atol=1e-5)


def test_spec_flux_uncert_no_unit_exp(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"
    new_flux = "erg / (s cm2 um)"

    spectrum1d.uncertainty = UnknownUncertainty(np.abs(
        np.random.randn(len(spectrum1d.spectral_axis.value))))

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux,
                                   new_spectral_axis=new_spectral_axis)

    assert np.allclose(converted_spectrum.spectral_axis.value,
                       RESULT_SPECTRAL_AXIS, atol=1e-5)
    assert np.allclose(converted_spectrum.flux.value,
                       RESULT_FLUX, atol=1e-5)
    assert converted_spectrum.uncertainty is None


def test_spec_flux_uncert_unit_exp(specviz_app, spectrum1d):
    label = "Test 1D Spectrum"
    specviz_app.load_spectrum(spectrum1d, data_label=label)

    new_spectral_axis = "micron"
    new_flux = "erg / (s cm2 um)"

    conv_func = uc.UnitConversion.process_unit_conversion
    converted_spectrum = conv_func(specviz_app.app, spectrum=spectrum1d,
                                   new_flux=new_flux,
                                   new_spectral_axis=new_spectral_axis)

    assert np.allclose(converted_spectrum.spectral_axis.value,
                       RESULT_SPECTRAL_AXIS, atol=1e-5)
    assert np.allclose(converted_spectrum.flux.value,
                       RESULT_FLUX, atol=1e-5)
    assert np.allclose(converted_spectrum.uncertainty.quantity.value,
                       RESULT_UNCERTAINTY, atol=1e-5)

import re

import pytest
import pkg_resources
from contextlib import contextmanager
from pint import UnitRegistry
from gemd.units import parse_units, convert_units, get_base_units, change_definitions_file, \
    UndefinedUnitError, DefinitionSyntaxError


@pytest.mark.parametrize("return_unit", [True, False])
def test_parse_expected(return_unit):
    """Test that we can parse the units that we expect to be able to."""
    # Pint's parse_units actually gets this wrong
    assert parse_units("m^-1 * newton / meter", return_unit=return_unit) == \
           parse_units("N / m^2", return_unit=return_unit)

    expected = [
        "degC", "degF", "K",
        "g", "kg", "mg", "ton",
        "L", "mL",
        "inch", "ft", "mm", "um",
        "second", "ms", "hour", "minute", "ns",
        "g/cm^3", "g/mL", "kg/cm^3",
        "", "1",
        "amu",  # A line that was edited
        "Seconds",  # Added support for some title-case units
        "delta_Celsius / hour",  # Added to make sure pint version is right (>0.10)
        "g / 2.5 cm",  # Scaling factors are acceptable
        "g / -+-25e-1 m",  # Weird but fine
        "ug / - -250 mL",  # Spaces between unaries is acceptable
        "1 / 10**5 degC"  # Spaces between unaries is acceptable
    ]
    for unit in expected:
        parsed = parse_units(unit, return_unit=return_unit)
        assert parsed == parse_units(parsed, return_unit=return_unit)
    assert parse_units("") == 'dimensionless'
    # Scaling factors bind tightly to trailing units
    assert parse_units("g / 2.5 cm", return_unit=return_unit) == \
           parse_units("g / (2.5 cm)", return_unit=return_unit)
    assert parse_units("g / 2.5cm", return_unit=return_unit) == \
           parse_units("g / (2.5 cm)", return_unit=return_unit)
    assert parse_units("g / 25.mm", return_unit=return_unit) == \
           parse_units("g / (25. mm)", return_unit=return_unit)
    assert parse_units("g / 2.5 * cm", return_unit=return_unit) == \
           parse_units("g cm / 2.5", return_unit=return_unit)


def test_parse_unexpected():
    """Test that we cannot parse the units that we do not expect to."""
    unexpected = [
        "gibberish",
        5,
        "cp",  # Removed because of risk of collision with cP
        "chain",  # Survey units eliminated
        "SECONDS",  # Not just case insensitivity
        "lb : in^3",  # : is not a valid operator
    ]
    for unit in unexpected:
        with pytest.raises(UndefinedUnitError):
            parse_units(unit)

    scaling = [
        "3 rpm",  # No leading digits
        "16",  # No values that are just integers
        "16.2"  # No values that are just floats
        "g * 0/ m",  # Zero scaling factor
        "F * 1.1 3.5",  # numeric syntax error
        "F m 1.1",  # scale follows unit
        "F * 1.1 ** 2",  # numeric syntax error
    ]
    for unit in scaling:
        with pytest.raises(ValueError, match=r"[sS]caling"):
            parse_units(unit)

    definition = [
        "/gram",  # A leading operator makes no sense
        "m ** - 1"  # Pint parse doesn't accept spaces between negative & numeral / unit
    ]
    for unit in definition:
        with pytest.raises(DefinitionSyntaxError):
            parse_units(unit)

    zero_division = [
        "g / 0 m",  # Division by zero
    ]
    for unit in zero_division:
        with pytest.raises(ZeroDivisionError):
            parse_units(unit)


def test_parse_none():
    """Test that None parses as None."""
    assert parse_units(None) is None
    assert parse_units(None, return_unit=True) == parse_units("", return_unit=True)


def test_parse_units_as_units():
    """Test that Units in == Units out."""
    from gemd.units.impl import _REGISTRY

    expected = [
        _REGISTRY("kg").u,
    ]
    for unit in expected:
        parsed = parse_units(unit)
        assert parsed == parse_units(parsed)


def test_format():
    """Test that custom formatting behaves as we hope."""
    # use the default unit registry for now
    reg = UnitRegistry(filename=pkg_resources.resource_filename("gemd.units", "citrine_en.txt"))

    result = parse_units("K^-2.0 m^-1e0 C^0 g^1 s^2")
    assert "-" not in result
    assert "[time]" in reg(result).dimensionality
    assert "[current]" not in reg(result).dimensionality
    kelvin = str(reg("K").units)
    gram = str(reg("g").units)
    second = str(reg("s").units)
    assert kelvin in result
    assert gram in result
    assert second in result
    assert result.index(gram) < result.index(kelvin)
    assert result.index(gram) < result.index(second)

    assert not re.search(r"\d", parse_units("m kg / s"))
    assert "/" not in parse_units("m kg s")
    assert "1" not in parse_units("s")
    assert "1" in parse_units("s^-1")
    assert "2.5" in parse_units("g / 2.5 cm")


def test_conversion():
    """Tests that check if particular units are interoperable."""
    conversions = {"in_lb": "foot_pound"}
    for source, dest in conversions.items():
        assert convert_units(convert_units(1, source, dest), dest, source) == 1

    # Verify that convert_units respects scaling factors
    assert -1e-8 < convert_units(100, 'g / 100 mL', 'g/cc') - 1 < 1e-8
    assert -1e-8 < convert_units(1, "g / 2.5 cm", "g / 25 mm") - 1 < 1e-8


def test_get_base_units():
    """Test that base units & conversions make sense."""
    from gemd.units.impl import _REGISTRY
    assert get_base_units("degC") == (_REGISTRY("kelvin"), 1, 273.15)
    assert get_base_units("degC") == get_base_units(_REGISTRY("degC"))
    assert get_base_units("km") == (_REGISTRY("meter"), 1000, 0)
    assert get_base_units("g / 25 mm") == (_REGISTRY("kg / m"), 0.04, 0)


@contextmanager
def _change_units(filename):
    try:
        change_definitions_file(filename)
        yield
    finally:
        change_definitions_file()


def test_file_change():
    """Test that swapping units files works."""
    assert convert_units(1, 'm', 'cm') == 100
    with pytest.raises(UndefinedUnitError):
        assert convert_units(1, 'usd', 'USD') == 1
    with _change_units(filename=pkg_resources.resource_filename("tests.units",
                                                                "test_units.txt")):
        with pytest.raises(UndefinedUnitError):
            assert convert_units(1, 'm', 'cm') == 100
        assert convert_units(1, 'usd', 'USD') == 1
    assert convert_units(1, 'm', 'cm') == 100  # And verify we're back to normal
    with pytest.raises(UndefinedUnitError):
        parse_units('mol : mol')  # Ensure the preprocessor is still there


def test_punctuation():
    """Test that punctuation parses reasonably."""
    assert parse_units('mol.') == parse_units('moles')
    assert parse_units('N.m') == parse_units('N * m')
    with pytest.raises(UndefinedUnitError):
        parse_units('mol : mol')


def test_exponents():
    """SPT-874 fractional exponents were being treated as zero."""
    megapascals = parse_units("MPa")
    sqrt_megapascals = parse_units('MPa^0.5')
    assert megapascals in sqrt_megapascals
    assert sqrt_megapascals == parse_units(f"{megapascals} / {sqrt_megapascals}")
    assert parse_units('MPa^1.5') == parse_units(f"{megapascals} * {sqrt_megapascals}")


def test__scientific_notation_preprocessor():
    """Verify that numbers are converted into scientific notation."""
    assert "1e2 kg" in parse_units("F* 10 ** 2 kg")
    assert "1e-5" in parse_units("F* mm*10**-5")
    assert "1e" not in parse_units("F* kg * 10 cm")
    assert "-3.07e2" in parse_units("F* -3.07 * 10 ** 2")
    assert "11e2" in parse_units("F* 11*10^2")

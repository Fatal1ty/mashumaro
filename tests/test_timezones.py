from dataclasses import dataclass
from datetime import timedelta, timezone

import pytest

from mashumaro import DataClassDictMixin

time_zones = [
    (timezone(timedelta(hours=-12)), "UTC-12:00"),  # Baker Island
    (timezone(timedelta(hours=-11)), "UTC-11:00"),  # American Samoa
    (timezone(timedelta(hours=-10)), "UTC-10:00"),  # Hawaii
    (
        timezone(timedelta(hours=-9, minutes=-30)),
        "UTC-09:30",
    ),  # Marquesas Isl.
    (timezone(timedelta(hours=-9)), "UTC-09:00"),  # Gambier Isl.
    (timezone(timedelta(hours=-8)), "UTC-08:00"),  # Pitcairn Isl.
    (timezone(timedelta(hours=-7)), "UTC-07:00"),  # Sonora
    (timezone(timedelta(hours=-6)), "UTC-06:00"),  # Costa Rica
    (timezone(timedelta(hours=-5)), "UTC-05:00"),  # Colombia
    (timezone(timedelta(hours=-4)), "UTC-04:00"),  # Bolivia
    (timezone(timedelta(hours=-3, minutes=-30)), "UTC-03:30"),  # Canada
    (timezone(timedelta(hours=-3)), "UTC-03:00"),  # Argentina
    (timezone(timedelta(hours=-2)), "UTC-02:00"),  # South Georgia
    (timezone(timedelta(hours=-1)), "UTC-01:00"),  # Cape Verde
    (timezone(timedelta(hours=0)), "UTC"),  # Burkina Faso
    (timezone(timedelta(hours=1)), "UTC+01:00"),  # Algeria
    (timezone(timedelta(hours=2)), "UTC+02:00"),  # Botswana
    (timezone(timedelta(hours=3)), "UTC+03:00"),  # Moscow
    (timezone(timedelta(hours=3, minutes=30)), "UTC+03:30"),  # Iran
    (timezone(timedelta(hours=4)), "UTC+04:00"),  # Armenia
    (timezone(timedelta(hours=4, minutes=30)), "UTC+04:30"),  # Afghanistan
    (timezone(timedelta(hours=5)), "UTC+05:00"),  # Maldives
    (timezone(timedelta(hours=5, minutes=30)), "UTC+05:30"),  # India
    (timezone(timedelta(hours=5, minutes=45)), "UTC+05:45"),  # Nepal
    (timezone(timedelta(hours=6)), "UTC+06:00"),  # Bangladesh
    (timezone(timedelta(hours=6, minutes=30)), "UTC+06:30"),  # Myanmar
    (timezone(timedelta(hours=7)), "UTC+07:00"),  # Cambodia
    (timezone(timedelta(hours=8)), "UTC+08:00"),  # Hong Kong
    (timezone(timedelta(hours=8, minutes=45)), "UTC+08:45"),  # Eucla
    (timezone(timedelta(hours=9)), "UTC+09:00"),  # Japan
    (timezone(timedelta(hours=9, minutes=30)), "UTC+09:30"),  # N. Australia
    (timezone(timedelta(hours=10)), "UTC+10:00"),  # Queensland
    (timezone(timedelta(hours=10, minutes=30)), "UTC+10:30"),  # Australia
    (timezone(timedelta(hours=11)), "UTC+11:00"),  # Vanuatu
    (timezone(timedelta(hours=12)), "UTC+12:00"),  # Nauru
    (timezone(timedelta(hours=12, minutes=45)), "UTC+12:45"),  # New Zealand
    (timezone(timedelta(hours=13)), "UTC+13:00"),  # Tonga
    (timezone(timedelta(hours=14)), "UTC+14:00"),  # Kiribati
]


@pytest.mark.parametrize(["tz", "tz_string"], time_zones)
def test_timezones(tz, tz_string):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: timezone

    assert DataClass(tz).to_dict() == {"x": tz_string}
    assert DataClass.from_dict({"x": tz_string}) == DataClass(tz)


def test_invalid_timezone():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: timezone

    with pytest.raises(ValueError):
        DataClass.from_dict({"x": "UTC+03:00:01"})

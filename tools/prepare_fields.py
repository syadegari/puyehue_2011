"""Build solver inputs in classic NetCDF from the packaged sources. SPDX-License-Identifier: MIT"""
from datetime import date, timedelta
import json
from pathlib import Path

import h5py
import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "case.json").read_text())
START = date.fromisoformat(CASE["start_utc"][:10])
END = date.fromisoformat(CASE["end_utc"][:10])


def axis(out, name, values, units):
    out.createDimension(name, len(values))
    var = out.createVariable(name, "d", (name,))
    var.units = units
    var[:] = values


def weather():
    days = [START + timedelta(days=i) for i in range((END - START).days + 1)]
    with netcdf_file(ROOT / "weather/transport.nc", "w") as out:
        out.source = "ECMWF ERA-Interim, unpacked from the four supplied MPTRAC test files"
        out.license = "CC BY 4.0; see SOURCES.md"
        axis(out, "time", np.arange(len(days)) * 24, f"hours since {START} 00:00:00")
        for i, day in enumerate(days):
            path = ROOT / "weather" / day.strftime("ei_%Y_%m_%d_00.nc")
            with h5py.File(path) as src:
                assert src["time"][0] == int(day.strftime("%Y%m%d"))
                for name, source, units in (("pressure", "plev", "Pa"), ("latitude", "lat", "degrees_north"),
                                            ("longitude", "lon", "degrees_east")):
                    if i == 0:
                        axis(out, name, src[source][:], units)
                    else:
                        np.testing.assert_array_equal(out.variables[name][:], src[source][:])
                for name, source, units in (("u", "U", "m s-1"), ("v", "V", "m s-1"),
                                            ("omega", "W", "Pa s-1"), ("temperature", "T", "K"),
                                            ("surface_pressure", "SP", "Pa")):
                    field = src[source]
                    raw = field[0]
                    if i == 0:
                        dims = ("time", "latitude", "longitude")
                        if raw.ndim == 3:
                            dims = ("time", "pressure", "latitude", "longitude")
                        var = out.createVariable(name, "f", dims)
                        var.units = units
                        var._FillValue = np.float32(np.nan)
                    data = raw.astype(np.float32)
                    data[raw == field.attrs["_FillValue"]] = np.nan
                    data = data * field.attrs["scale_factor"] + field.attrs["add_offset"]
                    out.variables[name][i] = data


def observations():
    grid = CASE["output_grid"]
    days = [START + timedelta(days=i) for i in range((END - START).days)]
    with netcdf_file(ROOT / "observations/aerosol_index.nc", "w") as out:
        out.source = "ESA Aerosol CCI, KNMI, GOME-2A L3 AAI v1.9; native-grid regional subset"
        out.license = "ESA CCI Data Policy; see SOURCES.md"
        axis(out, "day", range(len(days)), f"days since {START} 00:00:00")
        for i, day in enumerate(days):
            path = ROOT / "observations/source" / f"ESACCI-AEROSOL-L3-AAI-GOME2A-1D-{day:%Y%m%d}-fv1.9.nc"
            with h5py.File(path) as src:
                lon, lat = src["longitude"][:], src["latitude"][:]
                x = (grid["west_deg"] <= lon) & (lon < grid["east_deg"])
                y = (grid["south_deg"] <= lat) & (lat < grid["north_deg"])
                if i == 0:
                    axis(out, "longitude", lon[x], "degrees_east")
                    axis(out, "latitude", lat[y], "degrees_north")
                for name, dtype, units in (("absorbing_aerosol_index", "f", "1"),
                                           ("number_of_observations", "i", "1"),
                                           ("solar_zenith_angle", "f", "degrees")):
                    if i == 0:
                        var = out.createVariable(name, dtype, ("day", "latitude", "longitude"))
                        var.units = units
                        if dtype == "f":
                            var._FillValue = np.float32(np.nan)
                    out.variables[name][i] = src[name][:][np.ix_(x, y)].T


if __name__ == "__main__":
    weather()
    observations()

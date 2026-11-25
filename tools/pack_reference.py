"""Pack MPTRAC hourly grid and daily parcel tables. SPDX-License-Identifier: MIT"""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]


def pack(run, case_path, output):
    case = json.loads(case_path.read_text())
    grid = case["output_grid"]
    start = datetime.fromisoformat(case["start_utc"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(case["end_utc"].replace("Z", "+00:00"))
    stop = int((end - start).total_seconds())
    epoch = datetime.fromisoformat("2000-01-01T00:00:00+00:00")
    start_s = (start - epoch).total_seconds()
    count = case["release"]["particles"]
    nx, ny = grid["longitude_cells"], grid["latitude_cells"]
    for kind, cadence, filename in (("grid", case["grid_interval_seconds"], "hourly_grid.nc"),
                                    ("atm", case["particle_output_interval_seconds"], "daily_particles.nc")):
        seconds = list(range(0, stop + 1, cadence))
        with netcdf_file(output / filename, "w") as out:
            out.source = "MPTRAC CPU reference on the packaged initial ensemble; see README.md and SOURCES.md"
            out.createDimension("time", len(seconds))
            clock = out.createVariable("time", "i", ("time",))
            clock.units = "seconds since 2011-06-05 00:00:00 UTC"
            clock[:] = seconds
            if kind == "grid":
                for name, size, lo, hi, unit in (("longitude", nx, "west_deg", "east_deg", "degrees_east"),
                                                  ("latitude", ny, "south_deg", "north_deg", "degrees_north")):
                    out.createDimension(name, size)
                    coord = out.createVariable(name, "d", (name,))
                    coord.units = unit
                    edges = np.linspace(grid[lo], grid[hi], size + 1)
                    coord[:] = (edges[:-1] + edges[1:]) / 2
                area = out.createVariable("cell_area", "f", ("latitude", "longitude"))
                area.units = "km2"
                columns = (("column_mass", 6, "f", "kg m-2"), ("particle_count", 8, "i", "1"))
                dims = ("time", "latitude", "longitude")
            else:
                out.createDimension("id", count)
                out.createVariable("id", "i", ("id",))[:] = np.arange(count)
                columns = (("z", 1, "d", "km"), ("longitude", 2, "d", "degrees_east"),
                           ("latitude", 3, "d", "degrees_north"), ("mass", 12, "d", "kg"))
                dims = ("time", "id")
            for name, _, dtype, unit in columns:
                out.createVariable(name, dtype, dims).units = unit
            for i, dt in enumerate(seconds):
                at = start + timedelta(seconds=dt)
                data = np.loadtxt(run / f"{kind}_{at:%Y_%m_%d_%H_%M_%S}.tab")
                np.testing.assert_array_equal(data[:, 0], start_s + dt)
                if kind == "grid":
                    data = data.reshape(nx, ny, -1).transpose(1, 0, 2)
                    np.testing.assert_array_equal(data[0, :, 2], out.variables["longitude"][:])
                    np.testing.assert_array_equal(data[:, 0, 3], out.variables["latitude"][:])
                    if i == 0:
                        area[:] = data[..., 4]
                else:
                    assert len(data) == count
                for name, col, _, _ in columns:
                    out.variables[name][i] = data[..., col]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--case", type=Path, default=ROOT / "case.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reference")
    args = parser.parse_args()
    pack(args.run_directory, args.case, args.output)

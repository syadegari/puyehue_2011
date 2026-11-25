"""Check both releases, mass budgets, time axes and observation coverage. SPDX-License-Identifier: MIT"""
import csv
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]


def verify_run(config, initial, reference):
    release = config["release"]
    count, mass = release["particles"], release["total_mass_kg"]
    rows = np.loadtxt(initial, delimiter=",", skiprows=1)
    assert rows.shape == (count, 6) and np.isfinite(rows).all()
    np.testing.assert_array_equal(rows[:, 0], np.arange(count))
    np.testing.assert_array_equal(rows[:, 5], mass / count)
    np.testing.assert_allclose(rows[:, 4], release["surface_reference_hpa"] *
                               np.exp(-rows[:, 3] / release["scale_height_km"]), rtol=1e-9)
    with netcdf_file(reference / "daily_particles.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["time"][:], np.arange(4) * 86400)
        np.testing.assert_array_equal(v["id"][:], rows[:, 0])
        for name, column in (("longitude", 1), ("latitude", 2), ("z", 3)):
            assert np.isfinite(v[name][:]).all()
            # The source ASCII tables print six significant figures.
            np.testing.assert_allclose(v[name][0], rows[:, column], rtol=5e-6)
        np.testing.assert_array_equal(v["mass"][:].sum(axis=1), np.full(4, mass))
    with netcdf_file(reference / "hourly_grid.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["time"][:], np.arange(73) * 3600)
        expected, _ = np.histogramdd(rows[:, [2, 1]], bins=(
            np.arange(-65, -14.9, .5), np.arange(-90, 60.1, .5)))
        np.testing.assert_array_equal(v["particle_count"][0], expected)
        counts = v["particle_count"][:]
        assert (counts >= 0).all()
        np.testing.assert_array_equal(counts.sum(axis=(1, 2)), np.full(73, count))
        kg = v["column_mass"][:].astype(float) * v["cell_area"][:] * 1e6
        assert np.isfinite(kg).all() and (kg >= 0).all()
        np.testing.assert_allclose(kg, counts * (mass / count), rtol=1e-5, atol=1e-8)
        error = np.abs(kg.sum(axis=(1, 2)) - mass).max()
        print(f"{count:,} parcels, 73 grids, 4 snapshots. Largest gridded mass error: {error:,.0f} kg.")


def verify():
    verify_run(json.loads((ROOT / "case.json").read_text()), ROOT / "initial/particles.csv", ROOT / "reference")
    verify_run(json.loads((ROOT / "small/case.json").read_text()), ROOT / "small/particles.csv", ROOT / "small")
    with netcdf_file(ROOT / "weather/transport.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["time"][:], [0, 24, 48, 72])
        np.testing.assert_array_equal(v["longitude"][:], np.arange(0, 360, 3))
        np.testing.assert_array_equal(v["latitude"][:], np.arange(-90, 91, 3))
        assert len(v["pressure"][:]) == 59 and (np.diff(v["pressure"][:]) < 0).all()
        for name in ("u", "v", "omega", "temperature"):
            assert v[name].shape == (4, 59, 61, 120)
            assert np.isfinite(v[name][:, 32, 16:18, 95:98]).all()
    with netcdf_file(ROOT / "observations/aerosol_index.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["day"][:], [0, 1, 2])
        valid = np.isfinite(v["absorbing_aerosol_index"][:])
        np.testing.assert_array_equal(valid, v["number_of_observations"][:] > 0)
        print("GOME-2A valid 1-degree cells per day:", valid.sum(axis=(1, 2)).tolist(), "of 7,500.")
    with netcdf_file(ROOT / "observations/seviri_visible_ash.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["time"][:], [15, 39, 63])
        fraction = v["visible_ash_fraction"][:]
        assert fraction.shape == (3, 100, 300)
        assert np.nanmin(fraction) == 0 and np.nanmax(fraction) == 1
        outside = ((v["longitude"][:] < -75) | (v["longitude"][:] > -15))
        assert np.isnan(fraction[:, :, outside]).all()
        np.testing.assert_array_equal((fraction > 0).sum(axis=(1, 2)), [401, 876, 525])
    with (ROOT / "observations/seviri_centres.csv").open() as f:
        assert [int(row["model_hour"]) for row in csv.DictReader(f)] == [15, 39, 63]


if __name__ == "__main__":
    verify()

"""Generate the Puyehue release with Python's standard library. SPDX-License-Identifier: MIT"""
import argparse
import csv
import json
import math
import random
from pathlib import Path

CASE = Path(__file__).resolve().parents[1]


def generate(config, output):
    release = config["release"]
    rng = random.Random(release["seed"])
    fwhm_to_sigma = 1 / math.sqrt(8 * math.log(2))
    horizontal_sigma = release["horizontal_fwhm_km"] * fwhm_to_sigma
    vertical_sigma = release["vertical_fwhm_km"] * fwhm_to_sigma
    lat0 = release["latitude_deg"]
    km_per_degree = math.radians(1) * release["earth_radius_km"]
    km_per_degree_lon = km_per_degree * math.cos(math.radians(lat0))
    height = release["scale_height_km"]
    surface = release["surface_reference_hpa"]
    centre_pressure = surface * math.exp(-release["pressure_altitude_km"] / height)
    count = release["particles"]
    mass = release["total_mass_kg"] / count
    with output.open("w", newline="") as stream:
        rows = csv.writer(stream, lineterminator="\n")
        rows.writerow(["id", "lon_deg", "lat_deg", "z_km", "p_hpa", "mass_kg"])
        for particle_id in range(count):
            lon = release["longitude_deg"] + rng.gauss(0, horizontal_sigma) / km_per_degree_lon
            lat = lat0 + rng.gauss(0, horizontal_sigma) / km_per_degree
            pressure = centre_pressure * (1 - rng.gauss(0, vertical_sigma) / height)
            z = -height * math.log(pressure / surface)
            rows.writerow([particle_id, f"{lon:.9f}", f"{lat:.9f}", f"{z:.9f}",
                           f"{pressure:.9f}", f"{mass:.10g}"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CASE / "initial/particles.csv")
    parser.add_argument("--case", type=Path, default=CASE / "case.json")
    args = parser.parse_args()
    generate(json.loads(args.case.read_text()), args.output)

"""Prepare optional MPTRAC inputs for regenerating the benchmark. SPDX-License-Identifier: MIT"""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare(repo, run, case_path, particles):
    cfg = json.loads(case_path.read_text())
    epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
    def model_seconds(key):
        return int((datetime.fromisoformat(cfg[key].replace("Z", "+00:00")) - epoch).total_seconds())

    if run.parent != repo / "projects":
        raise ValueError("Use a new directory directly under the MPTRAC projects directory for its ancillary paths.")
    run.mkdir(mode=0o700)
    grid = cfg["output_grid"]
    controls = {"NQ": 9}
    for i, name in enumerate(("t", "u", "v", "w", "zg", "pv", "ps", "pt", "m")):
        controls[f"QNT_NAME[{i}]"] = name
    controls.update({"METBASE": ROOT / "weather/ei", "DT_MET": 86400, "DIFFUSION": 1,
                     "ATM_BASENAME": "atm", "GRID_BASENAME": "grid", "GRID_LON0": grid["west_deg"],
                     "GRID_LON1": grid["east_deg"], "GRID_LAT0": grid["south_deg"],
                     "GRID_LAT1": grid["north_deg"], "GRID_NX": grid["longitude_cells"],
                     "GRID_NY": grid["latitude_cells"], "GRID_Z0": grid["bottom_km"],
                     "GRID_Z1": grid["top_km"], "T_STOP": model_seconds("end_utc"),
                     "DT_MOD": cfg["step_seconds"], "GRID_DT_OUT": cfg["grid_interval_seconds"],
                     "ATM_DT_OUT": cfg["particle_output_interval_seconds"]})
    (run / "trac.ctl").write_text("".join(f"{key} = {val}\n" for key, val in controls.items()))
    (run / "dirlist").write_text(".\n")
    initial_time = model_seconds("start_utc")
    with particles.open() as source, (run / "release.tab").open("w") as target:
        for row in csv.DictReader(source):
            print(initial_time, row["z_km"], row["lon_deg"], row["lat_deg"], *([0] * 8),
                  row["mass_kg"], file=target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mptrac_checkout", type=Path)
    parser.add_argument("new_run_directory", type=Path)
    parser.add_argument("--case", type=Path, default=ROOT / "case.json")
    parser.add_argument("--particles", type=Path, default=ROOT / "initial/particles.csv")
    args = parser.parse_args()
    prepare(args.mptrac_checkout.resolve(), args.new_run_directory.resolve(), args.case, args.particles)

"""Plot reference column mass at the three satellite comparison times. SPDX-License-Identifier: MIT"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]


def plot():
    with (ROOT / "observations/seviri_centres.csv").open() as stream:
        centres = list(csv.DictReader(stream))
    with netcdf_file(ROOT / "reference/hourly_grid.nc", mmap=False) as data:
        v = data.variables
        lon, lat = v["longitude"][:], v["latitude"][:]
        mass = v["column_mass"][[int(row["model_hour"]) for row in centres]] * 1000
    with netcdf_file(ROOT / "observations/seviri_visible_ash.nc", mmap=False) as data:
        footprint = data.variables["visible_ash_fraction"][:].copy()
    fig, axes = plt.subplots(3, 2, figsize=(12, 8.1), sharex=True, sharey=True)
    fig.subplots_adjust(left=.08, right=.975, top=.85, bottom=.22, hspace=.33, wspace=.10)
    fig.suptitle("Ash from Puyehue across the South Atlantic", x=.08, y=.98, ha="left", fontsize=21)
    fig.text(.08, .912, "Modelled column mass", fontsize=14, weight="bold")
    fig.text(.55, .912, "Observed ash footprint", fontsize=14, weight="bold")
    for i, (row, grid) in enumerate(zip(centres, mass)):
        model, sat = axes[i]
        model.set_facecolor("#f0f3f4")
        img = model.pcolormesh(lon, lat, np.ma.masked_less_equal(grid, 0), cmap="magma_r",
                               norm=LogNorm(.001, 10), shading="nearest")
        sat.set_facecolor("#d7dee2")
        obs = sat.pcolormesh(lon, lat, np.ma.masked_invalid(footprint[i]), cmap="YlGnBu",
                             vmin=0, vmax=1, shading="nearest")
        sat.scatter(float(row["longitude_deg"]), float(row["latitude_deg"]), marker="x",
                    color="#b13e13", s=58, lw=2, zorder=4)
        for ax in (model, sat):
            ax.scatter(-72.117, -40.59, marker="^", facecolor="white", edgecolor="#1d2632", s=32, zorder=3)
            ax.set(xlim=(-85, 25), ylim=(-58, -17))
            ax.set_yticks([-55, -45, -35, -25])
            ax.set_xticks([-75, -55, -35, -15, 5, 25])
        model.set_ylabel("Latitude (°)")
        model.set_title(f"June {int(row['time_utc'][8:10])}, 15:00 UTC   ·   hour {row['model_hour']}",
                        loc="left", fontsize=10)
    for ax in axes[-1]:
        ax.set_xlabel("Longitude (° east)")
    for artist, x, title in ((img, .10, "Column mass (g/m²)"), (obs, .57, "Fraction of figure pixels showing ash")):
        cb = fig.colorbar(artist, cax=fig.add_axes([x, .115, .35, .015]), orientation="horizontal")
        cb.set_label(title, fontsize=9)
    fig.text(.08, .031, "Triangle: release site.  Cross: observed ash centre.  Grey on satellite panels: unavailable.",
             fontsize=9)
    fig.text(.08, .008, "100,000-parcel run using ECMWF ERA-Interim. Satellite panels digitized from Prata et al. (2021), Fig. 1.",
             fontsize=9)
    fig.savefig(ROOT / "reference/comparison.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plot()

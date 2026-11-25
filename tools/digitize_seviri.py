"""Digitize the visible ash footprint and marked centres in Prata et al. (2021), Fig. 1. SPDX-License-Identifier: MIT"""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]


def extract():
    image = np.asarray(Image.open(ROOT / "observations/seviri_figure1.png").convert("RGB"))
    if image.shape != (2159, 2058, 3):
        raise ValueError("Digitizer is calibrated to the supplied 2058 by 2159 publisher image.")
    # Each window encloses the blue X in a single left-hand (satellite) panel.
    windows = [(225, 275, 282, 322), (365, 411, 805, 849), (365, 411, 1345, 1389)]
    panel_tops = [64.5, 616.5, 1167.5]
    # Positions of the labelled parallels, read locally in the first panel.
    tick_offset = np.array([108.5, 156.5, 208.5, 262.5, 321.5, 384.5]) - panel_tops[0]
    start = datetime(2011, 6, 5, 15, tzinfo=timezone.utc)
    # Map frame and labelled tick centres of the published observation panel.
    parallels = [-20, -25, -30, -35, -40, -45, -50, -55]
    y_offsets = np.r_[0, tick_offset, 394]
    fractions = np.full((3, 100, 300), np.nan, dtype=np.float32)
    for i, panel_top in enumerate(panel_tops):
        y, x = np.mgrid[int(panel_top + 2):int(panel_top + 394), 94:563]
        r, g, b = image[y, x].astype(np.int16).transpose(2, 0, 1)
        # Coastlines/background are grey, annotations blue or pure red.
        # This selects plotted warm-colour ash pixels, including dark reds.
        coloured = (r > g - 3) & (r - b >= 15) & (r - np.minimum(g, b) >= 30)
        longitude = np.interp(x, [92.5, 563.5], [-75, -15])
        latitude = np.interp(y - panel_top, y_offsets, parallels)
        usable = ~((abs(longitude + 72.117) < 1.15) & (abs(latitude + 40.59) < 1.1))
        # Exclude blue overlays and neutral dark borders/coastlines from the denominator.
        usable &= ~((b > r + 10) | ((r < 225) & (r == g) & (g == b)))
        grid_x = np.floor((longitude[usable] + 90) * 2).astype(int)
        grid_y = np.floor((latitude[usable] + 65) * 2).astype(int)
        index = grid_y * 300 + grid_x
        sampled = np.bincount(index, minlength=30000)
        ash = np.bincount(index, weights=coloured[usable], minlength=30000)
        np.divide(ash, sampled, where=sampled > 0, out=fractions[i].reshape(-1))
    with netcdf_file(ROOT / "observations/seviri_visible_ash.nc", "w") as out:
        out.source = "Digitized from Prata et al. (2021) Figure 1, left panels a-c, CC BY 4.0"
        for name, values, units in (("time", [15, 39, 63], "hours since 2011-06-05 00:00:00"),
                                    ("latitude", np.arange(-64.75, -15, .5), "degrees_north"),
                                    ("longitude", np.arange(-89.75, 60, .5), "degrees_east")):
            out.createDimension(name, len(values))
            var = out.createVariable(name, "f", (name,))
            var.units = units
            var[:] = values
        var = out.createVariable("visible_ash_fraction", "f", ("time", "latitude", "longitude"))
        var.units = "1"
        var.long_name = "Fraction of usable figure pixels coloured as ash in each cell"
        var._FillValue = np.float32(np.nan)
        var[:] = fractions
    with (ROOT / "observations/seviri_centres.csv").open("w", newline="") as stream:
        rows = csv.writer(stream, lineterminator="\n")
        rows.writerow(["time_utc", "model_hour", "longitude_deg", "latitude_deg"])
        for i, (left, right, top, bottom) in enumerate(windows):
            r, g, b = image[top:bottom, left:right].transpose(2, 0, 1)
            yy, xx = np.nonzero((b > 175) & (r < 70) & (g < 150))
            x = left + (xx.min() + xx.max()) / 2
            y = top + (yy.min() + yy.max()) / 2
            lon = np.interp(x, [92.5, 563.5], [-75, -15])
            lat = np.interp(y - panel_tops[i], tick_offset, [-25, -30, -35, -40, -45, -50])
            stamp = (start + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            rows.writerow([stamp, 15 + 24 * i, f"{lon:.1f}", f"{lat:.1f}"])


if __name__ == "__main__":
    extract()

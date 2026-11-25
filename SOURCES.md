# Sources and reuse

| Packaged material | Origin and changes | Reuse terms |
|---|---|---|
| `weather/ei_*.nc`, `weather/transport.nc` | ECMWF ERA-Interim. Four existing daily files taken byte-for-byte from MPTRAC’s `tests/data/` at checkout `053522e0c4c3df51ae4a12f99beba12032a7a903`. The supplied test files record earlier model-level to pressure-level conversion, bilinear regridding to 3°, packing and compression. The starter decodes and combines five fields for the transport file. | ECMWF publishes ERA-Interim under **CC BY 4.0**. Retain the credit, licence, disclaimer and processing history below. |
| `case.json`, `small/case.json` and both initial `particles.csv` files | Newly generated idealized releases. Source location, nominal pressure altitude, bulk mass and spread follow the numeric scenario in the MPTRAC Puyehue example. Both release tables use a documented fixed seed. | **CC0 1.0** for the configuration and generated initial-condition tables. |
| `observations/source/*.nc`, `observations/aerosol_index.nc` | ESA Aerosol Climate Change Initiative (CCI), KNMI and EUMETSAT AC SAF. Metop-A/GOME-2 daily Level 3 Absorbing Aerosol Index v1.9, based on GOME-2A AAI v1.35. Three unmodified global source files and a geographically cropped, transposed subset with sampling counts. | **ESA CCI Data Policy** as declared in each source file. Use for any purpose. Acknowledge ESA CCI, Aerosol CCI and the individual provider in publications or presentations and cite the relevant dataset DOI when available. |
| `observations/seviri_figure1.png`, `observations/seviri_centres.csv`, `observations/seviri_visible_ash.nc` | © Prata, Mingari, Folch, Macedonio and Costa (2021). Figure 1, downloaded from the publisher unchanged. We digitized the three in-window footprints and mass-centre markers from its SEVIRI observational panels. | The **published figure is CC BY 4.0**. Preserve author credit, citation and notice of digitization. This grant covers the figure and adaptations of it. |
| `tools/*.py`, starter documentation | New preparation, conversion and verification code and accompanying original text. | **MIT**. Third-party data and quoted notices retain the terms above. |

## ECMWF notice

Copyright © 2011 European Centre for Medium-Range Weather Forecasts (ECMWF). Meteorological analyses for 2011. Source: www.ecmwf.int. This data is published under a Creative Commons Attribution 4.0 International (CC BY 4.0). https://creativecommons.org/licenses/by/4.0/

ECMWF does not accept any liability whatsoever for any error or omission in the data, their availability, or for any loss or damage arising from their use.

The packed weather source files record the earlier conversions in their global `history` attributes. The combined weather file uses pascals, metres and seconds. For a service based on this data, retain the service wording in the supplied product terms. [ECMWF product terms](https://cds.climate.copernicus.eu/licences/reanalysis-era-interim) · [ERA-Interim archive access](https://confluence.ecmwf.int/spaces/CKB/pages/85419044/How+to+download+ERA-Interim+data+from+the+ECMWF+data+archive) · [Offline product terms](licenses/ERA-Interim-terms.pdf)

## Satellite sources

The three original GOME-2A files bear the instrument name, acquisition date, product version, processing history, institution and licence. KNMI lists Tilstra, Tuinder and Stammes (2010), *GOME-2 Absorbing Aerosol Index: Statistical analysis, comparison to GOME-1 and impact of instrument degradation*, as the scientific product reference. File downloads for this case are [5 June](https://d1qb6yzwaaq4he.cloudfront.net/airpollution/absaai/GOME2A/daily/data/2011/ESACCI-AEROSOL-L3-AAI-GOME2A-1D-20110605-fv1.9.nc), [6 June](https://d1qb6yzwaaq4he.cloudfront.net/airpollution/absaai/GOME2A/daily/data/2011/ESACCI-AEROSOL-L3-AAI-GOME2A-1D-20110606-fv1.9.nc) and [7 June](https://d1qb6yzwaaq4he.cloudfront.net/airpollution/absaai/GOME2A/daily/data/2011/ESACCI-AEROSOL-L3-AAI-GOME2A-1D-20110607-fv1.9.nc). [KNMI product and download calendar](https://temis.pmc.knmi.cloud/airpollution/absaai/index.php) · [ESA dataset terms](https://climate.esa.int/en/terms-and-conditions/) · [Offline data policy](licenses/ESA-CCI-policy.pdf)

Prata, A. T., Mingari, L., Folch, A., Macedonio, G., and Costa, A. (2021). *FALL3D-8.0: a computational model for atmospheric transport and deposition of particles, aerosols and radionuclides – Part 2: Model validation*. Geoscientific Model Development 14, 409–436. Figure 1 shows Meteosat-9/SEVIRI retrieved fine ash mass in the left column. The authors identify the separately distributed FALL3D test suite as GPLv3. We used the journal figure as the sole source for the digitized footprints and centres. [Article and licence](https://doi.org/10.5194/gmd-14-409-2021) · [Original figure](https://gmd.copernicus.org/articles/14/409/2021/gmd-14-409-2021-f01-web.png)

## Software and licences

The starter scripts and tables can be used in an independently written solver. The original Puyehue example supplied the scenario parameters and the four packed weather inputs. [MPTRAC project](https://github.com/slcs-jsc/mptrac) · [MIT licence](licenses/MIT.txt) · [CC0 dedication](licenses/CC0-1.0.txt) · [CC BY 4.0 legal text](licenses/CC-BY-4.0.txt)

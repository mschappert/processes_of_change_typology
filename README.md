# Characterizing Landscape-Level Processes of Change

This repository contains the code accompanying the paper describing a modified
process-of-change framework for characterizing landscape-level habitat dynamics.

## Table of contents

- [Overview](#overview)
- [Process of change framework](#process-of-change-framework)
  - [Typology of process of change](#typology-of-process-of-change)
  - [Spatial implementation](#spatial-implementation)
- [Case study: Atlantic Forest](#case-study-atlantic-forest)
  - [Landscape metrics](#landscape-metrics)
  - [Quantification based on time intervals](#quantification-based-on-time-intervals)
  - [Quantification based on time series](#quantification-based-on-time-series)
- [Repository structure](#repository-structure)
- [The data folder](#the-data-folder)
  - [Adding your data](#adding-your-data)
- [Two parallel workflows](#two-parallel-workflows)
- [Environment setup (ipynb workflow)](#environment-setup-ipynb-workflow)
- [References](#references)

## Overview

In this work we present a modification of the method proposed by Bogaert et al.
(2004) that enables the characterization of landscape-level processes of change.
The method supports **discrete time-point characterization** of processes of
change, as well as a **continuous characterization through time**, allowing the
assessment of both abrupt transitions and long-term landscape dynamics.

The approach is demonstrated through a case study in the Atlantic Forest of
Brazil, where we characterize the spatial and temporal variability of forest
change processes over a 31-year period (1990–2020). Given the Atlantic Forest's
long history of disturbance, habitat loss, fragmentation, and more recent
restoration and conservation efforts, it provides an ideal system for examining
how landscape change processes vary across space and time.

This study advances previous work in three key ways:

1. It extends process-of-change classification from individual patches to
   continuous landscapes through a moving-window approach.
2. It integrates both time-interval and time-series analyses, enabling the
   detection of abrupt changes as well as the characterization of long-term
   landscape dynamics.
3. It refines and expands existing process-of-change typologies to better
   distinguish changes in habitat *amount* from changes in habitat
   *configuration*.

## Process of change framework

### Typology of process of change

Bogaert et al. (2004) introduced a classification of spatial processes of
habitat loss and gain that lead to different landscape configurations. Their
work and its applications (e.g., Barima et al. 2016; Torres Mallma and Torres
Mallma 2024) characterize the process of change at the study-area level.
However, larger regions such as the Atlantic Forest may experience
geographically different processes of change, and a landscape definition can be
much smaller than a study area.

Our framework expands on the previous typologies by adding **persistence
(stable)** and **fragmentation per se** (Fahrig et al. 2019) in addition to
those defined by Bogaert et al. (2004). Landscapes are classified based on the
combination of increases, decreases, or stability in patch number (N), area
(A), and perimeter (P), yielding ten distinct processes of change grouped into
four categories:

**Increase in habitat amount**

- **Aggregation** — decrease in patch number, stable or increasing area;
  previously separate patches merge into larger connected ones.
- **Creation** — increase in patch number and area due to new habitat patches.
- **Enlargement** — stable patch number, increasing area as existing patches
  expand.

**Decrease in habitat amount**

- **Attrition** — decrease in both patch number and area due to complete loss
  of patches.
- **Dissection** — increase in patch number, decrease in area as habitat is
  subdivided into smaller units.
- **Perforation** — stable patch number, decreasing area, increasing perimeter
  from internal holes forming within patches.
- **Shrinkage** — stable patch number, decreasing area and perimeter as patches
  contract.

**Configurational change (no change in total habitat amount)**

- **Deformation** — stable patch number and area, changing perimeter reflecting
  shape change.
- **Fragmentation per se** (Fahrig et al. 2019) — increase in patch number with
  total area constant; subdivision without net habitat loss.

**Persistent habitat**

- **Persistence** — patch number, area, and perimeter remain unchanged; loss of
  a patch in one location may be offset by an equivalent patch elsewhere.

### Spatial implementation

The framework is implemented using a **moving-window** approach in which the
window size corresponds to the landscape extent of interest. Within each window,
area, perimeter, and the number of patches are calculated and the computed value
is assigned to the central cell. The output image is then used to classify the
dominant process of landscape change. The moving window is preferred over
pre-defined, non-overlapping landscape units because it allows continuous
spatial coverage and facilitates post hoc integration with biodiversity data or
other measurements.

The change process can be computed between two discrete time points or across a
continuous time series:

- **Time interval (discrete).** Changes in area, perimeter, and patch number are
  calculated as the difference between consecutive observations (T1 − T0).
  Positive values indicate an increase, negative values a decrease, and zero
  indicates stability. The direction of change for each metric classifies the
  landscape into one of the ten processes of change.
- **Time series (continuous).** Area, perimeter, and patch number are calculated
  for each time step within the moving window, and temporal trends are assessed
  using the Mann-Kendall trend test. Mann-Kendall Tau values (−1 to 1) are
  standardized into z-scores to express trend strength relative to the
  distribution of trends across the study area. A z-score threshold defines
  increasing, decreasing, or stable trends; lower thresholds detect subtler
  changes, higher thresholds restrict classification to stronger trends. Results
  depend on the chosen threshold, which should reflect the desired balance
  between sensitivity to change and robustness to noise, and should be selected
  based on study objectives.

The output is one image per time period, or one image per time series assessed,
showing the dominant process of change within the pre-defined moving-window
landscapes.

## Case study: Atlantic Forest

### Landscape metrics

The aim of the case study was to assess the process of change affecting **core
forest areas**. Morphological Spatial Pattern Analysis (MSPA) was run using
GuidosToolbox Workbench (GWB) v1.9.8 (Vogt et al. 2022) to extract core forests
and their edges. MSPA classifies the landscape into background, edge, core,
connectors (bridges and loops), islands, branches, and islets based on the
spatial arrangement of a focal land cover relative to a uniform class (Soille and
Vogt 2009, 2022).

Metric definitions used here:

- **Core forest area** — pixels in MSPA classes *core*, *perforation*, and
  *edge* (excluding bridges, loops, islands, branches, and islets).
- **Perimeter** — pixels in *edge* and *perforation* classes combined.
- **Number of patches** — derived from forest area using an eight-neighbor
  connected-regions rule.

By restricting analysis to core forest areas and their edge zones, the method
characterizes core forest change rather than overall net forest change.
Reductions in core forest can therefore occur even when forest cover remains
present, since degradation can convert core into non-core MSPA classes without a
corresponding loss in total forest area (Laurance et al. 2002). The framework is
flexible to use all forest patches or alternative MSPA class combinations.

Area, perimeter, and number of patches were calculated using a moving-window
analysis in ArcGIS Pro v3.5 (Esri 2025). The landscape was defined as a circle
with a 1 km radius (33 cells), a scale at which Atlantic Forest studies have
shown significant biological responses (Rocha-Santos et al. 2017; Manzoli et al.
2023; Adorno et al. 2021).

### Quantification based on time intervals

Processes of change in core forests were identified using 5-year time intervals
from 1990 to 2020 (e.g., 1990–1995, 1995–2000). For each interval, changes in
area, perimeter, and number of patches were calculated at the pixel level using
image differencing. A pixel was classified as an increase (T1 − T0 > 0), a
decrease (< 0), or stable (= 0).

### Quantification based on time series

A time-series analysis of area, perimeter, and number of patches identified
general trends across the 31-year period (1990–2020) using the Mann-Kendall Tau
trend test. Tau values were converted to z-scores, classifying areas as changing
(increasing or decreasing) only where trends were above (𝓏 ≥ +0.5) or below
(𝓏 ≤ −0.5) one standard deviation from the mean, and as stable otherwise
(−0.5 < 𝓏 < +0.5). The objective of the threshold was not to identify
statistically significant trends but to distinguish dominant directions of
landscape change. The temporal analysis was performed in TerrSet IDRISI/liberaGIS
v20.03 (Eastman 2024).

## Repository structure

```
code/
  arcpy_workflow/   ArcGIS Pro / ArcPy implementation (see folder README)
  ipynb_workflow/   Open-source Python / Jupyter implementation (see folder README)
data/               Input and intermediate rasters (see "The data folder" below)
notes/              Working notes
Dockerfile          Reproducible environment for the ipynb workflow
environment.yml     Conda environment specification (typology_env)
```

## The `data/` folder

The pipeline is organized as a series of numbered stages. You supply the raw
input at the start; **most of the folder structure is created automatically** by
the scripts as they run (each step calls `os.makedirs(..., exist_ok=True)` for
its own outputs).

```
data/
  1_<raw land cover>/     (you add this)  annual land-cover rasters, one per year
  2_MSPA/                 (MSPA step)     GWB MSPA pattern-class rasters
  3_MovingWindow/         (auto) reclassified MSPA + moving-window metric outputs
    MSPA_rc_area/  MSPA_rc_edge/  rg/  rg_rc/
    mw_area/       mw_edge/       mw_pn/    per-year 1 km metric rasters
  4_TS_and_TI/            (auto) time-interval and time-series analysis
    img_diff/<metric>/    time-interval differences (T1 - T0)
    TS/                   Mann-Kendall Tau rasters per metric
    TS_mask/              validity masks
    TS_zscore/<metric>/   z-score standardized Tau (<metric>_MK_tau_z.tif)
  5_Typology/             (auto) remap, combine, and final process-of-change maps
    remap_timeseries/     remap_interval/
    combined_timeseries/  combined_interval/
    combined_rc_*/        reclassified + labeled typology rasters
```

Metric names used throughout are `area`, `edge` (perimeter), and `pn` (patch
number).

### Adding your data

Only the first stages are manual; everything downstream is generated by the
scripts and keyed off file names (each file should contain a 4-digit year).

1. **Set the workspace root.** Each script has a `main_workspace` (ArcPy) or an
   equivalent input/output path near the top. Point it at your `data/` folder
   (e.g. `main_workspace = r"...\typology\data"`).
2. **Add raw annual land-cover rasters.** Place one raster per year in your input
   folder. Scripts extract the year from the filename, so names must contain a
   4-digit year (e.g. `1990_landcover.tif`).
3. **Preprocess to binary.** Extract the target class (e.g. forest) and make the
   rest of the raster binary — foreground = 2, background = 1, nodata = 0, 8-bit —
   as required by MSPA.
4. **Run MSPA** (GuidosToolbox Workbench) to produce the pattern-class rasters in
   `2_MSPA/`. Clear the MSPA output folder before each run; leftover log files
   cause it to fail.
5. **Run the remaining steps in order.** Stages 3–5 create their own subfolders
   under `data/` automatically. Do not create the `3_MovingWindow`,
   `4_TS_and_TI`, or `5_Typology` folders by hand — just set `main_workspace` and
   run the scripts in sequence.

The repository ships with example outputs under `data/` (e.g. the `mw_*`
moving-window rasters) so you can inspect the expected structure before running
your own data.

## Two parallel workflows

- **`code/arcpy_workflow/`** — the original implementation using ArcGIS Pro and
  the ArcPy Spatial Analyst extension. See
  [`code/arcpy_workflow/README.md`](code/arcpy_workflow/README.md).
- **`code/ipynb_workflow/`** — an open-source Python/Jupyter implementation
  (rioxarray, rasterio, dask) that does not require a commercial license. See
  [`code/ipynb_workflow/README.md`](code/ipynb_workflow/README.md).

## Environment setup (ipynb workflow)

The Jupyter workflow runs in a reproducible Conda environment defined in
`environment.yml`. A Dockerfile is provided to build it.

Using Conda directly:

```bash
conda env create -f environment.yml
conda activate typology_env
jupyter lab
```

Using Docker:

```bash
# 1. Change into the repository directory
cd /path/to/typology/

# 2. Build the image
docker build -t typology_env .

# 3. Run the image (mounts the repo into the container)
docker run -p 8888:8888 -p 8787:8787 -v $(pwd):/home/gisuser/code/ -it typology_env
```

Port `8888` serves JupyterLab and `8787` serves the Dask dashboard. On Windows,
run the Docker commands from WSL and use the WSL mount path, e.g.
`cd /mnt/c/Users/username/path/to/typology/`.

The ArcPy workflow requires a separate ArcGIS Pro installation and its bundled
Python environment; see the arcpy workflow README.

## References

- Adorno et al. 2021
- Barima et al. 2016
- Bogaert, J., Ceulemans, R., Salvador-Van Eysenrode, D. 2004. Decision tree
  algorithm for detection of spatial processes in landscape transformation.
  *Environmental Management*.
- Eastman, J.R. 2024. TerrSet 2020 (IDRISI). Clark Labs.
- Esri 2025. ArcGIS Pro v3.5.
- Fahrig, L. et al. 2019. Is habitat fragmentation bad for biodiversity?
  *Biological Conservation*.
- Laurance, W.F. et al. 2002. Ecosystem decay of Amazonian forest fragments.
- Manzoli et al. 2023
- Rocha-Santos et al. 2017
- Soille, P., Vogt, P. 2009, 2022. Morphological segmentation of binary patterns.
- Torres Mallma and Torres Mallma 2024
- Vogt, P. et al. 2022. GuidosToolbox Workbench (GWB).

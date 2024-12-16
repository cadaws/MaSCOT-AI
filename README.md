# MaSCOT-AI
Mammary cell shape computation over time with Trackmate-Cellpose

This code was used to analyse intravital microscopy data of single mammary gland cells in mice in puberty, adulthood and pregnancy.
<br> Associated publication: **Dawson, Milevskiy et al. Cell Reports, 2024, Hormone-responsive progenitors have a unique identity and exhibit high motility during mammary morphogenesis.**

## Data acquisition
Movies were acquired using an Olympus-FVMPRS system with a 25x objective and 1.5 zoom at 512x512 pixels and 2 µm z-step.
Custom filters for Confetti fluorescent protein detection are described in the paper.
<br> See our protocol also:
- Dawson, C.A., Mueller, S.N., Lindeman, G.J. et al. Intravital microscopy of dynamic single-cell behavior in mouse mammary tissue. Nat Protoc 16, 1907–1935 (2021). https://doi.org/10.1038/s41596-020-00473-2

## Data processing
The original 4D movies were stabilised by a combination of 4D cell tracking and 'Correct 3D drift' in Imaris in FIJI with HyperStackReg
350 2D movies of single cell spans (10-15 µm) were generated manually by 3D crop in Imaris, then flattened by maximum projection in FIJI

## Model training
The MasCOT-AI model was trained in Cellpose 2 on 150 still images (the fifth time point from a representative sample of movies).
Training was initialised with the CP model and automatic cell size determination.

## Trackmate-Cellpose analysis
Analyse 2D movies with the Cellpose model within Trackmate to connect cell measurements over time, then extract and visualise meaningful information.

**Python script: Trackmate-Cellpose MaSCOT-AI.py**
<br> Incorporates the MaSCOT-AI model into Trackmate and loops through tiff time lapses to export various cell shape descriptors as csv
<br> Based on:
<br> https://imagej.net/plugins/trackmate/scripting/scripting
<br> https://imagej.net/plugins/trackmate/scripting/trackmate-detectors-trackers-keys
<br> https://github.com/trackmate-sc/TrackMate-Cellpose

**R script: 1 Read and split Trackmate-Cellpose data MaSCOT-AI**
<br> Compiles all cell timelines for each measurement in large nested lists

**R script: 2 Unnest and transform Trackmate-Cellpose data MaSCOT-AI**
<br> Rearranges the lists into a simple table so that each row represents a cell with an ID, sample label and measurements over time.

**Excel file: MaSCOT-AI_ellipse_aspectratio_analysis**
<br> Example of data analysis including:
* Extraction of cell tracks representative of percentiles
* Running average calculation
* Measuring peak frequency

Thanks for your interest and please get in touch @calebadawson (X/Twitter)

# MaSCOT-AI
Mammary cell shape computation over time with Trackmate-Cellpose

This code was used to analyse intravital microscopy data of single mammary gland cells in mice in puberty, adulthood and pregnancy.
<br> Associated publication: **Dawson, Milevskiy et al. Cell Reports, 2024, Hormone-responsive progenitors have a unique identity and exhibit high motility during mammary morphogenesis.** https://doi.org/10.1016/j.celrep.2024.115073
<br>
<br>
This workflow was built from work by Jean-Yves Tinevez, for which I am very grateful! Please refer to these sources for more detailed descriptions and troubleshooting. Sources include:
<br> https://imagej.net/plugins/trackmate/scripting/scripting
<br> https://imagej.net/plugins/trackmate/scripting/trackmate-detectors-trackers-keys
<br> https://github.com/trackmate-sc/TrackMate-Cellpose

## Deposited model, data, training images and example analysis
The MaSCOT-AI Cellpose model, training data and all analysed movies have been deposited on Zenodo (https://doi.org/10.5281/zenodo.14503475).
The data analysed in the paper are 2D single channel maximum projections derived from 4D multichannel intravital movies (Mammary epithelial cell lineage-specific Confetti fluorescence). I have also deposited the extracted 5th time points that were used for training the MaSCOT-AI model along with the associated Cellpose 2 segmentation files (.npy).
I will also upload a folder of example analyses movies and the resulting data exported from Trackmate-Cellpose.

## Data acquisition
Movies were acquired using an Olympus-FVMPRS system with a 25x objective and 1.5 zoom at 512x512 pixels and 2 µm z-step.
Mice were anaesthetised with isoflurane and the mammary glands were exposed on a skin flap and covered by a cover slip to make a small chamber sealed with silicone grease.
Our protocol paper describes this procedure and the custom filters used for Confetti fluorescence detection along with SHG and a far-red dye.
<br> Dawson, C.A., Mueller, S.N., Lindeman, G.J. et al. Intravital microscopy of dynamic single-cell behavior in mouse mammary tissue. Nat Protoc 16, 1907–1935 (2021). https://doi.org/10.1038/s41596-020-00473-2

## Data processing
The original 4D movies were stabilised by a combination of 4D cell tracking and 'Correct 3D drift' in Imaris, and by HyperStackReg in FIJI.
350 2D movies of single cell spans (10-30 µm) were generated manually by 3D crop in Imaris, then flattened by maximum projection in FIJI.

## Model training
The MasCOT-AI model was iteratively trained in Cellpose 2.2.2 on 150 still images (the fifth time point from a representative sample of movies).
Training was initialised with the CP model and automatic cell size determination.
<br>
<br> **Required software/packages:**
* Miniconda
* Cellpose Conda environment with Cellpose 2.2.2 installation (additional packages listed here: https://pypi.org/project/cellpose/)
* Conda pytorch install for GPU processing

## Trackmate-Cellpose analysis
Analyse 2D movies with the Cellpose model within Trackmate to connect cell measurements over time, then extract and visualise meaningful information.
<br>
<br> **Required software/packages:**
* FIJI (ImageJ 1.54h was used here)
* Plugins: Trackmate 7.11.1
* Miniconda
* Cellpose Conda environment with Cellpose 2.2.2 installation (additional packages listed here: https://pypi.org/project/cellpose/)
* Conda pytorch install for GPU processing

**Python script: Trackmate-Cellpose MaSCOT-AI.py**
<br> Incorporates the MaSCOT-AI model into Trackmate and loops through tiff time lapses to export various cell shape descriptors as csv, based on:
<br> https://imagej.net/plugins/trackmate/scripting/scripting
<br> https://imagej.net/plugins/trackmate/scripting/trackmate-detectors-trackers-keys
<br> https://github.com/trackmate-sc/TrackMate-Cellpose

**R script: 1 Read and split Trackmate-Cellpose data MaSCOT-AI**
<br> This script compiles all cell timelines for each measurement into large nested lists

**R script: 2 Unnest and transform Trackmate-Cellpose data MaSCOT-AI**
<br> This script rearranges the lists into a simple table so that each row represents a cell with an ID, sample label and measurements over time.

**Excel file: MaSCOT-AI_ellipse_aspectratio_analysis**
<br> Example of data analysis including:
* Extraction of cell tracks representative of percentiles
* Running average calculation
* Measuring peak frequency

Thanks for your interest and please get in touch @calebadawson (X/Twitter)

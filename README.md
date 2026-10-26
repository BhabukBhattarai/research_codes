# Research Codes

This repository contains code developed and used for research in hydrology, flood mapping, hydrological model evaluation, and machine learning-based land-use and land-cover (LULC) modelling.

## Projects

### 1. Sentinel-1 Flood Mapping and Flood Point Extraction

**Language:** JavaScript
**Platform:** Google Earth Engine

A workflow for identifying potential flood inundation areas using Sentinel-1 Synthetic Aperture Radar (SAR) imagery. The script applies Refined Lee speckle filtering, compares pre-event and post-event backscatter, and generates flood and non-flood sample points for export.

**Main features:**

- Sentinel-1 VH-polarization image processing
- Refined Lee speckle filtering
- Threshold-based flood inundation mapping
- Flood and non-flood sample point extraction
- CSV export and map visualization

**Status:** Research script. The flood classification depends on the selected dates and backscatter threshold and requires independent validation for reliable flood mapping.

### 2. Taylor Diagram for Hydrological Model Evaluation

**Language:** Python

A plotting script developed to compare the calibration and validation performance of the HBV and HEC-HMS rainfall–runoff models.

**Main features:**

- Calculation of correlation coefficients
- Normalized standard-deviation ratios
- Centered root-mean-square difference (CRMSD)
- Side-by-side Taylor diagrams for calibration and validation
- High-resolution PDF figure export

**Status:** Research visualization script. Input data must contain observed runoff and simulated runoff from both hydrological models.

### 3. CatBoost-Based LULC Prediction Prototype

**Language:** Python
**Algorithm:** CatBoost Classifier

An exploratory machine-learning workflow designed to investigate multiclass LULC classification and iterative projections for future years.

**Main features:**

- Definition of eight LULC classes
- Synthetic spatial explanatory variables
- Simulated land-cover transitions
- CatBoost model training
- Preliminary iterative projections for 2030 and 2035
- Summary of land-cover class counts

**Status:** Preliminary prototype. The current implementation uses synthetic data and has not been validated against observed LULC maps. It does not yet generate georeferenced LULC maps.

## Tools and Libraries

- Google Earth Engine
- JavaScript
- Python
- NumPy
- Pandas
- Matplotlib
- scikit-learn
- CatBoost

## Repository Structure

```text
research_codes/
├── README.md
├── flood_point_detection/
│   ├── food_point_detection.js
│   └── README.md
├── taylor-diagram/
│   ├── taylor_diagram_hbv_hechms.py
│   └── README.md
└── future_lulc_prediction/
    ├── lulc_prediction.py
    └── README.md
```

## Purpose

The purpose of this repository is to document and share computational workflows developed for hydrological and geospatial research. The scripts cover satellite-based flood mapping, visualization of hydrological model performance, and exploratory machine-learning approaches for LULC modelling.

## Limitations

These scripts have different levels of development. Their outputs depend on the input data, parameter choices, and assumptions described in each project. The LULC prediction script is experimental and uses synthetic data; its projections should not be interpreted as validated forecasts.

## Author

Bhabuk Raj Bhattarai


# DNS-2021 Dataset: Data Preprocessing and Exploratory Data Analysis (EDA)

This project involves the data preprocessing and exploratory data analysis (EDA) of the DNS-2021 dataset from the University of New Brunswick. The data is stored in an S3 bucket and processed using Python.

## Table of Contents

- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Data Preprocessing](#data-preprocessing)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)

## Dataset

The DNS-2021 dataset can be accessed from the University of New Brunswick's [website](https://www.unb.ca/cic/datasets/dns-2021.html). This dataset contains detailed network traffic data, which is used for analyzing and detecting Domain Name System (DNS) anomalies.

## Project Structure
```
.
├── data/
│   ├── raw/                  # Raw data from the DNS-2021 dataset
│   ├── processed/            # Processed data after preprocessing steps
├── notebooks/                # Jupyter notebooks for EDA
├── scripts/
│   ├── data_preprocessing.py # Script for data preprocessing
│   ├── eda.py                # Script for EDA
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore file
├── README.md                 # Project README 
```              


## Getting Started

### Prerequisites

- Python 3.12
- boto3
- pandas
- matplotlib
- seaborn

You can install the necessary packages using pip:

```bash
pip install - r requirements.txt
```

## Data Ingestion

Before starting with the data preprocessing and analysis, ensure that the DNS-2021 dataset is uploaded to your S3 bucket.

then, create an .env file as follow:
```bash
AWS_ACCESS_KEY_ID=your-value
AWS_SECRET_ACCESS_KEY=eyour-value
AWS_DEFAULT_REGION=your-value
S3_BUCKET_NAME=your-value
```


## Data Preprocessing

The preprocessing steps involve:

	1. Loading Data from S3: Using the boto3 library to load data directly from an S3 bucket to data/raw.
	2. Handling typos and complex array in each csv file.
	3. load the preprocess csv files into data/processed 

MAKE SURE TO EXECUTE SCRIPT FOR DATA PREPROCESSING BEFORE RUNNING THE NOTEBOOK.
file can be found in scripts/data_preprocessing.py

## Exploratory Data Analysis (EDA)

The EDA includes:

	1.	Descriptive Statistics: Getting an overview of the data.
	2.	Data Visualization: Using tools like Matplotlib and Seaborn to visualize distributions, correlations, and trends.
	3.	Feature Relationships: Exploring relationships between different features.
	4.	Trend Analysis: Analyzing trends over time, especially if the data includes timestamps.

Jupyter notebooks for EDA can be found in the notebooks/ directory.


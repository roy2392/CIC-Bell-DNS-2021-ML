# DNS-2021 Dataset: Data Preprocessing and Exploratory Data Analysis (EDA)

This project involves the data preprocessing and exploratory data analysis (EDA) of the DNS-2021 dataset from the University of New Brunswick. The data is stored in an S3 bucket and processed using Python.

## Table of Contents

- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Data Preprocessing](#data-preprocessing)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Storing Processed Data](#storing-processed-data)
- [Contributing](#contributing)
- [License](#license)

## Dataset

The DNS-2021 dataset can be accessed from the University of New Brunswick's [website](https://www.unb.ca/cic/datasets/dns-2021.html). This dataset contains detailed network traffic data, which is used for analyzing and detecting Domain Name System (DNS) anomalies.

## Project Structure
├── data/
│   ├── raw/                  # Raw data from the DNS-2021 dataset
│   ├── processed/            # Processed data after preprocessing steps
├── notebooks/                # Jupyter notebooks for EDA
├── scripts/
│   ├── data_preprocessing.py # Script for data preprocessing
│   ├── eda.py                # Script for EDA
├── README.md                 # Project README file


## Getting Started

### Prerequisites

- Python 3.x
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

## Data Preprocessing

The preprocessing steps involve:

	1.	Loading Data from S3: Using the boto3 library to load data directly from an S3 bucket.
	2.	Handling Missing Values: Filling or dropping missing values based on the context.
	3.	Data Type Conversion: Ensuring all data types are appropriate for analysis.
	4.	Handling Outliers: Identifying and treating outliers using statistical methods.

Scripts for data preprocessing can be found in scripts/data_preprocessing.py.

## Exploratory Data Analysis (EDA)

The EDA includes:

	1.	Descriptive Statistics: Getting an overview of the data.
	2.	Data Visualization: Using tools like Matplotlib and Seaborn to visualize distributions, correlations, and trends.
	3.	Feature Relationships: Exploring relationships between different features.
	4.	Trend Analysis: Analyzing trends over time, especially if the data includes timestamps.

Jupyter notebooks for EDA can be found in the notebooks/ directory.

Storing Processed Data

After preprocessing and analysis, the cleaned data is stored back into the S3 bucket. The script for this can be found in scripts/data_preprocessing.py.
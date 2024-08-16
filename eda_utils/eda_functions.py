# Import necessary libraries
import pandas as pd
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# this function will fill the numerical values based on the skewness of the data 
def decide_fill_method(df_list, columns):
    fill_methods = {}
    for df in df_list:
        for col in columns:
            if col in df.columns:
                skewness = df[col].skew()
                if abs(skewness) > 0.5:  # moderately to heavily skewed
                    fill_methods[col] = 'median'
                else:
                    fill_methods[col] = 'mean'
    return fill_methods

# this function will fill the numerical values based on the fill_methods
def fill_numeric_columns(df_list, columns, fill_methods):
    for df in df_list:
        for col in columns:
            if col in df.columns:
                if fill_methods[col] == 'median':
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mean())
    return df_list

# this function will define the data types for the columns and then will align the data types across all dataframes
def align_data_types(df_list):
    data_types = {
        'tld': 'object',
        'oc_8': 'int64',
        'char_distribution': 'object',
        'Emails': 'object',
        'subdomain': 'bool',  # boolean 1 - True and 0 - False
        'State': 'object',
        '1gram': 'object',
        'obfuscate_at_sign': 'int64',
        'longest_word': 'object',
        'puny_coded': 'bool',  # boolean 1 - True and 0 - False
        '2gram': 'object',
        'Country': 'object',
        'Organization': 'object',
        'numeric_percentage': 'float64',
        'hex_8': 'float64',
        'Creation_Date_Time': 'datetime64[ns]',
        'Domain': 'object',
        'len': 'int64',
        'Domain_Name': 'object',
        'Page_Rank': 'int64',
        'Alexa_Rank': 'float64',
        'ASN': 'object', #  unique 16 digit identification number
        'dec_8': 'int64',
        '3gram': 'object',
        'shortened': 'bool',  # boolean 1 - True and 0 - False
        'entropy': 'float64',
        'Domain_Age': 'object',
        'dec_32': 'bool',  # boolean 1 - True and 0 - False
        'Name_Server_Count': 'int64',
        'typos': 'object',
        'TTL': 'int64',
        'sld': 'object',
        'Registrar': 'object',
        'hex_32': 'float64',
        'oc_32': 'float64',
        'IP': 'object'
    }

    # Align data types across all dataframes
    for df in df_list:
        for col, dtype in data_types.items():
            if col in df.columns:
                if dtype == 'bool':
                    df[col] = df[col].astype('bool')
                elif dtype in ['int64', 'float64']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if dtype == 'int64':
                        df[col] = df[col].fillna(0).astype('int64')  # Handle NaNs before converting to int
                else:
                    df[col] = df[col].astype(dtype, errors='ignore')
    
    return df_list

# this function will remove the outliers from the data - 1% and 99% quantile
def remove_outliers(df, feature, lower_quantile=0.01, upper_quantile=0.99):
    lower_bound = df[feature].quantile(lower_quantile)
    upper_bound = df[feature].quantile(upper_quantile)
    before_count = len(df)
    df_filtered = df[(df[feature] >= lower_bound) & (df[feature] <= upper_bound)]
    after_count = len(df_filtered)
    print(f"Feature: {feature}")
    print(f"Rows before removing outliers: {before_count}")
    print(f"Rows after removing outliers: {after_count}")
    print(f"Rows removed: {before_count - after_count}\n")
    return df_filtered

# create a function for  any numeric feature in your dataframe
def plot_feature_distribution(df, feature, bins=None):
    # Define bins if not provided
    if bins is None:
        bins = 10  # Default number of bins if not specified

    # Create bins for the feature
    df[f'{feature}_bin'] = pd.cut(df[feature], bins=bins)

    # Calculate the percentage of each bin within each class
    feature_distribution = df.groupby(['class', f'{feature}_bin'], observed=True).size().unstack(fill_value=0)
    feature_distribution = feature_distribution.div(feature_distribution.sum(axis=1), axis=0) * 100

    # Plot the histogram
    ax = feature_distribution.T.plot(kind='bar', stacked=True, figsize=(14, 7))

    plt.title(f'Distribution of {feature} by Class (Percentage within each Class)')
    plt.xlabel(f'{feature} Bins')
    plt.ylabel('Percentage of Rows within Class (%)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Class', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add percentage labels
    for p in ax.patches:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy() 
        if height > 0:  # Only label the patches with height > 0
            ax.text(x + width/2, 
                    y + height/2, 
                    f'{height:.2f}%', 
                    ha='center', 
                    va='center')
    
    plt.tight_layout()
    plt.show()

# create a function for any categorical feature in your dataframe
def analyze_categorical_feature(df, feature):
    # Set the style for the plots
    sns.set_style("whitegrid")
    sns.set_palette("deep")

    # Create a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()

    # Remove 'unknown' values (case-insensitive)
    df_copy = df_copy[~df_copy[feature].str.lower().isin(['unknown', 'unk', 'n/a', 'none', '0','1'])]

    # Create subplots for each class
    n_classes = len(df_copy['class'].unique())
    n_cols = 2
    n_rows = (n_classes + 1) // 2  # Ceiling division
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 10 * n_rows))
    fig.suptitle(f'Top 10 Categories in {feature} by Class (Excluding Unknown)', fontsize=20, fontweight='bold')

    axes = axes.flatten()  # Flatten the axes array for easy indexing

    for i, cls in enumerate(df_copy['class'].unique()):
        ax = axes[i]
        class_data = df_copy[df_copy['class'] == cls]
        value_counts = class_data[feature].value_counts()
        total_count = len(class_data)
        
        # Calculate percentages
        percentages = (value_counts / total_count) * 100
        
        # Plot horizontal bar chart
        sns.barplot(y=percentages.index[:10], x=percentages.values[:10], ax=ax, orient='h')
        ax.set_title(f'Class: {cls}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Percentage', fontsize=12)
        ax.set_ylabel(feature, fontsize=12)
        
        # Add percentage and count labels to the end of each bar
        for j, (p, c) in enumerate(zip(percentages.values[:10], value_counts.values[:10])):
            ax.text(p, j, f'{p:.1f}% ({c})', va='center', fontweight='bold')
        
        # Remove top and right spines
        sns.despine(ax=ax, top=True, right=True)
        
        # Set the x-axis limit to slightly more than the maximum percentage
        ax.set_xlim(0, max(percentages.values[:10]) * 1.1)

    # Remove any unused subplots
    for i in range(n_classes, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.show()

    # text summary
    summary = f"Analysis for {feature} (Excluding Unknown):\n\n"
    for cls in df_copy['class'].unique():
        class_data = df_copy[df_copy['class'] == cls]
        value_counts = class_data[feature].value_counts()
        total_count = len(class_data)
        percentages = (value_counts / total_count) * 100
        
        summary += f"Class: {cls}\n"
        summary += f"Total unique values: {class_data[feature].nunique()}\n"
        summary += f"Total samples after removing unknown: {total_count}\n"
        summary += "Top 5 categories:\n"
        for cat, count in value_counts.head().items():
            summary += f"{cat}: {count} ({percentages[cat]:.1f}%)\n"
        summary += "\n"
        print(summary)

# this function will apply frequency encoding to the categorical columns
def frequency_encode(df, exclude_columns=None, drop_original=True):
    if exclude_columns is None:
        exclude_columns = []
    
    columns_to_encode = [col for col in df.select_dtypes(include=['object', 'category']).columns if col not in exclude_columns]
    
    for col in columns_to_encode:
        freq_map = df[col].value_counts().to_dict()
        df[col + '_encoded'] = df[col].map(freq_map)
    
    if drop_original:
        df = df.drop(columns=columns_to_encode)
    
    return df

import streamlit as st
import pandas as pd
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs

# Function to parse multiple prX structured data into separate columns
def parse_pr_data(pr_values):
    parsed_data = {}

    for pr_key, pr_value in pr_values.items():
        if pd.isna(pr_value) or not isinstance(pr_value, str):
            continue  # Skip if empty

        parts = pr_value.split("~")  # Split by delimiter
        product_number = pr_key[2:]  # Extract the product number (e.g., "1" from "pr1")
        prefix = f"p{product_number}_"  # Use "p1_", "p2_", etc.

        for part in parts:
            if len(part) < 3:  # Ignore unexpected short data
                continue

            key = part[:2]  # First 2 characters as the key
            value = part[2:].strip()  # Everything after is the value

            parsed_data[f"{prefix}{key}"] = urllib.parse.unquote(value)  # URL-decode

    return parsed_data

# Function to extract GA4 parameters from Request URL
def extract_ga4_params(url):
    query_params = parse_qs(urlparse(url).query)
    return {key: ', '.join(value) for key, value in query_params.items()}

# Streamlit UI
st.title("GA4 Log Analyzer")

# File Upload
uploaded_file = st.file_uploader("Lade dein Log-File hoch (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Ensure only "Request Url" column is used
    if "Request Url" in df.columns:
        # Extract GA4 parameters and remove "Request Url" immediately after extraction
        ga4_params_list = [extract_ga4_params(url) for url in df["Request Url"]]
        ga4_params_df = pd.DataFrame(ga4_params_list)

        # Drop the original "Request Url" column (reducing file size)
        df = ga4_params_df.copy()

        # Find all columns that start with "pr" (pr1, pr2, pr3...)
        pr_columns = [col for col in df.columns if col.startswith("pr")]

        # Pass all prX columns to parse_pr_data() dynamically
        if pr_columns:
            structured_pr_data = df[pr_columns].apply(lambda row: parse_pr_data(row.to_dict()), axis=1)

            # Convert the parsed dictionary into a DataFrame and merge it back
            structured_pr_df = pd.json_normalize(structured_pr_data)
            df = pd.concat([df, structured_pr_df], axis=1)

            # Drop the original prX columns to keep the file clean
            df = df.drop(columns=pr_columns)

        # Display structured GA4 data with extracted prX columns
        st.write("### Cleaned GA4 Data with Structured prX Parameters")
        st.dataframe(df)

        # Save structured data to CSV
        output_csv = "ga4_cleaned_data.csv"
        df.to_csv(output_csv, index=False)

        # Download button
        with open(output_csv, "rb") as f:
            st.download_button("Download Cleaned GA4 Data", f, file_name="ga4_cleaned_data.csv", mime="text/csv")
    else:
        st.error("The file does not contain a 'Request Url' column!")

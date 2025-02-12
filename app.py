import streamlit as st
import pandas as pd
import re  # Regular expressions
import urllib.parse  # For URL decoding
from urllib.parse import urlparse, parse_qs  # GA4 parameter extraction

# Function to extract GA4 parameters from Request URL
def extract_ga4_params(url):
    query_params = parse_qs(urlparse(url).query)
    return {key: ', '.join(value) for key, value in query_params.items()}

# Function to correctly parse pr1 structured data into separate columns
def parse_pr1_data(pr_value):
    if pd.isna(pr_value) or not isinstance(pr_value, str):
        return {}

    parts = pr_value.split("~")
    parsed_data = {}

    # Extract `prX.XX` value if present
    if parts[0].startswith("pr") and "." in parts[0][2:]:
        parsed_data["pr1_pr"] = parts[0][2:]  # Extract value after "pr"
        parts = parts[1:]  # Remove from list
    else:
        parsed_data["pr1_pr"] = ""  # Fallback if missing

    # Loop through remaining key-value pairs
    for part in parts:
        # Extract kX, vX, and standard parameters
        match = re.match(r"^([a-zA-Z]+\d*)(.*)$", part)
        if match:
            key, value = match.groups()
            parsed_data[f"pr1_{key}"] = urllib.parse.unquote(value.strip())  # URL-decode
        else:
            parsed_data[f"pr1_{part}"] = ""  # Handle standalone keys

    return parsed_data

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

        # Extract and structure pr1 item data
        if "pr1" in df.columns:
            structured_pr1_data = df["pr1"].apply(parse_pr1_data)
            structured_pr1_df = pd.json_normalize(structured_pr1_data)
            df = pd.concat([df, structured_pr1_df], axis=1)  # Merge new columns

            # Drop raw "pr1" column after extraction
            df = df.drop(columns=["pr1"])

        # Display structured GA4 data with extracted pr1 columns
        st.write("### Cleaned GA4 Data with Structured pr1 Parameters")
        st.dataframe(df)

        # Save structured data to CSV
        output_csv = "ga4_cleaned_data.csv"
        df.to_csv(output_csv, index=False)

        # Download button
        with open(output_csv, "rb") as f:
            st.download_button("Download Cleaned GA4 Data", f, file_name="ga4_cleaned_data.csv", mime="text/csv")
    else:
        st.error("The file does not contain a 'Request Url' column!")

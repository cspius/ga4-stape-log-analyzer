import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

# Function to extract GA4 parameters from URL
def extract_ga4_params(url):
    query_params = parse_qs(urlparse(url).query)
    return {key: ', '.join(value) for key, value in query_params.items()}

# Function to parse structured GA4 item parameters from pr1
def parse_pr1_data(pr_value):
    if pd.isna(pr_value) or not isinstance(pr_value, str):
        return {}

    parts = pr_value.split("~")
    parsed_data = {}

    for i in range(0, len(parts) - 1, 2):
        key = str(parts[i]).strip()  # Ensure key is always a string
        value = str(parts[i + 1]).strip()  # Ensure value is always a string

        # Ensure the key is valid before applying regex
        if key and isinstance(key, str) and re.match(r'^[a-zA-Z]+\d*$', key):  
            parsed_data[f"pr1_{key}"] = value

    return parsed_data

# Streamlit UI
st.title("GA4 Log Analyzer")

# File Upload
uploaded_file = st.file_uploader("Lade dein Log-File hoch (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Request Url" in df.columns:
        # Extract GA4 parameters
        ga4_params_list = [extract_ga4_params(url) for url in df["Request Url"]]
        ga4_params_df = pd.DataFrame(ga4_params_list)

        # Merge extracted GA4 parameters with original data
        df = pd.concat([df, ga4_params_df], axis=1)

        # Extract and structure `pr1` item data
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

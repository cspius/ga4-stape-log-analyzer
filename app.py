import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

# Function to extract GA4 parameters from URL
def extract_ga4_params(url):
    query_params = parse_qs(urlparse(url).query)
    return {key: ', '.join(value) for key, value in query_params.items()}

# Function to parse GA4 item data from "pr1", "pr2", etc.
def parse_item_data(pr_value):
    if pd.isna(pr_value):
        return {}
    parts = pr_value.split("~")
    parsed_data = {}
    
    key = None
    for part in parts:
        if part.startswith("k"):
            key = part[1:]  # Remove 'k' prefix (e.g., k0item_tax_rate -> item_tax_rate)
        elif part.startswith("v") and key:
            parsed_data[key] = part[1:]  # Remove 'v' prefix (value assignment)
            key = None
        elif key:
            parsed_data[key] = part  # Assign remaining values
            key = None

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

        # Extract item data (from pr1, pr2, etc.)
        item_columns = [col for col in ga4_params_df.columns if col.startswith("pr")]
        if item_columns:
            structured_item_data = ga4_params_df[item_columns].applymap(parse_item_data)
            structured_item_df = pd.json_normalize(structured_item_data.stack().tolist())

            # Display structured item data
            st.write("### Extracted GA4 Item Data")
            st.dataframe(structured_item_df)

            # Save structured data to CSV
            output_csv = "ga4_item_data_cleaned.csv"
            structured_item_df.to_csv(output_csv, index=False)

            # Download button
            with open(output_csv, "rb") as f:
                st.download_button("Download Processed Item Data", f, file_name="ga4_item_data_cleaned.csv", mime="text/csv")
        else:
            st.warning("No item data (pr1, pr2, etc.) found in the uploaded file.")
    else:
        st.error("The file does not contain a 'Request Url' column!")

import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

def extract_ga4_params(url):
    query_params = parse_qs(urlparse(url).query)
    return {key: ', '.join(value) for key, value in query_params.items()}

st.title("GA4 Stape Log Analyzer")

uploaded_file = st.file_uploader("Lade dein Log-File hoch (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if "Request Url" in df.columns:
        ga4_params_list = [extract_ga4_params(url) for url in df["Request Url"]]
        ga4_params_df = pd.DataFrame(ga4_params_list)

        st.write("### Extrahierte GA4-Parameter")
        st.dataframe(ga4_params_df)

        output_csv = "ga4_params_cleaned.csv"
        ga4_params_df.to_csv(output_csv, index=False)

        with open(output_csv, "rb") as f:
            st.download_button("Download bereinigte CSV", f, file_name="ga4_params_cleaned.csv", mime="text/csv")
    else:
        st.error("Die Datei enthält keine 'Request Url'-Spalte!")

import streamlit as st
import pandas as pd
import json

from windwatch.config import DATA_DIR


def main(input_path):
    
    try:
        df = pd.read_json(input_path, lines=True)
    except:
        print("Error loading file")
        return

    st.title(f"{df["comName"][0]} Observations")

    # Create map
    st.map(df[['lat', 'lon', 'howMany']],
           latitude='lat',
           longitude='lon',
           size='howMany',
           color='#4bb4ff')
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(df)

if __name__ == "__main__":
    main(DATA_DIR+"proc_bird_sighting_data.jsonl")

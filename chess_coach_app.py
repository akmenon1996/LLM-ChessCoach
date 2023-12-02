import streamlit as st
import subprocess
import os
from export_lichess_games import ChessGameDownloader  # Import your ChessGameDownloader class

# Streamlit UI
st.title("Chess Game Analyzer")
st.write("Enter your details and date range to analyze chess games.")

# User Inputs
username = st.text_input("Username:")
api_token = st.text_input("API Token:", type="password")
start_date = st.date_input("Start Date:")
end_date = st.date_input("End Date:")

if st.button("Analyze"):
    downloader = ChessGameDownloader()

    # Download and save games
    epoch_time = downloader.date_text_to_epoch(start_date.strftime('%Y-%m-%d'))
    folder = downloader.fetch_and_save_games(epoch_time)
    st.success(f"Loaded files successfully to --> {folder}")

    status = downloader.run_analysis()

    # Display the analysis results or errors
    if status:
        st.success("Analysis completed successfully!")

        # Capture and display the folder path for analysis
        analysis_folder_path = f'{folder}/analysis/'
        st.write(f"Analysis results are available in the folder: {analysis_folder_path}")

        # Display individual game analyses
        if analysis_folder_path:
            for root, dirs, files in os.walk(analysis_folder_path):
                for file in files:
                    if file.endswith("_analysis.txt"):
                        analysis_file_path = os.path.join(root, file)
                        with open(analysis_file_path, 'r') as analysis_file:
                            analysis_content = analysis_file.read()
                        st.write(f"Analysis for {file}:")
                        st.write(analysis_content)
    else:
        st.error("An error occurred during analysis:")

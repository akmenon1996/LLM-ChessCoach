import streamlit as st
import os
from export_lichess_games import ChessGameDownloader

# Initialize session state
if 'view_results' not in st.session_state:
    st.session_state['view_results'] = False
if 'analysis_folder_path' not in st.session_state:
    st.session_state['analysis_folder_path'] = ""


# Main app logic
def page_switch_logic():
    print("Switch Logic Active")
    if st.session_state['view_results']:
        results_page()
    else:
        main_page()
        
# Streamlit UI for the main page
def main_page():
    st.title("Chess Game Analyzer")
    st.write("Enter your details and date range to analyze chess games.")

    username = st.text_input("Username:")
    api_token = st.text_input("API Token:", type="password")
    start_date = st.date_input("Start Date:")
    end_date = st.date_input("End Date:")
    run_id = st.text_input("Run ID:")

    if st.button("Analyze"):
        downloader = ChessGameDownloader()
        epoch_time = downloader.date_text_to_epoch(start_date.strftime('%Y-%m-%d'))
        if len(run_id)>0:
            status = downloader.run_analysis(run_id=run_id,username=username)
        else:
            folder = downloader.fetch_and_save_games(epoch_time)
            st.success(f"Loaded files successfully to --> {folder}")

            status = downloader.run_analysis()

        if status:
            st.success("Analysis completed successfully!")
            if len(run_id)>0:
                st.session_state['analysis_folder_path'] = f'games/{run_id}/analysis/'
            else:
                st.session_state['analysis_folder_path'] = f'{folder}/analysis/'
            st.session_state['view_results'] = True
            if st.button("View Results"):
                pass
                
        else:
            st.error("An error occurred during analysis:")


# Streamlit UI for the results page
def results_page():
    st.title("Analysis Results")
    analysis_folder_path = st.session_state['analysis_folder_path']
    print(analysis_folder_path)

    # Sidebar with individual game analyses
    with st.sidebar:
        st.header("Games")
        game_files = [file for root, dirs, files in os.walk(analysis_folder_path) for file in files if file.endswith("_analysis.txt")]
        for file in game_files:
            print(file)
            if st.button(file,key=file):
                st.session_state['selected_game'] = os.path.join(analysis_folder_path, file)

    # Display selected game analysis
    if 'selected_game' in st.session_state:
        with open(st.session_state['selected_game'], 'r') as analysis_file:
            analysis_content = analysis_file.read()
        st.subheader(f"Analysis for {os.path.basename(st.session_state['selected_game'])}")
        st.write(analysis_content)
    
    if st.button("Load Games again!"):
        st.session_state['analysis_folder_path'] = ""
        st.session_state['view_results'] = False
        page_switch_logic()



page_switch_logic()
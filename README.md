# LLM-ChessCoach

## Introduction
LLM-ChessCoach is an innovative tool that leverages Large Language Models (LLM), specifically GPT-3, to analyze chess games. It fetches games from online chess platforms, analyzes them, and provides insightful feedback to help players improve their strategies.

## Features
- **Game Import**: Downloads games from online chess platforms.
- **Advanced Analysis**: Uses GPT-3 to provide detailed game analyses.
- **Batch Processing**: Analyzes multiple games concurrently for efficiency.
- **User-Friendly Interface**: Offers a Streamlit-based web interface for easy interaction.

## Components
1. `export_lichess_games.py`: Downloads games from a chess website.
2. `chess_coach_app.py`: Streamlit application for user interaction.
3. `analyze_games.py`: Analyzes games using GPT-3 and saves the results.
4. `.gitignore`: Specifies untracked files to ignore.
5. `requirements.txt`: Lists all Python libraries required for the project.

## Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up your Lichess API token in `config.json`.

## Usage
1. Run the Streamlit app: `streamlit run chess_coach_app.py`.
2. Enter your details and select game dates for analysis.

## Contributing
Contributions are welcome. Please read the contributing guidelines first.

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgements
- Chess websites for game data.
- OpenAI's GPT-3 for game analysis.

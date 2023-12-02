import os
import requests
import json
from datetime import datetime
import argparse
import analyze_games as analyze_chess_games
import shortuuid

class ChessGameDownloader:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from 'config.json'."""
        with open('config.json') as f:
            config = json.load(f)
        return config

    def date_text_to_epoch(self, date_text):
        """Convert date text to epoch timestamp."""
        try:
            date_obj = datetime.strptime(date_text, '%Y-%m-%d')
            epoch_timestamp = int(date_obj.timestamp() * 1000)
            return epoch_timestamp
        except ValueError:
            return None

    def fetch_and_save_games(self, epoch_time):
        """Fetch and save user's chess games."""
        output_folder = self.create_output_folder()
        lichess_api_url = self.config['lichess_api_url']
        username = self.config['lichess_user_name']
        self.username = username
        lichess_api_url = f"{lichess_api_url}{username}?since={epoch_time}"
        api_token = self.config['lichess_api_token']

        response = requests.get(lichess_api_url, headers={"Authorization": f"Bearer {api_token}"})
        
        if response.status_code == 200:
            games_text = response.text
            games = games_text.split("\n\n\n")
            for index, game in enumerate(games):
                game_id = f"game_{index + 1}"
                filename = os.path.join(output_folder, f"{game_id}.pgn")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(game)
                print(f"Saved game {game_id} to {filename}")
        else:
            print(f"Failed to fetch games. Status code: {response.status_code}")
            print("Response content:", response.text)
        
        self.folder = output_folder
        return output_folder
    
    def run_analysis(self):
        analysis_status = analyze_chess_games.analyze_games(self.folder, self.username)
        return analysis_status

    def create_output_folder(self):
        """Create a unique output folder for storing downloaded games."""
        unique_id = shortuuid.uuid()
        output_folder = os.path.join("games", unique_id)
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

def main():
    parser = argparse.ArgumentParser(description="Download and analyze chess games.")
    parser.add_argument("--date", help="Date text in 'yyyy-mm-dd' format")
    parser.add_argument("--load_games", choices=["y", "n", "Y", "N"], help="Load games --> Y or N", default="Y")
    parser.add_argument("--analyze", choices=["y", "n", "Y", "N"], help="Analyze --> Y or N", default="N")
    parser.add_argument("--runid", required=False, help="Parameter (required only if mode is 'a')")

    args = parser.parse_args()

    downloader = ChessGameDownloader()

    if args.load_games.upper() == "Y":
        epoch_time = downloader.date_text_to_epoch(args.date)
        folder = downloader.fetch_and_save_games(epoch_time)

    if args.analyze.upper() == "Y":
        if args.load_games.upper() == 'N' and args.runid is None:
            parser.error("--runid is required when --load_games is 'N' and --analyze is 'Y'")
        elif args.load_games.upper() == 'N' and args.runid is not None:
            folder = f'games/{args.runid}'
        username = downloader.config['lichess_user_name']
        analyze_chess_games.analyze_games(folder, username)
    else:
        print("Not analyzing. Thank you!")

if __name__ == '__main__':
    main()
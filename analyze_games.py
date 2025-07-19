import os
import argparse
import chess.pgn
import io
from openai import OpenAI
import concurrent.futures
import threading
import multiprocessing
import json
from stockfish_engine import evaluate_game

def extract_players_from_pgn(pgn_content):
    """Extract White and Black players from PGN content."""
    game = chess.pgn.read_game(io.StringIO(pgn_content))
    white_player = game.headers.get("White", "Unknown")
    black_player = game.headers.get("Black", "Unknown")
    return white_player, black_player

def generate_chess_analysis(pgn, user_alias,type='single'):
    """Generate chess game analysis using GPT-3."""
    white_player, black_player = extract_players_from_pgn(pgn)
    if type == 'single':
        prompt = f"You are a chess grandmaster rated 3200. We are analyzing a chess game between {white_player} and {black_player}:\n\nProvide analysis and suggestions for {user_alias}:\n\n{pgn}"
    elif type =='combined':
         prompt = f"You are a chess grandmaster rated 3200. We are analyzing multiple chess games between {white_player} and other players:\n\n Provide your overall analysis of the player {user_alias} and \
            also recommendations for how they can improve as a player. You don't have to use specific move combinations unless it is to appreciate a checkmate combo or provide missed checkmate combos. \
                 The games could be across different time formats. Keep that into account in your analysis. Focus more on subjective feedback.  Any specific material you can refer them to will also be helpful. :\n\n{pgn}"

    client = OpenAI() 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )
    return str(completion.choices[0].message.content)

def analyze_games(pgn_folder, user_alias):
    """Analyze a batch of chess games and generate an overall analysis."""

    # List to store individual PGNs
    global games_folder
    games_folder = pgn_folder
    individual_pgns = []

    game_data = []

    # Iterate through the PGN files in the folder
    for root, dirs, files in os.walk(pgn_folder):
        for file in files:
            if file.endswith(".pgn"):
                pgn_file_path = os.path.join(root, file)
                with open(pgn_file_path, 'r') as pgn_file:
                    pgn_content = pgn_file.read()
                if pgn_content:
                    game_data.append((pgn_content, file))
                    individual_pgns.append(pgn_content)

    # Define a function to generate analysis for a game
    def generate_analysis(game):
        pgn_content, filename = game
        game = filename.split('.')[0]
        analysis_file = f'{games_folder}/analysis/{game}_analysis.txt'
        if os.path.exists(analysis_file):
            print(f"Analysis for {game} already exists.")
            f = open(analysis_file)
            analysis = f.read()
            f.close()
        else:
            analysis = generate_chess_analysis(pgn_content, user_alias)
            engine_eval = evaluate_game(os.path.join(games_folder, filename))
            eval_file = f'{game}_engine.json'
            analysis_file = game + "_analysis.txt"
            analysis_root = os.path.join(games_folder, 'analysis')
            os.makedirs(analysis_root, exist_ok=True)
            analysis_file_path = os.path.join(analysis_root, analysis_file)
            with open(analysis_file_path, "w") as f:
                    f.write(str(analysis))
            with open(os.path.join(analysis_root, eval_file), 'w') as f:
                    json.dump(engine_eval, f)
            print(f"Analysis for {filename} saved to {analysis_file_path}")
        return filename, analysis

    # Use concurrent.futures to generate analyses concurrently
    num_cores = multiprocessing.cpu_count()
    print(f"Number of available cores --> {num_cores}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores-6) as executor:
        future_to_filename = {executor.submit(generate_analysis, game): game for game in game_data}

        # Wait for all futures to complete
        concurrent.futures.wait(future_to_filename)

        # Write analyses to files concurrently
        for future in concurrent.futures.as_completed(future_to_filename):
            filename, analysis = future.result()
            

    # Combine all individual PGNS into one
    combined_pgn = "\n".join(individual_pgns)

    # Generate an overall analysis for all the games
    overall_analysis = generate_chess_analysis(combined_pgn, user_alias,type='combined')

    # Save the overall analysis to a file
    analysis_folder = os.path.join(pgn_folder, 'analysis')
    overall_analysis_file = os.path.join(analysis_folder, "overall_analysis.txt")
    print(overall_analysis_file)
    with open(overall_analysis_file, "w") as overall_file:
        overall_file.write(str(overall_analysis))

    print(f"Overall analysis for all games saved to {overall_analysis_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Analyze chess games.")
    parser.add_argument("--pgn_folder", required=True, help="Folder containing PGN files to analyze")
    parser.add_argument("--user_alias", required=True, help="User alias for analysis")

    args = parser.parse_args()
    analyze_games(args.pgn_folder, args.user_alias)

if __name__ == "__main__":
    main()

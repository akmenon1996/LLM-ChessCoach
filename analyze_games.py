import os
import argparse
import chess.pgn
import io
from openai import OpenAI
import concurrent.futures
import threading
import multiprocessing

def extract_players_from_pgn(pgn_content):
    """Extract White and Black players from PGN content."""
    game = chess.pgn.read_game(io.StringIO(pgn_content))
    white_player = game.headers.get("White", "Unknown")
    black_player = game.headers.get("Black", "Unknown")
    return white_player, black_player

def generate_chess_analysis(pgn, user_alias):
    """Generate chess game analysis using GPT-3."""
    white_player, black_player = extract_players_from_pgn(pgn)
    prompt = f"You are a chess grandmaster rated 3200. We are analyzing a chess game between {white_player} and {black_player}:\n\nProvide analysis and suggestions for {user_alias}:\n\n{pgn}"

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
        analysis = generate_chess_analysis(pgn_content, user_alias)
        return filename, analysis

    # Use concurrent.futures to generate analyses concurrently
    num_cores = multiprocessing.cpu_count()
    print(f"Number of available cores --> {num_cores}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores-2) as executor:
        future_to_filename = {executor.submit(generate_analysis, game): game for game in game_data}

        # Wait for all futures to complete
        concurrent.futures.wait(future_to_filename)

        # Write analyses to files concurrently
        for future in concurrent.futures.as_completed(future_to_filename):
            filename, analysis = future.result()
            analysis_file = os.path.splitext(filename)[0] + "_analysis.txt"
            analysis_root = os.path.join(root, 'analysis')
            os.makedirs(analysis_root, exist_ok=True)
            analysis_file_path = os.path.join(analysis_root, analysis_file)
            if not os.path.isfile(analysis_file_path):
                with open(analysis_file_path, "w") as f:
                    f.write(str(analysis))
                print(f"Analysis for {filename} saved to {analysis_file_path}")

    # Combine all individual PGNS into one
    combined_pgn = "\n".join(individual_pgns)

    # Generate an overall analysis for all the games
    overall_analysis = generate_chess_analysis(combined_pgn, user_alias)

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
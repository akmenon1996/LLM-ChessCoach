from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from export_lichess_games import ChessGameDownloader
import os
import json
import uuid

app = FastAPI(title="LLM Chess Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

downloader = ChessGameDownloader()

@app.post("/api/analyze")
async def analyze(date: str):
    epoch_time = downloader.date_text_to_epoch(date)
    folder = downloader.fetch_and_save_games(epoch_time)
    username = downloader.config['lichess_user_name']
    downloader.run_analysis(username=username)
    run_id = os.path.basename(folder)
    return {"run_id": run_id}

@app.get("/api/analysis/{run_id}")
async def get_analysis(run_id: str):
    base_dir = os.path.abspath('games')
    analysis_root = os.path.normpath(os.path.join(base_dir, run_id, 'analysis'))
    result = {}
    if not analysis_root.startswith(base_dir):
        # Prevent path traversal
        return {}
    if os.path.exists(analysis_root):
        for file in os.listdir(analysis_root):
            file_path = os.path.normpath(os.path.join(analysis_root, file))
            if not file_path.startswith(analysis_root):
                continue
            with open(file_path) as f:
                result[file] = f.read()
    return result

SCHEDULE_FILE = 'schedules.json'

def load_schedules():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE) as f:
            return json.load(f)
    return []

def save_schedules(data):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(data, f)

@app.post("/api/schedule")
async def add_schedule(date: str, frequency: str):
    schedules = load_schedules()
    schedules.append({'date': date, 'frequency': frequency, 'id': str(uuid.uuid4())})
    save_schedules(schedules)
    return {"status": "scheduled"}

@app.get("/api/dashboard/{username}")
async def dashboard(username: str):
    # Placeholder summary
    schedules = load_schedules()
    return {"username": username, "scheduled_jobs": schedules}


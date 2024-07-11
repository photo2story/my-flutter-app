# git_operations.py
import git
import os,sys
import glob
import shutil
import requests
import pandas as pd
import io
from dotenv import load_dotenv


load_dotenv()

repo_path = os.getenv('GIT_REPO_PATH', '.')
csv_url = 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv'

try:
    repo = git.Repo(repo_path)
except git.exc.InvalidGitRepositoryError:
    print(f'Invalid Git repository at path: {repo_path}')
    repo = None

def fetch_csv_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
        return pd.read_csv(io.StringIO(csv_data))
    except requests.exceptions.RequestException as e:
        print(f'Error fetching CSV data: {e}')
        return None

def move_files_to_images_folder():
    if repo is None:
        print('No valid Git repository. Skipping git operations.')
        return

    patterns = ["*.png", "*.csv"]
    destination_folder = os.path.join('static', 'images')

    df = fetch_csv_data(csv_url)
    if df is not None:
        csv_path = os.path.join(destination_folder, 'stock_market.csv')
        os.makedirs(destination_folder, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"Downloaded CSV to {csv_path}")
    else:
        print("Failed to download CSV data.")

    for pattern in patterns:
        for file in glob.glob(pattern):
            if file != "stock_market.csv":
                shutil.move(file, os.path.join(destination_folder, os.path.basename(file)))
                print(f"Moved {file} to {destination_folder}")

    try:
        repo.git.add(all=True)
        repo.index.commit('Auto-commit moved files')
        origin = repo.remote(name='origin')
        origin.push()
        print('Changes pushed to GitHub')
    except Exception as e:
        print(f'Error during git operations: {e}')

df = fetch_csv_data(csv_url)
if df is not None:
    print(df.head())
else:
    print("Failed to fetch CSV data.")


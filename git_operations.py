# git_operations.py

import git
import os
import glob
import shutil

# 리포지토리 경로 설정
repo_path = '.'  # 현재 디렉토리

# 리포지토리 객체 생성
repo = git.Repo(repo_path)

def move_files_to_images_folder():
    patterns = ["*.png", "*.csv"]
    destination_folder = os.path.join('static', 'images')  # 'app.static_folder' 대신 경로를 명시적으로 설정

    for pattern in patterns:
        for file in glob.glob(pattern):
            if file != "stock_market.csv":
                shutil.move(file, os.path.join(destination_folder, os.path.basename(file)))
                print(f"Moved {file} to {destination_folder}")

    # 파일 이동 후 깃허브 커밋 및 푸시
    try:
        repo.git.add(all=True)  # 모든 변경 사항 추가
        repo.index.commit('Auto-commit moved files')
        origin = repo.remote(name='origin')
        origin.push()
        print('Changes pushed to GitHub')
    except Exception as e:
        print(f'Error during git operations: {e}')

import os
import sys

def setup_kaggle():
    """Check if Kaggle API is setup"""
    token_path = os.path.expanduser("~/.kaggle/kaggle.json")
    return os.path.exists(token_path)

def download_food101():
    """Download Food-101 dataset"""
    try:
        import kagglehub
        path = kagglehub.dataset_download("dansbecker/food-101")
        print(f"Dataset downloaded to: {path}")
        return path
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kagglehub"])
        import kagglehub
        return download_food101()

if __name__ == "__main__":
    print("Food-101 Dataset Downloader")
    
    if not setup_kaggle():
        print("Kaggle API token not found. Setup required.")
        print("See README for Kaggle API setup instructions.")
        sys.exit(1)
    
    download_food101()
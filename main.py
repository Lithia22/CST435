import os
import sys
from datetime import datetime

def setup_results_folder():
    """Create results folder WITHOUT timestamp"""
    results_dir = "results"
    
    import shutil
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    
    os.makedirs(os.path.join(results_dir, "performance_data"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "output_images"), exist_ok=True) 
    
    print(f"Results folder: {results_dir}/")
    return results_dir

def zip_results(results_dir):
    """Automatically zip the results folder"""
    import zipfile
    
    # Simple name: results.zip
    zip_filename = "results.zip"
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(results_dir))
                    zipf.write(file_path, arcname)
        
        print(f"Zip created: {zip_filename}")
        return zip_filename
        
    except Exception:
        return None

def run_all():
    """Run the complete pipeline"""
    print("=" * 60)
    print("PARALLEL IMAGE PROCESSING")
    print("=" * 60)
    
    # Setup results folder
    results_dir = setup_results_folder()
    print(f"📁 Results folder: {results_dir}")
    
    # Check dataset
    dataset_path = "food101_subset"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found: {dataset_path}")
        return
    
    # Run multiprocessing
    sys.path.append('src')
    from src.multiprocessing_impl import run_multiprocessing_experiment
    mp_results = run_multiprocessing_experiment("food101_subset", results_dir=results_dir)
    
    # Run concurrent.futures
    from src.concurrent_futures_impl import run_futures_experiment
    futures_results = run_futures_experiment("food101_subset", results_dir=results_dir)
    
    # Performance analysis
    from src.performance_analysis import plot_comparison
    plot_comparison(mp_results, futures_results, results_dir)
    
    # Auto-zip for easy download
    zip_file = zip_results(results_dir)
    
    if zip_file:
        print(f"\nDownload from GCP: {zip_file}")

if __name__ == "__main__":
    run_all()
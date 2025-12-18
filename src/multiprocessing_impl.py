import os
import time
import glob
from multiprocessing import Pool, cpu_count
from image_filters import ImageProcessor
from pathlib import Path

def process_single_image(image_path):
    """Process a single image with all filters"""
    try:
        processing_time = ImageProcessor.apply_all_filters(
            image_path, 
            output_dir="results/output_images"
        )
        return processing_time
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return 0

def multiprocessing_pipeline(image_folder, num_processes=None):
    """
    Process all images using multiprocessing.Pool
    """
    # Get all image paths
    image_extensions = ['*.jpg', '*.jpeg', '*.png']
    image_paths = []
    
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(image_folder, '**', ext), recursive=True))
    
    print(f"Found {len(image_paths)} images to process")
    
    # Set number of processes (default to CPU count)
    if num_processes is None:
        num_processes = cpu_count()
    
    # Create output directory
    Path("results/output_images").mkdir(parents=True, exist_ok=True)
    
    # Start timing
    start_time = time.time()
    
    # Create pool and process images
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_single_image, image_paths)
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Calculate statistics
    total_processing_time = sum(results)
    avg_time_per_image = total_processing_time / len(results) if results else 0
    
    print(f"\n=== Multiprocessing Results ===")
    print(f"Number of processes: {num_processes}")
    print(f"Total images processed: {len(image_paths)}")
    print(f"Total wall-clock time: {total_time:.2f} seconds")
    print(f"Total processing time (sum): {total_processing_time:.2f} seconds")
    print(f"Average time per image: {avg_time_per_image:.2f} seconds")
    
    return {
        'num_processes': num_processes,
        'num_images': len(image_paths),
        'total_time': total_time,
        'processing_times': results
    }

def run_multiprocessing_experiment(image_folder, process_counts=None):
    """
    Run multiprocessing with different process counts
    """
    if process_counts is None:
        process_counts = [1, 2, 4, 8]
    
    results = {}
    
    for num_procs in process_counts:
        print(f"\n{'='*50}")
        print(f"Running with {num_procs} processes...")
        print('='*50)
        
        result = multiprocessing_pipeline(image_folder, num_procs)
        results[num_procs] = result
        
        # Small delay between runs
        time.sleep(2)
    
    return results

if __name__ == "__main__":
    # Test with your dataset
    dataset_path = "food101_subset"
    if os.path.exists(dataset_path):
        results = run_multiprocessing_experiment(dataset_path)
        
        # Save results for later analysis
        import json
        Path("results/performance_data").mkdir(parents=True, exist_ok=True)
        with open('results/performance_data/multiprocessing_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("Results saved to: results/performance_data/multiprocessing_results.json")
    else:
        print(f"Dataset path '{dataset_path}' not found!")
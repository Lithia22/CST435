import os
import time
import glob
import concurrent.futures
from image_filters import ImageProcessor
from pathlib import Path
import multiprocessing

def process_single_image_futures(image_path):
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

def futures_pipeline(image_folder, num_workers=None):
    """
    Process all images using concurrent.futures ProcessPoolExecutor
    """
    # Get all image paths
    image_extensions = ['*.jpg', '*.jpeg', '*.png']
    image_paths = []
    
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(image_folder, '**', ext), recursive=True))
    
    print(f"Found {len(image_paths)} images to process")
    
    # Set number of workers (default to CPU count)
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    # Create output directory
    Path("results/output_images").mkdir(parents=True, exist_ok=True)
    
    # Start timing
    start_time = time.time()
    
    # Use ProcessPoolExecutor for parallel processing
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        future_to_image = {
            executor.submit(process_single_image_futures, img_path): img_path 
            for img_path in image_paths
        }
        
        # Collect results as they complete
        results = []
        for future in concurrent.futures.as_completed(future_to_image):
            img_path = future_to_image[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Image {img_path} generated exception: {e}")
                results.append(0)
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Calculate statistics
    total_processing_time = sum(results)
    avg_time_per_image = total_processing_time / len(results) if results else 0
    
    print(f"\n=== Concurrent.Futures Results ===")
    print(f"Number of workers: {num_workers}")
    print(f"Total images processed: {len(image_paths)}")
    print(f"Total wall-clock time: {total_time:.2f} seconds")
    print(f"Total processing time (sum): {total_processing_time:.2f} seconds")
    print(f"Average time per image: {avg_time_per_image:.2f} seconds")
    
    return {
        'num_workers': num_workers,
        'num_images': len(image_paths),
        'total_time': total_time,
        'processing_times': results
    }

def run_futures_experiment(image_folder, worker_counts=None):
    """
    Run concurrent.futures with different worker counts
    """
    if worker_counts is None:
        worker_counts = [1, 2, 4, 8]
    
    results = {}
    
    for num_workers in worker_counts:
        print(f"\n{'='*50}")
        print(f"Running with {num_workers} workers...")
        print('='*50)
        
        result = futures_pipeline(image_folder, num_workers)
        results[num_workers] = result
        
        # Small delay between runs
        time.sleep(2)
    
    return results

if __name__ == "__main__":
    # Test with your dataset
    dataset_path = "food101_subset"
    
    if os.path.exists(dataset_path):
        results = run_futures_experiment(dataset_path)
        
        # Save results for later analysis
        import json
        Path("results/performance_data").mkdir(parents=True, exist_ok=True)
        with open('results/performance_data/futures_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("Results saved to: results/performance_data/futures_results.json")
    else:
        print(f"Dataset path '{dataset_path}' not found!")
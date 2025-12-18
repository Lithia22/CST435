import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

class ImageProcessor:
    @staticmethod
    def apply_grayscale(image_path):
        """Convert RGB image to grayscale using luminance formula"""
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # Luminance formula: Y = 0.299*R + 0.587*G + 0.114*B
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray
    
    @staticmethod
    def apply_gaussian_blur(image_path):
        """Apply 3x3 Gaussian kernel for smoothing"""
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # 3x3 Gaussian kernel
        blurred = cv2.GaussianBlur(img, (3, 3), 0)
        return blurred
    
    @staticmethod
    def apply_edge_detection(image_path):
        """Sobel filter for edge detection"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        
        # Sobel operators
        sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate magnitude
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        magnitude = np.uint8(np.clip(magnitude, 0, 255))
        
        return magnitude
    
    @staticmethod
    def apply_sharpening(image_path):
        """Enhance edges and details"""
        img = Image.open(image_path)
        
        # Using PIL's filter
        sharpened = img.filter(ImageFilter.SHARPEN)
        
        # Convert back to numpy array for consistency
        sharpened_np = np.array(sharpened)
        
        # If grayscale, convert to 3-channel
        if len(sharpened_np.shape) == 2:
            sharpened_np = cv2.cvtColor(sharpened_np, cv2.COLOR_GRAY2BGR)
        
        return sharpened_np
    
    @staticmethod
    def apply_brightness_adjustment(image_path, factor=1.5):
        """Increase or decrease image brightness"""
        img = Image.open(image_path)
        
        # Adjust brightness
        enhancer = ImageEnhance.Brightness(img)
        brightened = enhancer.enhance(factor)  # >1 brighter, <1 darker
        
        # Convert to numpy array
        brightened_np = np.array(brightened)
        
        # If grayscale, convert to 3-channel
        if len(brightened_np.shape) == 2:
            brightened_np = cv2.cvtColor(brightened_np, cv2.COLOR_GRAY2BGR)
        
        return brightened_np
    
    @staticmethod
    def apply_all_filters(image_path, output_dir="processed"):
        """
        Apply all 5 filters sequentially to one image
        Returns processing time
        """
        import time
        
        start_time = time.time()
        
        # Apply each filter
        gray = ImageProcessor.apply_grayscale(image_path)
        blurred = ImageProcessor.apply_gaussian_blur(image_path)
        edges = ImageProcessor.apply_edge_detection(image_path)
        sharpened = ImageProcessor.apply_sharpening(image_path)
        brightened = ImageProcessor.apply_brightness_adjustment(image_path)
        
        # Save results
        if output_dir:
            import os
            from pathlib import Path
            
            # Create output directory
            Path(output_dir).mkdir(exist_ok=True)
            
            # Get filename without extension
            filename = Path(image_path).stem
            
            # Save each filtered image
            cv2.imwrite(f"{output_dir}/{filename}_gray.jpg", gray)
            cv2.imwrite(f"{output_dir}/{filename}_blurred.jpg", blurred)
            cv2.imwrite(f"{output_dir}/{filename}_edges.jpg", edges)
            cv2.imwrite(f"{output_dir}/{filename}_sharpened.jpg", sharpened)
            cv2.imwrite(f"{output_dir}/{filename}_brightened.jpg", brightened)
        
        end_time = time.time()
        return end_time - start_time
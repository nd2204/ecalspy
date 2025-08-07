import cv2
import numpy as np
import matplotlib.pyplot as plt

def Preprocess(pilImg):
    img = np.array(pilImg)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Blue range (tweak if needed)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Keep only blue parts
    result = cv2.bitwise_and(img, img, mask=mask)

    # Convert to grayscale
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # Light denoising
    gray = cv2.medianBlur(gray, 3)

    # Binarize
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh

def preprocess_image_for_ocr(pilImg, output_path=None, show_steps=True):
    """
    Preprocess an image for better OCR results

    Args:
        image: PIL Image
        output_path: Path to save processed image (optional)
        show_steps: Whether to display preprocessing steps

    Returns:
        Preprocessed image ready for OCR
    """

    img = np.array(pilImg)
    original = img.copy()

    if show_steps:
        plt.figure(figsize=(15, 12))
        plt.subplot(3, 4, 1)
        plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')
        plt.axis('off')

    # Step 1: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if show_steps:
        plt.subplot(3, 4, 2)
        plt.imshow(gray, cmap='gray')
        plt.title('Grayscale')
        plt.axis('off')

    # Step 2: Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    if show_steps:
        plt.subplot(3, 4, 3)
        plt.imshow(enhanced, cmap='gray')
        plt.title('CLAHE Enhanced')
        plt.axis('off')

    # Step 3: Gentle noise reduction with bilateral filter (preserves edges better)
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)

    if show_steps:
        plt.subplot(3, 4, 4)
        plt.imshow(denoised, cmap='gray')
        plt.title('Bilateral Filter')
        plt.axis('off')

    # Step 4: Adaptive thresholding (better for varying lighting)
    adaptive_thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )

    if show_steps:
        plt.subplot(3, 4, 5)
        plt.imshow(adaptive_thresh, cmap='gray')
        plt.title('Adaptive Threshold')
        plt.axis('off')

    # Step 5: Remove small noise components
    # Find connected components and remove small ones
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        255 - adaptive_thresh, connectivity=4
    )

    # Create a mask for components larger than a minimum size
    min_size = 10  # Minimum component size
    mask = np.zeros_like(adaptive_thresh)

    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            mask[labels == i] = 255

    # Apply the mask
    cleaned = cv2.bitwise_and(adaptive_thresh, mask)

    if show_steps:
        plt.subplot(3, 4, 6)
        plt.imshow(cleaned, cmap='gray')
        plt.title('Noise Removed')
        plt.axis('off')

    # Step 6: Morphological operations to connect broken characters
    # Use a smaller kernel for gentle operations
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 1))
    closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close, iterations=1)

    # Fill small gaps in horizontal direction (good for text)
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
    dilated = cv2.dilate(closed, kernel_dilate, iterations=1)
    eroded = cv2.erode(dilated, kernel_dilate, iterations=1)

    if show_steps:
        plt.subplot(3, 4, 7)
        plt.imshow(eroded, cmap='gray')
        plt.title('Morphological Ops')
        plt.axis('off')

    # Step 7: Ensure proper contrast (black text on white background)
    # Count black vs white pixels to determine if inversion is needed
    black_pixels = np.sum(eroded == 0)
    white_pixels = np.sum(eroded == 255)

    if black_pixels > white_pixels:
        final = cv2.bitwise_not(eroded)
        inversion_applied = True
    else:
        final = eroded
        inversion_applied = False

    if show_steps:
        plt.subplot(3, 4, 8)
        plt.imshow(final, cmap='gray')
        plt.title(f'Contrast Fixed {"(Inverted)" if inversion_applied else ""}')
        plt.axis('off')

    # Step 8: Resize for better OCR (if image is too small)
    height, width = final.shape
    if height < 50 or width < 200:
        # Calculate scale factor to get reasonable size
        scale_factor = max(3, 200 // width, 50 // height)
        final = cv2.resize(final, None, fx=scale_factor, fy=scale_factor, 
                          interpolation=cv2.INTER_CUBIC)

    if show_steps:
        plt.subplot(3, 4, 9)
        plt.imshow(final, cmap='gray')
        plt.title(f'Resized ({final.shape[1]}x{final.shape[0]})')
        plt.axis('off')

        # Show original vs final comparison
        plt.subplot(3, 4, 10)
        plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        plt.title('Original')
        plt.axis('off')

        plt.subplot(3, 4, 11)
        plt.imshow(final, cmap='gray')
        plt.title('Final Result')
        plt.axis('off')

        plt.tight_layout()
        plt.show()

    # Save processed image if output path provided
    if output_path:
        cv2.imwrite(output_path, final)
        print(f"Processed image saved to: {output_path}")

    return final

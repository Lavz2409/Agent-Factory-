import logging
from typing import Dict, Any
import numpy as np
import cv2

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TraceAI")

def initialize_logger(name: str) -> logging.Logger:
    """Initialize and return a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def load_image(image_path: str) -> np.ndarray:
    """Load an image from the given path."""
    logger.info(f"Loading image from path: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Failed to load image from path: {image_path}")
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    return image

def resize_image(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize the image to the given width and height."""
    logger.info(f"Resizing image to width: {width}, height: {height}")
    resized_image = cv2.resize(image, (width, height))
    return resized_image

def convert_image_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert the image to grayscale."""
    logger.info("Converting image to grayscale")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def extract_faces(image: np.ndarray, face_cascade_path: str) -> list:
    """Detect and extract faces from the image using a Haar cascade."""
    logger.info("Extracting faces from image")
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    gray_image = convert_image_to_grayscale(image)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    logger.info(f"Detected {len(faces)} faces")
    return faces

def log_analysis_results(results: Dict[str, Any]) -> None:
    """Log the results of the analysis."""
    logger.info("Logging analysis results")
    for key, value in results.items():
        logger.info(f"{key}: {value}")

def validate_data(data: Dict[str, Any], required_keys: list) -> bool:
    """Validate that the data contains all required keys."""
    logger.info("Validating data")
    for key in required_keys:
        if key not in data:
            logger.error(f"Missing required key: {key}")
            return False
    return True

def calculate_accuracy(true_positives: int, false_positives: int, false_negatives: int) -> float:
    """Calculate the accuracy of the model."""
    logger.info("Calculating accuracy")
    total_predictions = true_positives + false_positives + false_negatives
    if total_predictions == 0:
        logger.warning("No predictions made, returning 0 accuracy")
        return 0.0
    accuracy = true_positives / total_predictions
    logger.info(f"Calculated accuracy: {accuracy}")
    return accuracy
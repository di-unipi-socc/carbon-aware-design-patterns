import cv2
import os

class Request:
    def __init__(self, image_name:str):
        image_path = os.path.join("immagini",image_name)
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Immagine non trovata: {image_path}")
        self.path= image_path
        self.n_applied_filters=0
        self.applied_filters= []
        self.image= cv2.imread(self.path)
        self.original_image= self.image.copy()
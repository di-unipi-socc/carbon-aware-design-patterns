from handler import Filter
from request import Request
import cv2
import numpy as np
import mediapipe as mp

class Blur(Filter):
    _next_handler:Filter=None
    blur_intensity = 51

    def __init__(self):
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentator = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=0)
    
    def apply_filter(self, request:Request):
        rgb_image = cv2.cvtColor(request.image, cv2.COLOR_BGR2RGB)
        result = self.segmentator.process(rgb_image)
        mask = result.segmentation_mask
        blur_background = cv2.GaussianBlur(request.image,(self.blur_intensity,self.blur_intensity),0)
        condition = np.stack((mask,) * 3, axis=-1) > 0.1
        composed_image = np.where(condition,request.image,blur_background)
        request.image =composed_image
        request.n_applied_filters+=1
        request.applied_filters.append("blur")
    
        if self._next_handler is not None:
            return self._next_handler.apply_filter(request)

        return request

    def set_next(self, handler):
        self._next_handler=handler
        return handler
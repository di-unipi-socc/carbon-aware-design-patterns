from handler import Filter
from request import Request
import cv2
import numpy as np
import mediapipe as mp
import time

class Blur(Filter):
    _next_handler:Filter=None
    blur_intensity = 51
    avg_time = 0.07781479199999011
    def __init__(self):
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentator = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=0)
    
    def apply_filter(self, request:Request,co2:float,budgetco2:float,total_cost:float):
        average_cost= co2 * 0.05 * (self.avg_time/3600)
        if budgetco2 >= average_cost:
            start_time = time.perf_counter()
            rgb_image = cv2.cvtColor(request.image, cv2.COLOR_BGR2RGB)
            result = self.segmentator.process(rgb_image)
            mask = result.segmentation_mask
            blur_background = cv2.GaussianBlur(request.image,(self.blur_intensity,self.blur_intensity),0)
            condition = np.stack((mask,) * 3, axis=-1) > 0.1
            composed_image = np.where(condition,request.image,blur_background)
            request.image =composed_image
            end_time = time.perf_counter()
            request.n_applied_filters+=1
            request.applied_filters.append("blur")
            total_time = end_time-start_time
            actual_cost = co2 * 0.05 * (total_time/3600)
            budgetco2 -= actual_cost
            total_cost+= actual_cost

        if self._next_handler is not None:
            return self._next_handler.apply_filter(request,co2,budgetco2,total_cost)

        return request

    def set_next(self, handler):
        self._next_handler=handler
        return handler
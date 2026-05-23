from handler import Filter
from request import Request
import cv2
import numpy as np
import mediapipe as mp


class Relighting(Filter):
    _next_handler:Filter=None
    
    def __init__(self):
        self.light_intensity= 1.4
        self.face_detection= mp.solutions.face_detection
        self.detector = self.face_detection.FaceDetection(model_selection=0,min_detection_confidence=0.5)

    def apply_filter(self,request:Request):
        rgb_image = cv2.cvtColor(request.image, cv2.COLOR_BGR2RGB)
        height, width, _ = request.image.shape

        result = self.detector.process(rgb_image)
        light_mask = np.zeros((height, width), dtype=np.uint8)
        face = result.detections[0]
        bbox = face.location_data.relative_bounding_box
        x_min = int(bbox.xmin * width)
        y_min = int(bbox.ymin * height)
        w = int(bbox.width * width)
        h = int(bbox.height * height)

        center_x = x_min + (w // 2)
        center_y = y_min + (h // 2)
        radius = int(w * 1.5)

        cv2.circle(light_mask, (center_x, center_y), radius, 255, -1)

        blur_size = radius | 1 # trucco bit-a-bit per assicurarsi che sia dispari
        if blur_size < 3: blur_size = 3
        light_mask = cv2.GaussianBlur(light_mask, (blur_size, blur_size), 0)

        mask_float = light_mask.astype(float) / 255.0
        mask_float = np.stack((mask_float,) * 3, axis=-1)
        lighted_image = cv2.convertScaleAbs(request.image, alpha=self.light_intensity, beta=15)
        final_image = (lighted_image * mask_float) + (request.image * (1.0 - mask_float))
        request.image = final_image.astype(np.uint8)
        request.n_applied_filters += 1
        request.applied_filters.append("relighting")
        if self._next_handler is not None:
            return self._next_handler.apply_filter(request)
        
        return request

    def set_next(self, handler):
        self._next_handler=handler
        return handler
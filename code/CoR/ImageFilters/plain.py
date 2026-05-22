import time
import cv2
from request import Request
import numpy as np
import mediapipe as mp

class Plain():
    def __init__(self):
        self.social_w=1152
        self.social_h=2048
        self.increase = 20
        self.blur_intensity = 51
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentator = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=0)
        self.light_intensity= 1.4
        self.face_detection= mp.solutions.face_detection
        self.detector = self.face_detection.FaceDetection(model_selection=0,min_detection_confidence=0.5)


    def apply_filter(self,req:Request):

        self.apply_resolution(req)
        self.apply_saturation(req)
        self.apply_blur(req)
        self.apply_relighting(req)

        return req


    def apply_resolution(self,request:Request):
        height,width,_ = request.image.shape

        ratio_w= self.social_w/width
        ratio_h= self.social_h/height
        max_ratio = max(ratio_w,ratio_h)

        new_w = int(width*max_ratio)
        new_h = int(height*max_ratio)
        
        scaled_image= cv2.resize(request.image,(new_w,new_h))

        x_start= (new_w -self.social_w) // 2
        y_start= (new_h -self.social_h) // 2

        x_end= x_start + self.social_w
        y_end = y_start + self.social_h

        request.image = scaled_image[y_start:y_end,x_start:x_end]
        return request
    
    def apply_saturation(self,request:Request):
        hsv_image = cv2.cvtColor(request.image,cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv_image)
        s_increased= cv2.add(s,self.increase)

        hsv_image_modified = cv2.merge([h,s_increased,v])
        request.image= cv2.cvtColor(hsv_image_modified,cv2.COLOR_HSV2BGR)
        return request
    
    def apply_blur(self,request:Request):
        rgb_image = cv2.cvtColor(request.image, cv2.COLOR_BGR2RGB)
        result = self.segmentator.process(rgb_image)
        mask = result.segmentation_mask
        blur_background = cv2.GaussianBlur(request.image,(self.blur_intensity,self.blur_intensity),0)
        condition = np.stack((mask,) * 3, axis=-1) > 0.1
        composed_image = np.where(condition,request.image,blur_background)
        request.image =composed_image
        return request
    
    def apply_relighting(self,request:Request):
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

            return request
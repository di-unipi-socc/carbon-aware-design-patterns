from handler import Filter
from request import Request
import cv2
import numpy as np
import time

class Saturation(Filter):
    _next_handler:Filter=None
    increase = 20

    def apply_filter(self,request:Request):

        hsv_image = cv2.cvtColor(request.image,cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv_image)
        s_increased= cv2.add(s,self.increase)

        hsv_image_modified = cv2.merge([h,s_increased,v])
        request.image= cv2.cvtColor(hsv_image_modified,cv2.COLOR_HSV2BGR)
        request.n_applied_filters += 1
        request.applied_filters.append("saturation")
        if self._next_handler is not None:
            return self._next_handler.apply_filter(request)

        
        return request

    def set_next(self, handler):
        self._next_handler=handler
        return handler
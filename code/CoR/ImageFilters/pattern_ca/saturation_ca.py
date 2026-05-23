from handler import Filter
from request import Request
import cv2
import numpy as np
import time

class Saturation(Filter):
    _next_handler:Filter=None
    increase = 20
    avg_time = 0.02017406800005119

    def apply_filter(self,request:Request,co2:float,budgetco2:float,total_cost:float):
        average_cost= co2 * 0.05 * (self.avg_time/3600)
        if budgetco2 >= average_cost:
            start_time = time.perf_counter()
            hsv_image = cv2.cvtColor(request.image,cv2.COLOR_BGR2HSV)
            h,s,v = cv2.split(hsv_image)
            s_increased= cv2.add(s,self.increase)

            hsv_image_modified = cv2.merge([h,s_increased,v])
            request.image= cv2.cvtColor(hsv_image_modified,cv2.COLOR_HSV2BGR)
            end_time = time.perf_counter()
            request.n_applied_filters += 1
            request.applied_filters.append("saturation")
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
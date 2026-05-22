from handler import Filter
from request import Request
import cv2
import time

class Resolution(Filter):
    _next_handler:Filter=None
    social_w=1152
    social_h=2048

    def apply_filter(self, request: Request):
        height,width,_ = request.image.shape

        if (width != self.social_w) or (height != self.social_h):
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
            request.n_applied_filters+=1
            request.applied_filters.append("resolution")

        
        if self._next_handler is not None:
            return self._next_handler.apply_filter(request)


        return request
        



    def set_next(self, handler):
        self._next_handler=handler
        return handler
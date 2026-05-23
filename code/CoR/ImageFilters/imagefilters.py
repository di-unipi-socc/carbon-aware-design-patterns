import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore", category=UserWarning)

from filter_ca import filter_ca
from carbonprovider import CarbonProvider
from request import Request
import cv2





def main():
    immagine = f"immagine{i}.jpeg"
    req= Request(immagine)
    provider = CarbonProvider()
    co2intensity = provider.get_co2()
    budget = None
    processedimage = filter_ca(req,co2intensity,budget)
    
    return

if __name__ == "__main__":
    main()
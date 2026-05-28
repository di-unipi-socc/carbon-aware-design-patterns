import os
import argparse
import warnings
import cv2

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore", category=UserWarning)

from filter_ca import filter_ca
from carbonprovider import CarbonProvider
from request import Request

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

def main():
    parser = argparse.ArgumentParser(description="Demo Image Filters")
    parser.add_argument("--image", type=str, default="immagine1", help="Nome dell'immagine (senza .jpeg)")
    parser.add_argument("--co2", type=float, default=270.0, help="Livello di CO2 attuale")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    immagine_file = f"{args.image}.jpeg"
    img_path = os.path.join(DATA_DIR, "immagini", immagine_file)
    
    print(f" Avvio ImageFilters -> Immagine: {immagine_file} | CO2: {args.co2}")
    
    req = Request(img_path)
    provider = CarbonProvider()
    provider.set_co2(args.co2)
    
    print("Applicazione filtri in corso...")
    processedimage = filter_ca(req, args.co2, 0.8)
    print(type(processedimage))
    
    if processedimage.image is not None:
        out_path = os.path.join(OUTPUT_DIR, f"processed_{immagine_file}")
        cv2.imwrite(out_path, processedimage.image)
        print(f"Filtri applicati! Immagine salvata in: {out_path}")
    else:
        print("Impossibile elaborare l'immagine.")

if __name__ == "__main__":
    main()
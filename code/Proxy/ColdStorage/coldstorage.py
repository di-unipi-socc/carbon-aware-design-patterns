import threading
from generator import generator
import time
from coldstorage_ca import ColdStorage_ca
from coldstorage_realservice import ColdStorage_RealService
from carbonprovider import CarbonProvider
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import sys
from plain import Plain

def main():
    t1=threading.Thread(target=generator,daemon=True)
    t1.start()
    provider = CarbonProvider()
    provider.set_co2(100.0)
    service = ColdStorage_RealService()
    proxy_ca= ColdStorage_ca(service,provider,300.0)
    try:
        while True:
            operazione, sensore_a, sensore_b =None
            if operazione =='esci':
                break
            match operazione:
                case "correlazione":
                    print(f"------------------------------\n")
                    correlazione_ca=proxy_ca.calculate_correlation(operazione,sensore_a,sensore_b)
                    print(f"------------------------------\n")
                case "anomalie":
                    anomalia= proxy_ca.calculate_anomaly(operazione,sensore_a)
                    print(anomalia)
    except KeyboardInterrupt:
        print('Chiusura')


if __name__ == "__main__":
    main()

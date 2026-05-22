import datetime
from database import DataBase
from database_handler import DatabaseHandler
from carbonprovider import CarbonProvider
from real_resumer import Resumer_RealService
from proxy_resumer_ca import Resumer_CarbonAware
from document_resume import Document_resume


def main():

    provider = CarbonProvider()
    provider.set_co2_attuale(datetime.datetime.now(),100.0)

    orarioforecast = datetime.datetime.now() + datetime.timedelta(seconds=30)
    provider.set_forecast(time=orarioforecast, intensity=100.0)


    real_resumer = Resumer_RealService()
    proxy_resumer = Resumer_CarbonAware(real_resumer,provider,co2_threshold=250)
    db = DataBase()
    db_handler = DatabaseHandler(proxy_resumer,db)

    while True:
        fatto = False
        while not fatto:
            orarioforecast = datetime.datetime.now() + datetime.timedelta(seconds=30)
            provider.set_forecast(time=orarioforecast, intensity=100.0)
            book = input ("inserisci il libro da riassumere")
            author = input ("inserisci l'autore")
            resume = db_handler.get_resume(book,author)

            print(f"{resume}")

if __name__ == "__main__":
    main()
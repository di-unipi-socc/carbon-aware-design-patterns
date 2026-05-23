import time
import csv
import datetime
import random
import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "database.csv")

def generator():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    while True:
        time.sleep(1)
        temp_door=generate_temp_port()
        temp_bot=generate_temp_fond(temp_door)
        um=generate_um(temp_door)
        cons=generate_cons(temp_door)
        with open(DB_FILE, mode='a', newline='') as database:
            datawriter = csv.writer(database, delimiter=';')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datawriter.writerow([timestamp, temp_door, temp_bot, um, cons])

def generate_temp_port():
    prob= random.random()
    if prob < 0.02 :
        temp= round(random.uniform(12,22),1)
    else:
        temp= round(random.uniform(0,6),1)
    return temp

def generate_temp_fond(td):
    tf_base = td - random.uniform(0.5, 1.5)
    prob = random.random()
    if prob < 0.01:
        tf = round(random.uniform(12, 22), 1)
    else:
        tf = tf_base
    return round(tf, 1)

def generate_um(td):
    um_base = 90.0 - (td * 1.5)
    um = round(um_base + random.uniform(-2.0, 2.0),1)
    prob = random.random()
    if prob < 0.02:
        um= round(random.uniform(10,50),1)
    elif prob < 0.01:
        um = round(random.uniform(96,100),1)
    
    return um

def generate_cons(td):
    cons_base = 0.5 + (td * 0.15)
    cons = round(cons_base + random.uniform(-0.1, 0.1),2)
    prob= random.random()
    if prob < 0.02:
        cons = round(random.uniform(4.5,6.5),2)
    return cons

if __name__ == "__main__":
    generator()
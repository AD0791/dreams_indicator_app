import pymysql
from sqlalchemy import create_engine, text
from decouple import config
from dotenv import load_dotenv
import pandas as pd
from numpy import int16
from enum import Enum

#from functions import *
load_dotenv()

# get the environment variables needed
USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')


class Set_date(Enum):
    master_start = "2017-10-01"
    master_end = "2021-11-31"
    period_start = "2021-10-01"
    period_end = "2021-12-31"


# get the engine to connect and fetch
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}")

v21 = open('../v21_script.sql')
v21_text = text(v21.read())
v21_data = engine.execute(v21_text).fetchall()

print(v21_data)

engine.dispose()


from decouple import config
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pandas import (
    read_sql_query
)


load_dotenv()

USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')


engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}"
)


query = """
SELECT 
    vhs.*,
    vhs.a7_score + vhs.12_score + vhs.12a_score + vhs.12b_score + vhs.14a_score + vhs.15a_score AS total_score
FROM
    caris_db.view_hts_score vhs; 
"""


hts_screening = read_sql_query(query, engine,parse_dates=True)

















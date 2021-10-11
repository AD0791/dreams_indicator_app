from numpy import int16
from components.ovc_actif import actif_in_Q3Q4, actif_in_Q3strict, actif_in_Q4strict, actif_in_Q3, actif_in_Q4
from pandas import concat
from datetime import datetime
date_du_jour = datetime.today().strftime("%d_%m_%Y")

if not ((actif_in_Q3.id_patient.count() == actif_in_Q3Q4.id_patient.count() + actif_in_Q3strict.id_patient.count()) and (actif_in_Q4.id_patient.count() == actif_in_Q3Q4.id_patient.count() + actif_in_Q4strict.id_patient.count())):
    raise ValueError("Qi <> Qistrict + QiQj, bad logic")
else:
    print("the logic  Qi = Qistrict + QiQj is valid")
    
#### Q4served&enroled + Q3Q4served 

completed_Q4strict =  actif_in_Q4strict[actif_in_Q4strict.complete_at_least=="yes"]
completed_Q3strict =  actif_in_Q3strict[actif_in_Q3strict.complete_at_least=="yes"]
completed_Q3Q4 =  actif_in_Q3Q4[actif_in_Q3Q4.complete_at_least=="yes"]

enrolledQ4_CQ4strict = completed_Q4strict[completed_Q4strict.isEnrolledQ4=="yes"]
enrolledQ4_CQ3strict = completed_Q3strict[completed_Q3strict.isEnrolledQ4=="yes"]
enrolledQ4_CQ3Q4 = completed_Q3Q4[completed_Q3Q4.isEnrolledQ4=="yes"]

all_ovc = concat([completed_Q3Q4,enrolledQ4_CQ4strict])
all_ovc.drop_duplicates("id_patient",inplace=True)
all_ovc.test_results.fillna("0,",inplace=True)

####### OVC_SERV 

ovc_data = all_ovc[
    (all_ovc.test_results!="0,,3,")&
    (all_ovc.test_results!="0,,1,,2,")&
    (all_ovc.test_results!="0,,2,,3,")&
    (all_ovc.test_results!="3,")&
    (all_ovc.test_results!="2,,3,")
]

### key object
positive_dreams= ovc_data[
    (ovc_data.test_results=="1,")|
    (ovc_data.test_results=="0,,1,")
]

### key object
ovcS_dreams = ovc_data[
    (ovc_data.ovc_age=="10-14")|
    (ovc_data.ovc_age=="15-17")
]

ovcS_dreams['Gender'] = "Female"

datim_ovc_dreams = ovcS_dreams.pivot_table(index="commune",values="id_patient",columns=["Gender","ovc_age"],aggfunc='count',fill_value=0)
datim_ovc_dreams[('Female','<1')] = 0
datim_ovc_dreams[('Female','1-4')] = 0
datim_ovc_dreams[('Female','5-9')] = 0
datim_ovc_dreams[('Female','18+')] = 0

columns_orientation =[
    ('Female','<1'),
    ('Female','1-4'),
    ('Female','5-9'),
    ('Female','10-14'),
    ('Female','15-17'),   
    ('Female','18+'),   
]

### key object
datim_ovc_dreams = datim_ovc_dreams.reindex(columns= columns_orientation)



##### regime script
import pymysql
from sqlalchemy import create_engine
from decouple import config
from dotenv import load_dotenv
from pandas import to_datetime, read_sql_query

load_dotenv()
USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}")

regim_query=""" 
SELECT
        p.patient_code, id_patient,
            MIN(IF(start_date != '0000-00-00', start_date, NULL)) AS start_date,
            GROUP_CONCAT(la.acronym
                SEPARATOR '-') AS regime,
            GROUP_CONCAT(tr.start_date
                SEPARATOR ' | ') AS all_start_date,
            GROUP_CONCAT(tr.end_date
                SEPARATOR ' | ') AS all_end_date
    FROM
        tracking_regime tr
LEFT JOIN patient p ON p.id = tr.id_patient
    LEFT JOIN lookup_arv la ON la.id = tr.id_arv
    WHERE
        category = 'regime_infant_treatment' and tr.end_date='0000-00-00'
    GROUP BY id_patient
"""

regime_status = read_sql_query(regim_query, engine)

engine.dispose()




from cgfunc import ovc_age, gender, age_to_correct
from decouple import config
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pymysql
from core.agyw import AgywPrev
from pandas import read_excel, Int32Dtype, read_sql_query
#from sys import path
#path.insert(0, '../core')


# Gender, place code at first, age_paran, commune
parent_fap = read_excel(
    './commcare/FòmAnrejistremanPatisipan_2022_06_15.xlsx')
parent_fap.age_paran = parent_fap.age_paran.astype(Int32Dtype())
parent_fap.age_paran.fillna(-1, inplace=True)
parent_fap['age_ovc'] = parent_fap.age_paran.map(ovc_age)
parent_fap['age_status'] = parent_fap.age_paran.map(age_to_correct)
parent_fap.Gender = parent_fap.Gender.map(gender)

parents = parent_fap[['code', 'non_paran_responsab',
                      'Gender', 'commune', 'age_paran', 'age_ovc', 'age_status']]


# parenting served in the Quarter
datim = AgywPrev()
base = datim.data_dreams_valid

parenting_leastone = base[
    (base.parenting_detailed != "no")
]

parenting_completed = base[
    (base.parenting_detailed == "yes")
]


id_parent_served = parenting_leastone[[
    'id_patient', 'nbre_parenting_coupe_present']]

id_parent_completed = parenting_completed[[
    'id_patient',
    'nbre_parenting_coupe_present'
]]


# All dreams people
load_dotenv()
# get the environment variables needed
USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')

# get the engine to connect and fetch
engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}")
query = '''
SELECT 
    dm.id_patient as id_patient,
    d.case_id,
    p.patient_code AS code,
    d.a_non_patisipan_an AS first_name,
    d.b_siyati AS last_name,
    TIMESTAMPDIFF(YEAR,
        d.nan_ki_dat_ou_fet,
        now()) AS age,
    d.nan_ki_dat_ou_fet AS dob,
    d.a1_dat_entvyou_a_ft_jjmmaa_egz_010817 AS interview_date,
    d.e__telefn,
    d.d_adrs AS adress,
    IF(dm.id IS NOT NULL, 'yes', 'no') AS already_in_a_group,
    dm.id_group AS actual_id_group,
    dg.name AS actual_group_name,
    dm.id_parenting_group AS actual_id_parenting_group,
    dpg.name AS actual_parenting_group_name,
    dh.name AS actual_hub,
    ld.name AS actual_departement,
    d.f_komin AS commune,
    d.g_seksyon_kominal AS commune_section,
    d.b1_non_moun_mennen_entvyou_a AS interviewer_firstname,
    d.c1_siyati_moun_ki_f_entvyou_a AS interviewer_lastname,
    d.d1_kad AS interviewer_role,
    d.lot_kad AS interviewer_other_info,
    d.h_kote_entvyou_a_ft AS interview_location,
    d.paran_ou_vivan AS is_your_parent_alive,
    d.i_non_manman AS mothers_name,
    d.j_non_papa AS fathers_name,
    d.k_reskonsab_devan_lalwa AS who_is_your_law_parent,
    d.total,
    d.organisation
FROM
    caris_db.dreams_surveys_data d
        LEFT JOIN
    dream_member dm ON dm.case_id = d.case_id
        LEFT JOIN
    patient p ON p.id = dm.id_patient
        LEFT JOIN
    dream_group dg ON dg.id = dm.id_group
        LEFT JOIN
    dream_group dpg ON dpg.id = dm.id_parenting_group
        LEFT JOIN
    dream_hub dh ON dh.id = dg.id_dream_hub
        LEFT JOIN
    lookup_commune lc ON lc.id = dh.commune
        LEFT JOIN
    lookup_departement ld ON ld.id = lc.departement
'''

sdata = read_sql_query(query, engine, parse_dates=True)
# get the test excel file from Query

# close the pool of connection
engine.dispose()

# Tidy zone

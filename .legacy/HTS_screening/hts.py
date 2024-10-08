from static.agyw import AgywPrev
import pymysql
from decouple import config
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pandas import (
    read_sql_query,
    Int32Dtype,
    to_datetime
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

_sdata_query = f"""
SELECT
    d.case_id,
    dm.id_patient as id_patient,
    p.patient_code AS code,
    d.a_non_patisipan_an AS first_name,
    d.b_siyati AS last_name,
    TIMESTAMPDIFF(YEAR,
        d.nan_ki_dat_ou_fet,
        NOW()) AS age,
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
"""


_datim = AgywPrev()
base = _datim.data_dreams_valid

sdata = read_sql_query(_sdata_query, engine, parse_dates=True)
sdata.id_patient = sdata.id_patient.astype(Int32Dtype())

hts_screening = read_sql_query(query, engine, parse_dates=True)
hts_screening['id_patient'] = hts_screening.id_patient.astype(Int32Dtype())
hts_screening['age'] = hts_screening.age.astype(Int32Dtype())
screening_vih = hts_screening[
    [
        'case_id',
        'id_patient',
        'patient_code',
        'total_score',
        'lastname',
        'firstname',
        'interview_date',
        'dob',
        'age',
        'commune',
        'age_range',
        'ovc_age'
    ]
]
screening_vih.interview_date = to_datetime(screening_vih.interview_date)

hts = base[
    base.hts == 'yes'
]

fy22 = screening_vih[
    (screening_vih.interview_date >= "2021-10-01") &
    (screening_vih.interview_date <= "2022-03-31")
]


engine.dispose()

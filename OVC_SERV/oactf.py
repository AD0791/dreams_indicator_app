import pymysql
from sqlalchemy import create_engine
from decouple import config
from dotenv import load_dotenv
from pandas import to_datetime, read_sql_query
from numpy import int16
from enum import Enum
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os


from ofunc import *

load_dotenv()
# get the environment variables needed
USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')


class Set_date(Enum):
    period_start = "2021-10-01"
    period_end = "2022-09-31"


# get the engine to connect and fetch
engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}")

query_period = f"""
SELECT 
    a.id_patient,
    h.id_parenting_group,
    g.departement,
    g.commune,
    b.nbre_pres_for_inter,
    h.nbre_parenting_coupe_present,
    b.has_comdom_topic,
    b.has_preventive_vbg,
    d.number_of_condoms_sensibilize,
    d.number_condoms_sensibilization_date_in_the_interval,
    d.number_condoms_reception_in_the_interval,
    d.number_test_date_in_the_interval,
    d.test_results,
    d.number_vbg_treatment_date_in_the_interval,
    d.number_gynecological_care_date_in_the_interval,
    d.number_prep_initiation_date_in_the_interval,
    d.number_contraceptive_reception_in_the_interval,
    c.age_in_year,
    IF(c.age_in_year >= 10
            AND c.age_in_year <= 14,
        '10-14',
        IF(c.age_in_year >= 15
                AND c.age_in_year <= 19,
            '15-19',
            IF(c.age_in_year >= 20
                    AND c.age_in_year <= 24,
                '20-24',
                IF(c.age_in_year >= 25
                        AND c.age_in_year <= 29,
                    '25-29',
                    'not_valid_age')))) AS age_range,
    IF(c.age_in_year >= 10
            AND c.age_in_year <= 14,
        '10-14',
        IF(c.age_in_year >= 15
                AND c.age_in_year <= 17,
            '15-17',
            IF(c.age_in_year >= 18
                    AND c.age_in_year <= 24,
                '18-24',
                IF(c.age_in_year >= 25
                        AND c.age_in_year <= 29,
                    '25-29',
                    'not_valid_age')))) AS ovc_age,
    c.date_interview,
    IF(c.month_in_program >= 0
            AND c.month_in_program <= 6,
        '0-6 months',
        IF(c.month_in_program >= 7
                AND c.month_in_program <= 12,
            '07-12 months',
            IF(c.month_in_program >= 13
                    AND c.month_in_program <= 24,
                '13-24 months',
                '25+ months'))) AS month_in_program_range,
    IF(e.id_patient IS NOT NULL,
        'yes',
        'no') AS muso,
    IF(f.id_patient IS NOT NULL,
        'yes',
        'no') AS gardening,
    IF(past.id_patient IS NOT NULL,
        'yes',
        'no') AS has_a_service_with_date_in_the_past
FROM
    ((SELECT 
        dhi.id_patient
    FROM
        dream_hivinfos dhi
    WHERE
        (dhi.condom_sensibilization_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.contraceptive_reception_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.test_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.vbg_treatment_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.gynecological_care_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.prep_initiation_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.has_been_sensibilize_for_condom = 1
            AND ((dhi.condom_sensibilization_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')))) UNION (SELECT 
        dga.id_patient
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}') UNION (SELECT 
        dpga.id_patient
    FROM
        dream_parenting_group_attendance dpga
    LEFT JOIN dream_parenting_group_session dpgs ON dpgs.id = dpga.id_parenting_group_session
    WHERE
        (dpga.parent_g = 'P'
            OR dpga.parent_vd = 'P'
            OR dpga.yg_g = 'P'
            OR dpga.yg_vd = 'P')
            AND dpgs.date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}') UNION (SELECT 
        dm.id_patient
    FROM
        dream_member dm
    INNER JOIN patient p ON p.id = dm.id_patient
    INNER JOIN muso_group_members mgm ON mgm.id_patient = dm.id_patient) UNION (SELECT 
        dmx.id_patient
    FROM
        dream_member dmx
    INNER JOIN patient px ON px.id = dmx.id_patient
    INNER JOIN gardening_beneficiary gbx ON gbx.code_dreams = px.patient_code
    GROUP BY dmx.id_patient)) a
        LEFT JOIN
    (SELECT 
        xy.id_patient,
            COUNT(*) AS nbre_pres_for_inter,
            IF((SUM(number_of_session_s_08) > 0
                OR SUM(number_of_session_s_10) > 0
                OR SUM(number_of_session_s_11) > 0
                OR SUM(number_of_session_s_18) > 0), 'yes', 'no') AS has_comdom_topic,
            IF((SUM(number_of_session_s_14) > 0
                OR SUM(number_of_session_s_16) > 0), 'yes', 'no') AS has_preventive_vbg
    FROM
        (SELECT 
        id_patient,
            SUM(dgs.topic = 8) AS number_of_session_s_08,
            SUM(dgs.topic = 10) AS number_of_session_s_10,
            SUM(dgs.topic = 11) AS number_of_session_s_11,
            SUM(dgs.topic = 18) AS number_of_session_s_18,
            SUM(dgs.topic = 14) AS number_of_session_s_14,
            SUM(dgs.topic = 16) AS number_of_session_s_16
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}'
    GROUP BY dga.id_patient , dgs.topic) xy
    GROUP BY xy.id_patient) b ON b.id_patient = a.id_patient
        LEFT JOIN
    (SELECT 
        dm2.id_patient,
            TIMESTAMPDIFF(MONTH, dsd.a1_dat_entvyou_a_ft_jjmmaa_egz_010817, NOW()) AS month_in_program,
            TIMESTAMPDIFF(YEAR, dsd.nan_ki_dat_ou_fet, NOW()) AS age_in_year,
            dsd.a1_dat_entvyou_a_ft_jjmmaa_egz_010817 AS date_interview
    FROM
        dream_member dm2
    LEFT JOIN dreams_surveys_data dsd ON dsd.case_id = dm2.case_id) c ON a.id_patient = c.id_patient
        LEFT JOIN
    (SELECT 
        dhi1.id_patient,
            SUM((dhi1.condom_sensibilization_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.condom_sensibilization_date IS NOT NULL)) AS number_condoms_sensibilization_date_in_the_interval,
            SUM((dhi1.contraceptive_reception_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.contraceptive_reception_date IS NOT NULL)) AS number_contraceptive_reception_in_the_interval,
            SUM(dhi1.has_been_sensibilize_for_condom = 1
                AND (dhi1.has_been_sensibilize_for_condom IS NOT NULL)) AS number_of_condoms_sensibilize,
            SUM((dhi1.condoms_reception_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.condoms_reception_date IS NOT NULL)) AS number_condoms_reception_in_the_interval,
            SUM((dhi1.test_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.test_date IS NOT NULL)) AS number_test_date_in_the_interval,
            SUM((dhi1.vbg_treatment_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.vbg_treatment_date IS NOT NULL)) AS number_vbg_treatment_date_in_the_interval,
            SUM((dhi1.gynecological_care_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.gynecological_care_date IS NOT NULL)) AS number_gynecological_care_date_in_the_interval,
            SUM((dhi1.prep_initiation_date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}')
                AND (dhi1.prep_initiation_date IS NOT NULL)) AS number_prep_initiation_date_in_the_interval,
            GROUP_CONCAT(DISTINCT dhi1.test_result, ',') AS test_results
    FROM
        dream_hivinfos dhi1
    GROUP BY dhi1.id_patient) d ON a.id_patient = d.id_patient
        LEFT JOIN
    (SELECT 
        dm2.id_patient
    FROM
        dream_member dm2
    INNER JOIN muso_group_members mgm ON mgm.id_patient = dm2.id_patient
    GROUP BY dm2.id_patient) e ON a.id_patient = e.id_patient
        LEFT JOIN
    (SELECT 
        dm3.id_patient
    FROM
        dream_member dm3
    INNER JOIN patient p1 ON p1.id = dm3.id_patient
    INNER JOIN gardening_beneficiary gb ON gb.code_dreams = p1.patient_code
    GROUP BY dm3.id_patient) f ON a.id_patient = f.id_patient
        LEFT JOIN
    (SELECT 
        dmy.id_patient, lc.name AS commune, ld.name AS departement
    FROM
        dream_member dmy
    LEFT JOIN dream_group dg ON dg.id = dmy.id_group
    LEFT JOIN dream_hub dh ON dh.id = dg.id_dream_hub
    LEFT JOIN lookup_commune lc ON lc.id = dh.commune
    LEFT JOIN lookup_departement ld ON ld.id = lc.departement) g ON a.id_patient = g.id_patient
        LEFT JOIN
    (SELECT 
        dpga.id_patient,
            COUNT(*) AS nbre_parenting_coupe_present,
            dpgs.id_group AS id_parenting_group
    FROM
        dream_parenting_group_attendance dpga
    LEFT JOIN dream_parenting_group_session dpgs ON dpgs.id = dpga.id_parenting_group_session
    WHERE
        (dpga.parent_g = 'P'
            OR dpga.parent_vd = 'P'
            OR dpga.yg_g = 'P'
            OR dpga.yg_vd = 'P')
            AND dpgs.date BETWEEN '{Set_date.period_start.value}' AND '{Set_date.period_end.value}'
    GROUP BY id_patient) h ON h.id_patient = a.id_patient
        LEFT JOIN
    ((SELECT 
        dhi.id_patient
    FROM
        dream_hivinfos dhi
    WHERE
        (dhi.test_date < '{Set_date.period_start.value}')
            OR (dhi.condoms_reception_date < '{Set_date.period_start.value}')
            OR (dhi.vbg_treatment_date < '{Set_date.period_start.value}')
            OR (dhi.gynecological_care_date < '{Set_date.period_start.value}')
            OR (dhi.prep_initiation_date < '{Set_date.period_start.value}')
            OR (dhi.condom_sensibilization_date < '{Set_date.period_start.value}')
            OR (dhi.contraceptive_reception_date < '{Set_date.period_start.value}')) UNION (SELECT 
        dga.id_patient
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date < '{Set_date.period_start.value}')) past ON past.id_patient = a.id_patient

"""

patient_query= f""" 
SELECT
    id as id_patient,
    patient_code as dreams_code,
    which_program
FROM
    caris_db.patient;
"""

patient = read_sql_query(patient_query, engine, parse_dates=True)
actif = read_sql_query(query_period, engine, parse_dates=True)
engine.dispose()


actif.nbre_pres_for_inter.fillna(0, inplace=True)
actif.has_comdom_topic.fillna('no', inplace=True)
actif.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif.number_condoms_reception_in_the_interval.fillna(0, inplace=True)
actif.number_test_date_in_the_interval.fillna(0, inplace=True)
actif.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif.number_vbg_treatment_date_in_the_interval.fillna(0, inplace=True)
actif.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif.nbre_parenting_coupe_present.fillna(0, inplace=True)
actif.number_contraceptive_reception_in_the_interval.fillna(
    0, inplace=True)
actif.number_condoms_sensibilization_date_in_the_interval.fillna(
    0, inplace=True)


actif.nbre_pres_for_inter = actif.nbre_pres_for_inter.astype(
    int16)
actif.number_of_condoms_sensibilize = actif.number_of_condoms_sensibilize.astype(
    int16)
actif.number_condoms_reception_in_the_interval = actif.number_condoms_reception_in_the_interval.astype(
    int16)
actif.number_test_date_in_the_interval = actif.number_test_date_in_the_interval.astype(
    int16)
actif.number_gynecological_care_date_in_the_interval = actif.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif.number_vbg_treatment_date_in_the_interval = actif.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif.number_prep_initiation_date_in_the_interval = actif.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif.nbre_parenting_coupe_present = actif.nbre_parenting_coupe_present.astype(
    int16)
actif.number_contraceptive_reception_in_the_interval = actif.number_contraceptive_reception_in_the_interval.astype(
    int16)
actif.number_condoms_sensibilization_date_in_the_interval = actif.number_condoms_sensibilization_date_in_the_interval.astype(
    int16)

actif['parenting_detailed'] = actif.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif['parenting'] = actif.nbre_parenting_coupe_present.map(
    parenting)
actif['curriculum_detailed'] = actif.nbre_pres_for_inter.map(
    curriculum_detailed)
actif['curriculum'] = actif.nbre_pres_for_inter.map(
    curriculum)
actif['condom'] = actif.apply(
    lambda df: condom(df), axis=1)
actif['hts'] = actif.number_test_date_in_the_interval.map(
    hts)
actif['contraceptive'] = actif.number_contraceptive_reception_in_the_interval.map(
    contraceptive)
actif['post_violence_care'] = actif.apply(
    lambda df: postcare(df), axis=1)
actif['socioeco_app'] = actif.apply(
    lambda df: socioeco(df), axis=1)
actif['prep'] = actif.number_prep_initiation_date_in_the_interval.map(
    prep)

actif['ps_1014'] = actif.apply(
    lambda df: prim_1014(df), axis=1)
actif['ps_1519'] = actif.apply(
    lambda df: prim_1519(df), axis=1)
actif['ps_2024'] = actif.apply(
    lambda df: prim_2024(df), axis=1)
actif['secondary_1014'] = actif.apply(
    lambda df: sec_1014(df), axis=1)
actif['secondary_1519'] = actif.apply(
    lambda df: sec_1519(df), axis=1)
actif['secondary_2024'] = actif.apply(
    lambda df: sec_2024(df), axis=1)
actif['complete_1014'] = actif.apply(
    lambda df: comp_1014(df), axis=1)
actif['complete_1519'] = actif.apply(
    lambda df: comp_1519(df), axis=1)
actif['complete_2024'] = actif.apply(
    lambda df: comp_2024(df), axis=1)

actif.date_interview = to_datetime(actif.date_interview)

actif['complete_at_least'] = actif.apply(
    lambda df: complete_at_least(df), axis=1)
actif['isEnrolledQ4'] = actif.date_interview.map(isEnrolledQ4)

# schooling
#Connecting to Commcare
load_dotenv('id_cc.env')
email = os.getenv('COMCARE_EMAIL')
password_cc = os.getenv('COMCARE_PASSWORD')

#Defining the driver
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(1000)

#Creating login function
def dreams_schooling():
    driver.get(
        'https://www.commcarehq.org/a/caris-test/data/export/custom/new/case/download/ae3ce02aad63402d0108435a413d38cb/'
    )
    #driver.find_element_by_xpath('//*[@id="id_auth-username"]').send_keys(email)
    driver.find_element(By.XPATH,'//*[@id="id_auth-username"]').send_keys(email)
    #driver.find_element_by_xpath('//*[@id="id_auth-password"]').send_keys(password_cc)
    driver.find_element(By.XPATH,'//*[@id="id_auth-password"]').send_keys(password_cc)
    driver.find_element(By.CSS_SELECTOR,'button[type=submit]').click()

#Muso beneficiaries
dreams_schooling()

#Download the database "All gardens"
#driver.find_element_by_xpath('//*[@id="download-export-form"]/form/div[2]/div/div[2]/div[1]/button/span[1]').click()
driver.find_element(By.XPATH,"//*[@id='download-export-form']/form/div[2]/div/div[2]/div[1]/button/span[1]").click()
#driver.find_element_by_xpath('//*[@id="download-progress"]/div/div/div[2]/div[1]/form/a/span[1]').click()    
driver.find_element(By.XPATH,"//*[@id='download-progress']/div/div/div[2]/div[1]/form/a/span[1]").click()





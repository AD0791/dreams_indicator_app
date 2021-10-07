import pymysql
from sqlalchemy import create_engine
from decouple import config
from dotenv import load_dotenv
from pandas import to_datetime, read_sql_query
from numpy import int16
from enum import Enum

from ovc_serv_functions import *

load_dotenv()
# get the environment variables needed
USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')


class Set_date(Enum):
    period_Qi_start = "2021-04-01"
    period_Qi_end = "2021-06-30"
    period_Qj_start = "2021-07-01"
    period_Qj_end = "2021-09-30"


# get the engine to connect and fetch
engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}")

# logic
# i<j
##########



query_Qi_period = f"""
SELECT 
    a.id_patient,
    h.id_parenting_group,
    g.departement,
    g.commune,
    b.nbre_pres_for_inter,
    h.nbre_parenting_coupe_present,
    b.has_comdom_topic,
    d.number_of_condoms_sensibilize,
    d.number_condoms_reception_in_the_interval,
    d.number_test_date_in_the_interval,
    d.test_results,
    d.number_vbg_treatment_date_in_the_interval,
    d.number_gynecological_care_date_in_the_interval,
    d.number_prep_initiation_date_in_the_interval,
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
        '10-14',if(c.age_in_year >= 15
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
        (dhi.test_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.vbg_treatment_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.gynecological_care_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.prep_initiation_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.has_been_sensibilize_for_condom = 1)) UNION (SELECT 
        dga.id_patient
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}') UNION (SELECT 
        dpga.id_patient
    FROM
        dream_parenting_group_attendance dpga
    LEFT JOIN dream_parenting_group_session dpgs ON dpgs.id = dpga.id_parenting_group_session
    WHERE
        (dpga.parent_g = 'P'
            OR dpga.parent_vd = 'P'
            OR dpga.yg_g = 'P'
            OR dpga.yg_vd = 'P')
            AND dpgs.date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')  UNION (SELECT 
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
                OR SUM(number_of_session_s_18) > 0), 'yes', 'no') AS has_comdom_topic
    FROM
        (SELECT 
        id_patient,
            SUM(dgs.topic = 8) AS number_of_session_s_08,
            SUM(dgs.topic = 10) AS number_of_session_s_10,
            SUM(dgs.topic = 11) AS number_of_session_s_11,
            SUM(dgs.topic = 18) AS number_of_session_s_18
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}'
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
            SUM(dhi1.has_been_sensibilize_for_condom = 1
                AND (dhi1.has_been_sensibilize_for_condom IS NOT NULL)) AS number_of_condoms_sensibilize,
            SUM((dhi1.condoms_reception_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
                AND (dhi1.condoms_reception_date IS NOT NULL)) AS number_condoms_reception_in_the_interval,
            SUM((dhi1.test_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
                AND (dhi1.test_date IS NOT NULL)) AS number_test_date_in_the_interval,
            SUM((dhi1.vbg_treatment_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
                AND (dhi1.vbg_treatment_date IS NOT NULL)) AS number_vbg_treatment_date_in_the_interval,
            SUM((dhi1.gynecological_care_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
                AND (dhi1.gynecological_care_date IS NOT NULL)) AS number_gynecological_care_date_in_the_interval,
            SUM((dhi1.prep_initiation_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
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
        dpga.id_patient, count(*) as nbre_parenting_coupe_present,dpgs.id_group as id_parenting_group
    FROM
        dream_parenting_group_attendance dpga
    LEFT JOIN dream_parenting_group_session dpgs ON dpgs.id = dpga.id_parenting_group_session
    WHERE
        (dpga.parent_g = 'P'
            OR dpga.parent_vd = 'P'
            OR dpga.yg_g = 'P'
            OR dpga.yg_vd = 'P')
            AND dpgs.date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}'
            group by id_patient
            ) h on h.id_patient=a.id_patient
            LEFT JOIN
    ((SELECT 
        dhi.id_patient
    FROM
        dream_hivinfos dhi
    WHERE
        (dhi.test_date < '{Set_date.period_Qi_start.value}')
            OR (dhi.condoms_reception_date < '{Set_date.period_Qi_start.value}')
            OR (dhi.vbg_treatment_date < '{Set_date.period_Qi_start.value}')
            OR (dhi.gynecological_care_date < '{Set_date.period_Qi_start.value}')
            OR (dhi.prep_initiation_date < '{Set_date.period_Qi_start.value}')) UNION (SELECT 
        dga.id_patient
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date < '{Set_date.period_Qi_start.value}')) past ON past.id_patient = a.id_patient

"""


query_Qj_period = f"""
SELECT 
    a.id_patient,
    h.id_parenting_group,
    g.departement,
    g.commune,
    b.nbre_pres_for_inter,
    h.nbre_parenting_coupe_present,
    b.has_comdom_topic,
    d.number_of_condoms_sensibilize,
    d.number_condoms_reception_in_the_interval,
    d.number_test_date_in_the_interval,
    d.test_results,
    d.number_vbg_treatment_date_in_the_interval,
    d.number_gynecological_care_date_in_the_interval,
    d.number_prep_initiation_date_in_the_interval,
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
        '10-14',if(c.age_in_year >= 15
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
        (dhi.test_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.vbg_treatment_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.gynecological_care_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.prep_initiation_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.has_been_sensibilize_for_condom = 1)) UNION (SELECT 
        dga.id_patient
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}') UNION (SELECT 
        dpga.id_patient
    FROM
        dream_parenting_group_attendance dpga
    LEFT JOIN dream_parenting_group_session dpgs ON dpgs.id = dpga.id_parenting_group_session
    WHERE
        (dpga.parent_g = 'P'
            OR dpga.parent_vd = 'P'
            OR dpga.yg_g = 'P'
            OR dpga.yg_vd = 'P')
            AND dpgs.date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')  UNION (SELECT 
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
                OR SUM(number_of_session_s_18) > 0), 'yes', 'no') AS has_comdom_topic
    FROM
        (SELECT 
        id_patient,
            SUM(dgs.topic = 8) AS number_of_session_s_08,
            SUM(dgs.topic = 10) AS number_of_session_s_10,
            SUM(dgs.topic = 11) AS number_of_session_s_11,
            SUM(dgs.topic = 18) AS number_of_session_s_18
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}'
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
            SUM(dhi1.has_been_sensibilize_for_condom = 1
                AND (dhi1.has_been_sensibilize_for_condom IS NOT NULL)) AS number_of_condoms_sensibilize,
            SUM((dhi1.condoms_reception_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
                AND (dhi1.condoms_reception_date IS NOT NULL)) AS number_condoms_reception_in_the_interval,
            SUM((dhi1.test_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
                AND (dhi1.test_date IS NOT NULL)) AS number_test_date_in_the_interval,
            SUM((dhi1.vbg_treatment_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
                AND (dhi1.vbg_treatment_date IS NOT NULL)) AS number_vbg_treatment_date_in_the_interval,
            SUM((dhi1.gynecological_care_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
                AND (dhi1.gynecological_care_date IS NOT NULL)) AS number_gynecological_care_date_in_the_interval,
            SUM((dhi1.prep_initiation_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
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
        dpga.id_patient, count(*) as nbre_parenting_coupe_present,dpgs.id_group as id_parenting_group
    FROM
        dream_parenting_group_attendance dpga
    LEFT JOIN dream_parenting_group_session dpgs ON dpgs.id = dpga.id_parenting_group_session
    WHERE
        (dpga.parent_g = 'P'
            OR dpga.parent_vd = 'P'
            OR dpga.yg_g = 'P'
            OR dpga.yg_vd = 'P')
            AND dpgs.date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}'
            group by id_patient
            ) h on h.id_patient=a.id_patient
            LEFT JOIN
    ((SELECT 
        dhi.id_patient
    FROM
        dream_hivinfos dhi
    WHERE
        (dhi.test_date < '{Set_date.period_Qj_start.value}')
            OR (dhi.condoms_reception_date < '{Set_date.period_Qj_start.value}')
            OR (dhi.vbg_treatment_date < '{Set_date.period_Qj_start.value}')
            OR (dhi.gynecological_care_date < '{Set_date.period_Qj_start.value}')
            OR (dhi.prep_initiation_date < '{Set_date.period_Qj_start.value}')) UNION (SELECT 
        dga.id_patient
    FROM
        dream_group_attendance dga
    LEFT JOIN dream_group_session dgs ON dgs.id = dga.id_group_session
    WHERE
        dga.value = 'P'
            AND dgs.date < '{Set_date.period_Qj_start.value}')) past ON past.id_patient = a.id_patient

"""


agyw_served_Qi = read_sql_query(query_Qi_period, engine, parse_dates=True)
agyw_served_Qj = read_sql_query(query_Qj_period, engine, parse_dates=True)

# close the pool of connection
engine.dispose()


actif_in_Q3 = agyw_served_Qi
actif_in_Q4 = agyw_served_Qj

actif_in_Q3Q4 = actif_in_Q3[actif_in_Q3.id_patient.isin(actif_in_Q4.id_patient)]
actif_in_Q3strict = actif_in_Q3[~actif_in_Q3.id_patient.isin(actif_in_Q4.id_patient)]
actif_in_Q4strict = actif_in_Q4[~actif_in_Q4.id_patient.isin(actif_in_Q3.id_patient)]


#################################################################
#################################
#################################

# Q3 strict

actif_in_Q3strict.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q3strict.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q3strict.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q3strict.number_condoms_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3strict.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q3strict.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3strict.number_vbg_treatment_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3strict.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3strict.nbre_parenting_coupe_present.fillna(0, inplace=True)


actif_in_Q3strict.nbre_pres_for_inter = actif_in_Q3strict.nbre_pres_for_inter.astype(
    int16)
actif_in_Q3strict.number_of_condoms_sensibilize = actif_in_Q3strict.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q3strict.number_condoms_reception_in_the_interval = actif_in_Q3strict.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q3strict.number_test_date_in_the_interval = actif_in_Q3strict.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q3strict.number_gynecological_care_date_in_the_interval = actif_in_Q3strict.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q3strict.number_vbg_treatment_date_in_the_interval = actif_in_Q3strict.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q3strict.number_prep_initiation_date_in_the_interval = actif_in_Q3strict.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q3strict.nbre_parenting_coupe_present = actif_in_Q3strict.nbre_parenting_coupe_present.astype(
    int16)

actif_in_Q3strict['parenting_detailed'] = actif_in_Q3strict.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q3strict['parenting'] = actif_in_Q3strict.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q3strict['curriculum_detailed'] = actif_in_Q3strict.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q3strict['curriculum'] = actif_in_Q3strict.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q3strict['condom'] = actif_in_Q3strict.apply(
    lambda df: condom(df), axis=1)
actif_in_Q3strict['hts'] = actif_in_Q3strict.number_test_date_in_the_interval.map(
    hts)
actif_in_Q3strict['post_violence_care'] = actif_in_Q3strict.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q3strict['socioeco_app'] = actif_in_Q3strict.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q3strict['prep'] = actif_in_Q3strict.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q3strict['ps_1014'] = actif_in_Q3strict.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q3strict['ps_1519'] = actif_in_Q3strict.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q3strict['ps_2024'] = actif_in_Q3strict.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q3strict['secondary_1014'] = actif_in_Q3strict.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q3strict['secondary_1519'] = actif_in_Q3strict.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q3strict['secondary_2024'] = actif_in_Q3strict.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q3strict['complete_1014'] = actif_in_Q3strict.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q3strict['complete_1519'] = actif_in_Q3strict.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q3strict['complete_2024'] = actif_in_Q3strict.apply(
    lambda df: comp_2024(df), axis=1)

#############################################
# Q4 strict

actif_in_Q4strict.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q4strict.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q4strict.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q4strict.number_condoms_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4strict.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q4strict.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4strict.number_vbg_treatment_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4strict.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4strict.nbre_parenting_coupe_present.fillna(0, inplace=True)


actif_in_Q4strict.nbre_pres_for_inter = actif_in_Q4strict.nbre_pres_for_inter.astype(
    int16)
actif_in_Q4strict.number_of_condoms_sensibilize = actif_in_Q4strict.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q4strict.number_condoms_reception_in_the_interval = actif_in_Q4strict.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q4strict.number_test_date_in_the_interval = actif_in_Q4strict.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q4strict.number_gynecological_care_date_in_the_interval = actif_in_Q4strict.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q4strict.number_vbg_treatment_date_in_the_interval = actif_in_Q4strict.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q4strict.number_prep_initiation_date_in_the_interval = actif_in_Q4strict.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q4strict.nbre_parenting_coupe_present = actif_in_Q4strict.nbre_parenting_coupe_present.astype(
    int16)

# services
actif_in_Q4strict['parenting_detailed'] = actif_in_Q4strict.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q4strict['parenting'] = actif_in_Q4strict.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q4strict['curriculum_detailed'] = actif_in_Q4strict.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q4strict['curriculum'] = actif_in_Q4strict.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q4strict['condom'] = actif_in_Q4strict.apply(
    lambda df: condom(df), axis=1)
actif_in_Q4strict['hts'] = actif_in_Q4strict.number_test_date_in_the_interval.map(
    hts)
actif_in_Q4strict['post_violence_care'] = actif_in_Q4strict.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q4strict['socioeco_app'] = actif_in_Q4strict.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q4strict['prep'] = actif_in_Q4strict.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q4strict['ps_1014'] = actif_in_Q4strict.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q4strict['ps_1519'] = actif_in_Q4strict.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q4strict['ps_2024'] = actif_in_Q4strict.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q4strict['secondary_1014'] = actif_in_Q4strict.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q4strict['secondary_1519'] = actif_in_Q4strict.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q4strict['secondary_2024'] = actif_in_Q4strict.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q4strict['complete_1014'] = actif_in_Q4strict.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q4strict['complete_1519'] = actif_in_Q4strict.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q4strict['complete_2024'] = actif_in_Q4strict.apply(
    lambda df: comp_2024(df), axis=1)


##################################
# Q3Q4

actif_in_Q3Q4.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q3Q4.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q3Q4.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q3Q4.number_condoms_reception_in_the_interval.fillna(0, inplace=True)
actif_in_Q3Q4.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q3Q4.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3Q4.number_vbg_treatment_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q3Q4.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3Q4.nbre_parenting_coupe_present.fillna(0, inplace=True)


actif_in_Q3Q4.nbre_pres_for_inter = actif_in_Q3Q4.nbre_pres_for_inter.astype(
    int16)
actif_in_Q3Q4.number_of_condoms_sensibilize = actif_in_Q3Q4.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q3Q4.number_condoms_reception_in_the_interval = actif_in_Q3Q4.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q3Q4.number_test_date_in_the_interval = actif_in_Q3Q4.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q3Q4.number_gynecological_care_date_in_the_interval = actif_in_Q3Q4.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q3Q4.number_vbg_treatment_date_in_the_interval = actif_in_Q3Q4.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q3Q4.number_prep_initiation_date_in_the_interval = actif_in_Q3Q4.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q3Q4.nbre_parenting_coupe_present = actif_in_Q3Q4.nbre_parenting_coupe_present.astype(
    int16)


actif_in_Q3Q4['parenting_detailed'] = actif_in_Q3Q4.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q3Q4['parenting'] = actif_in_Q3Q4.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q3Q4['curriculum_detailed'] = actif_in_Q3Q4.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q3Q4['curriculum'] = actif_in_Q3Q4.nbre_pres_for_inter.map(curriculum)
actif_in_Q3Q4['condom'] = actif_in_Q3Q4.apply(lambda df: condom(df), axis=1)
actif_in_Q3Q4['hts'] = actif_in_Q3Q4.number_test_date_in_the_interval.map(hts)
actif_in_Q3Q4['post_violence_care'] = actif_in_Q3Q4.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q3Q4['socioeco_app'] = actif_in_Q3Q4.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q3Q4['prep'] = actif_in_Q3Q4.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q3Q4['ps_1014'] = actif_in_Q3Q4.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q3Q4['ps_1519'] = actif_in_Q3Q4.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q3Q4['ps_2024'] = actif_in_Q3Q4.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q3Q4['secondary_1014'] = actif_in_Q3Q4.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q3Q4['secondary_1519'] = actif_in_Q3Q4.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q3Q4['secondary_2024'] = actif_in_Q3Q4.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q3Q4['complete_1014'] = actif_in_Q3Q4.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q3Q4['complete_1519'] = actif_in_Q3Q4.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q3Q4['complete_2024'] = actif_in_Q3Q4.apply(
    lambda df: comp_2024(df), axis=1)


##### complete and enrolled {merge}

actif_in_Q4strict.date_interview = to_datetime(actif_in_Q4strict.date_interview)
actif_in_Q3strict.date_interview = to_datetime(actif_in_Q3strict.date_interview)
actif_in_Q3Q4.date_interview= to_datetime(actif_in_Q3Q4.date_interview)

actif_in_Q3strict['complete_at_least']= actif_in_Q3strict.apply(lambda df: complete_at_least(df),axis=1)
actif_in_Q4strict['complete_at_least'] = actif_in_Q4strict.apply(lambda df: complete_at_least(df),axis=1)
actif_in_Q3Q4['complete_at_least']= actif_in_Q3Q4.apply(lambda df: complete_at_least(df),axis=1)


actif_in_Q3strict['isEnrolledQ4']= actif_in_Q3strict.date_interview.map(isEnrolledQ4)
actif_in_Q4strict['isEnrolledQ4'] = actif_in_Q4strict.date_interview.map(isEnrolledQ4)
actif_in_Q3Q4['isEnrolledQ4']= actif_in_Q3Q4.date_interview.map(isEnrolledQ4)

################################ for Q3 and Q4



# Q3 

actif_in_Q3.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q3.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q3.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q3.number_condoms_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q3.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3.number_vbg_treatment_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q3.nbre_parenting_coupe_present.fillna(0, inplace=True)


actif_in_Q3.nbre_pres_for_inter = actif_in_Q3.nbre_pres_for_inter.astype(
    int16)
actif_in_Q3.number_of_condoms_sensibilize = actif_in_Q3.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q3.number_condoms_reception_in_the_interval = actif_in_Q3.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q3.number_test_date_in_the_interval = actif_in_Q3.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q3.number_gynecological_care_date_in_the_interval = actif_in_Q3.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q3.number_vbg_treatment_date_in_the_interval = actif_in_Q3.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q3.number_prep_initiation_date_in_the_interval = actif_in_Q3.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q3.nbre_parenting_coupe_present = actif_in_Q3.nbre_parenting_coupe_present.astype(
    int16)

actif_in_Q3['parenting_detailed'] = actif_in_Q3.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q3['parenting'] = actif_in_Q3.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q3['curriculum_detailed'] = actif_in_Q3.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q3['curriculum'] = actif_in_Q3.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q3['condom'] = actif_in_Q3.apply(
    lambda df: condom(df), axis=1)
actif_in_Q3['hts'] = actif_in_Q3.number_test_date_in_the_interval.map(
    hts)
actif_in_Q3['post_violence_care'] = actif_in_Q3.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q3['socioeco_app'] = actif_in_Q3.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q3['prep'] = actif_in_Q3.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q3['ps_1014'] = actif_in_Q3.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q3['ps_1519'] = actif_in_Q3.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q3['ps_2024'] = actif_in_Q3.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q3['secondary_1014'] = actif_in_Q3.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q3['secondary_1519'] = actif_in_Q3.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q3['secondary_2024'] = actif_in_Q3.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q3['complete_1014'] = actif_in_Q3.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q3['complete_1519'] = actif_in_Q3.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q3['complete_2024'] = actif_in_Q3.apply(
    lambda df: comp_2024(df), axis=1)

#############################################
# Q4 

actif_in_Q4.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q4.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q4.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q4.number_condoms_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q4.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4.number_vbg_treatment_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q4.nbre_parenting_coupe_present.fillna(0, inplace=True)


actif_in_Q4.nbre_pres_for_inter = actif_in_Q4.nbre_pres_for_inter.astype(
    int16)
actif_in_Q4.number_of_condoms_sensibilize = actif_in_Q4.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q4.number_condoms_reception_in_the_interval = actif_in_Q4.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q4.number_test_date_in_the_interval = actif_in_Q4.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q4.number_gynecological_care_date_in_the_interval = actif_in_Q4.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q4.number_vbg_treatment_date_in_the_interval = actif_in_Q4.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q4.number_prep_initiation_date_in_the_interval = actif_in_Q4.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q4.nbre_parenting_coupe_present = actif_in_Q4.nbre_parenting_coupe_present.astype(
    int16)

# services
actif_in_Q4['parenting_detailed'] = actif_in_Q4.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q4['parenting'] = actif_in_Q4.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q4['curriculum_detailed'] = actif_in_Q4.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q4['curriculum'] = actif_in_Q4.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q4['condom'] = actif_in_Q4.apply(
    lambda df: condom(df), axis=1)
actif_in_Q4['hts'] = actif_in_Q4.number_test_date_in_the_interval.map(
    hts)
actif_in_Q4['post_violence_care'] = actif_in_Q4.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q4['socioeco_app'] = actif_in_Q4.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q4['prep'] = actif_in_Q4.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q4['ps_1014'] = actif_in_Q4.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q4['ps_1519'] = actif_in_Q4.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q4['ps_2024'] = actif_in_Q4.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q4['secondary_1014'] = actif_in_Q4.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q4['secondary_1519'] = actif_in_Q4.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q4['secondary_2024'] = actif_in_Q4.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q4['complete_1014'] = actif_in_Q4.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q4['complete_1519'] = actif_in_Q4.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q4['complete_2024'] = actif_in_Q4.apply(
    lambda df: comp_2024(df), axis=1)


########### pure case

actif_in_Q4.date_interview = to_datetime(actif_in_Q4.date_interview)
actif_in_Q3.date_interview = to_datetime(actif_in_Q3.date_interview)
actif_in_Q3['complete_at_least']= actif_in_Q3.apply(lambda df: complete_at_least(df),axis=1)
actif_in_Q4['complete_at_least'] = actif_in_Q4.apply(lambda df: complete_at_least(df),axis=1)
actif_in_Q3['isEnrolledQ4']= actif_in_Q3.date_interview.map(isEnrolledQ4)
actif_in_Q4['isEnrolledQ4'] = actif_in_Q4.date_interview.map(isEnrolledQ4)



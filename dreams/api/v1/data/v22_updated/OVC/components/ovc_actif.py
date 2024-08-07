import pymysql
from sqlalchemy import create_engine
from decouple import config
from dotenv import load_dotenv
from pandas import to_datetime, read_sql_query
from numpy import int16
from enum import Enum

from .ovc_serv_functions import *

load_dotenv()
# get the environment variables needed
USER = config('USRCaris')
PASSWORD = config('PASSCaris')
HOSTNAME = config('HOSTCaris')
DBNAME = config('DBCaris')


class Set_date(Enum):
    period_Qi_start = "2021-10-01"
    period_Qi_end = "2021-12-31"
    period_Qj_start = "2022-01-01"
    period_Qj_end = "2022-03-31"


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
        (dhi.condom_sensibilization_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.contraceptive_reception_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.test_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.vbg_treatment_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.gynecological_care_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.prep_initiation_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.has_been_sensibilize_for_condom = 1
            AND ((dhi.condom_sensibilization_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')))) UNION (SELECT 
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
            AND dpgs.date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}') UNION (SELECT 
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
            SUM((dhi1.condom_sensibilization_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
                AND (dhi1.condom_sensibilization_date IS NOT NULL)) AS number_condoms_sensibilization_date_in_the_interval,
            SUM((dhi1.contraceptive_reception_date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}')
                AND (dhi1.contraceptive_reception_date IS NOT NULL)) AS number_contraceptive_reception_in_the_interval,
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
            AND dpgs.date BETWEEN '{Set_date.period_Qi_start.value}' AND '{Set_date.period_Qi_end.value}'
    GROUP BY id_patient) h ON h.id_patient = a.id_patient
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
            OR (dhi.prep_initiation_date < '{Set_date.period_Qi_start.value}')
            OR (dhi.condom_sensibilization_date < '{Set_date.period_Qi_start.value}')
            OR (dhi.contraceptive_reception_date < '{Set_date.period_Qi_start.value}')) UNION (SELECT 
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
        (dhi.condom_sensibilization_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.contraceptive_reception_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.test_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.vbg_treatment_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.gynecological_care_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.prep_initiation_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.has_been_sensibilize_for_condom = 1
            AND ((dhi.condom_sensibilization_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
            OR (dhi.condoms_reception_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')))) UNION (SELECT 
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
            AND dpgs.date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}') UNION (SELECT 
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
            SUM((dhi1.condom_sensibilization_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
                AND (dhi1.condom_sensibilization_date IS NOT NULL)) AS number_condoms_sensibilization_date_in_the_interval,
            SUM((dhi1.contraceptive_reception_date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}')
                AND (dhi1.contraceptive_reception_date IS NOT NULL)) AS number_contraceptive_reception_in_the_interval,
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
            AND dpgs.date BETWEEN '{Set_date.period_Qj_start.value}' AND '{Set_date.period_Qj_end.value}'
    GROUP BY id_patient) h ON h.id_patient = a.id_patient
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
            OR (dhi.prep_initiation_date < '{Set_date.period_Qj_start.value}')
            OR (dhi.condom_sensibilization_date < '{Set_date.period_Qj_start.value}')
            OR (dhi.contraceptive_reception_date < '{Set_date.period_Qj_start.value}')) UNION (SELECT 
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


actif_in_Q1 = agyw_served_Qi
actif_in_Q2 = agyw_served_Qj

actif_in_Q1Q2 = actif_in_Q1[actif_in_Q1.id_patient.isin(
    actif_in_Q2.id_patient)]
actif_in_Q1strict = actif_in_Q1[~actif_in_Q1.id_patient.isin(
    actif_in_Q2.id_patient)]
actif_in_Q2strict = actif_in_Q2[~actif_in_Q2.id_patient.isin(
    actif_in_Q1.id_patient)]


#################################################################
#################################
#################################

# Q1 strict

actif_in_Q1strict.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q1strict.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q1strict.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q1strict.number_condoms_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1strict.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q1strict.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1strict.number_vbg_treatment_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1strict.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1strict.nbre_parenting_coupe_present.fillna(0, inplace=True)
actif_in_Q1strict.number_contraceptive_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1strict.number_condoms_sensibilization_date_in_the_interval.fillna(
    0, inplace=True)


actif_in_Q1strict.nbre_pres_for_inter = actif_in_Q1strict.nbre_pres_for_inter.astype(
    int16)
actif_in_Q1strict.number_of_condoms_sensibilize = actif_in_Q1strict.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q1strict.number_condoms_reception_in_the_interval = actif_in_Q1strict.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q1strict.number_test_date_in_the_interval = actif_in_Q1strict.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q1strict.number_gynecological_care_date_in_the_interval = actif_in_Q1strict.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q1strict.number_vbg_treatment_date_in_the_interval = actif_in_Q1strict.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q1strict.number_prep_initiation_date_in_the_interval = actif_in_Q1strict.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q1strict.nbre_parenting_coupe_present = actif_in_Q1strict.nbre_parenting_coupe_present.astype(
    int16)
actif_in_Q1strict.number_contraceptive_reception_in_the_interval = actif_in_Q1strict.number_contraceptive_reception_in_the_interval.astype(
    int16)
actif_in_Q1strict.number_condoms_sensibilization_date_in_the_interval = actif_in_Q1strict.number_condoms_sensibilization_date_in_the_interval.astype(
    int16)

actif_in_Q1strict['parenting_detailed'] = actif_in_Q1strict.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q1strict['parenting'] = actif_in_Q1strict.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q1strict['curriculum_detailed'] = actif_in_Q1strict.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q1strict['curriculum'] = actif_in_Q1strict.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q1strict['condom'] = actif_in_Q1strict.apply(
    lambda df: condom(df), axis=1)
actif_in_Q1strict['hts'] = actif_in_Q1strict.number_test_date_in_the_interval.map(
    hts)
actif_in_Q1strict['contraceptive'] = actif_in_Q1strict.number_contraceptive_reception_in_the_interval.map(
    contraceptive)
actif_in_Q1strict['post_violence_care'] = actif_in_Q1strict.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q1strict['socioeco_app'] = actif_in_Q1strict.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q1strict['prep'] = actif_in_Q1strict.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q1strict['ps_1014'] = actif_in_Q1strict.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q1strict['ps_1519'] = actif_in_Q1strict.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q1strict['ps_2024'] = actif_in_Q1strict.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q1strict['secondary_1014'] = actif_in_Q1strict.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q1strict['secondary_1519'] = actif_in_Q1strict.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q1strict['secondary_2024'] = actif_in_Q1strict.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q1strict['complete_1014'] = actif_in_Q1strict.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q1strict['complete_1519'] = actif_in_Q1strict.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q1strict['complete_2024'] = actif_in_Q1strict.apply(
    lambda df: comp_2024(df), axis=1)
#############################################
# Q2 strict

actif_in_Q2strict.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q2strict.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q2strict.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q2strict.number_condoms_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2strict.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q2strict.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2strict.number_vbg_treatment_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2strict.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2strict.nbre_parenting_coupe_present.fillna(0, inplace=True)
actif_in_Q2strict.number_contraceptive_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2strict.number_condoms_sensibilization_date_in_the_interval.fillna(
    0, inplace=True)


actif_in_Q2strict.nbre_pres_for_inter = actif_in_Q2strict.nbre_pres_for_inter.astype(
    int16)
actif_in_Q2strict.number_of_condoms_sensibilize = actif_in_Q2strict.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q2strict.number_condoms_reception_in_the_interval = actif_in_Q2strict.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q2strict.number_test_date_in_the_interval = actif_in_Q2strict.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q2strict.number_gynecological_care_date_in_the_interval = actif_in_Q2strict.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q2strict.number_vbg_treatment_date_in_the_interval = actif_in_Q2strict.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q2strict.number_prep_initiation_date_in_the_interval = actif_in_Q2strict.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q2strict.nbre_parenting_coupe_present = actif_in_Q2strict.nbre_parenting_coupe_present.astype(
    int16)
actif_in_Q2strict.number_contraceptive_reception_in_the_interval = actif_in_Q2strict.number_contraceptive_reception_in_the_interval.astype(
    int16)
actif_in_Q2strict.number_condoms_sensibilization_date_in_the_interval = actif_in_Q2strict.number_condoms_sensibilization_date_in_the_interval.astype(
    int16)

actif_in_Q2strict['parenting_detailed'] = actif_in_Q2strict.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q2strict['parenting'] = actif_in_Q2strict.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q2strict['curriculum_detailed'] = actif_in_Q2strict.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q2strict['curriculum'] = actif_in_Q2strict.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q2strict['condom'] = actif_in_Q2strict.apply(
    lambda df: condom(df), axis=1)
actif_in_Q2strict['hts'] = actif_in_Q2strict.number_test_date_in_the_interval.map(
    hts)
actif_in_Q2strict['contraceptive'] = actif_in_Q2strict.number_contraceptive_reception_in_the_interval.map(
    contraceptive)
actif_in_Q2strict['post_violence_care'] = actif_in_Q2strict.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q2strict['socioeco_app'] = actif_in_Q2strict.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q2strict['prep'] = actif_in_Q2strict.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q2strict['ps_1014'] = actif_in_Q2strict.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q2strict['ps_1519'] = actif_in_Q2strict.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q2strict['ps_2024'] = actif_in_Q2strict.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q2strict['secondary_1014'] = actif_in_Q2strict.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q2strict['secondary_1519'] = actif_in_Q2strict.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q2strict['secondary_2024'] = actif_in_Q2strict.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q2strict['complete_1014'] = actif_in_Q2strict.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q2strict['complete_1519'] = actif_in_Q2strict.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q2strict['complete_2024'] = actif_in_Q2strict.apply(
    lambda df: comp_2024(df), axis=1)


##################################
# Q1Q2

actif_in_Q1Q2.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q1Q2.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q1Q2.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q1Q2.number_condoms_reception_in_the_interval.fillna(0, inplace=True)
actif_in_Q1Q2.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q1Q2.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1Q2.number_vbg_treatment_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q1Q2.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1Q2.nbre_parenting_coupe_present.fillna(0, inplace=True)
actif_in_Q1Q2.number_contraceptive_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1Q2.number_condoms_sensibilization_date_in_the_interval.fillna(
    0, inplace=True)


actif_in_Q1Q2.nbre_pres_for_inter = actif_in_Q1Q2.nbre_pres_for_inter.astype(
    int16)
actif_in_Q1Q2.number_of_condoms_sensibilize = actif_in_Q1Q2.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q1Q2.number_condoms_reception_in_the_interval = actif_in_Q1Q2.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q1Q2.number_test_date_in_the_interval = actif_in_Q1Q2.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q1Q2.number_gynecological_care_date_in_the_interval = actif_in_Q1Q2.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q1Q2.number_vbg_treatment_date_in_the_interval = actif_in_Q1Q2.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q1Q2.number_prep_initiation_date_in_the_interval = actif_in_Q1Q2.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q1Q2.nbre_parenting_coupe_present = actif_in_Q1Q2.nbre_parenting_coupe_present.astype(
    int16)
actif_in_Q1Q2.number_contraceptive_reception_in_the_interval = actif_in_Q1Q2.number_contraceptive_reception_in_the_interval.astype(
    int16)
actif_in_Q1Q2.number_condoms_sensibilization_date_in_the_interval = actif_in_Q1Q2.number_condoms_sensibilization_date_in_the_interval.astype(
    int16)

actif_in_Q1Q2['parenting_detailed'] = actif_in_Q1Q2.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q1Q2['parenting'] = actif_in_Q1Q2.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q1Q2['curriculum_detailed'] = actif_in_Q1Q2.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q1Q2['curriculum'] = actif_in_Q1Q2.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q1Q2['condom'] = actif_in_Q1Q2.apply(
    lambda df: condom(df), axis=1)
actif_in_Q1Q2['hts'] = actif_in_Q1Q2.number_test_date_in_the_interval.map(
    hts)
actif_in_Q1Q2['contraceptive'] = actif_in_Q1Q2.number_contraceptive_reception_in_the_interval.map(
    contraceptive)
actif_in_Q1Q2['post_violence_care'] = actif_in_Q1Q2.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q1Q2['socioeco_app'] = actif_in_Q1Q2.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q1Q2['prep'] = actif_in_Q1Q2.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q1Q2['ps_1014'] = actif_in_Q1Q2.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q1Q2['ps_1519'] = actif_in_Q1Q2.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q1Q2['ps_2024'] = actif_in_Q1Q2.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q1Q2['secondary_1014'] = actif_in_Q1Q2.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q1Q2['secondary_1519'] = actif_in_Q1Q2.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q1Q2['secondary_2024'] = actif_in_Q1Q2.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q1Q2['complete_1014'] = actif_in_Q1Q2.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q1Q2['complete_1519'] = actif_in_Q1Q2.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q1Q2['complete_2024'] = actif_in_Q1Q2.apply(
    lambda df: comp_2024(df), axis=1)


# complete and enrolled {merge}

actif_in_Q2strict.date_interview = to_datetime(
    actif_in_Q2strict.date_interview)
actif_in_Q1strict.date_interview = to_datetime(
    actif_in_Q1strict.date_interview)
actif_in_Q1Q2.date_interview = to_datetime(actif_in_Q1Q2.date_interview)

actif_in_Q1strict['complete_at_least'] = actif_in_Q1strict.apply(
    lambda df: complete_at_least(df), axis=1)
actif_in_Q2strict['complete_at_least'] = actif_in_Q2strict.apply(
    lambda df: complete_at_least(df), axis=1)
actif_in_Q1Q2['complete_at_least'] = actif_in_Q1Q2.apply(
    lambda df: complete_at_least(df), axis=1)


actif_in_Q1strict['isEnrolledQ2'] = actif_in_Q1strict.date_interview.map(
    isEnrolledQ2)
actif_in_Q2strict['isEnrolledQ2'] = actif_in_Q2strict.date_interview.map(
    isEnrolledQ2)
actif_in_Q1Q2['isEnrolledQ2'] = actif_in_Q1Q2.date_interview.map(isEnrolledQ2)

# for Q1 and Q2


# Q1

actif_in_Q1.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q1.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q1.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q1.number_condoms_reception_in_the_interval.fillna(0, inplace=True)
actif_in_Q1.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q1.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1.number_vbg_treatment_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q1.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1.nbre_parenting_coupe_present.fillna(0, inplace=True)
actif_in_Q1.number_contraceptive_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q1.number_condoms_sensibilization_date_in_the_interval.fillna(
    0, inplace=True)


actif_in_Q1.nbre_pres_for_inter = actif_in_Q1.nbre_pres_for_inter.astype(
    int16)
actif_in_Q1.number_of_condoms_sensibilize = actif_in_Q1.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q1.number_condoms_reception_in_the_interval = actif_in_Q1.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q1.number_test_date_in_the_interval = actif_in_Q1.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q1.number_gynecological_care_date_in_the_interval = actif_in_Q1.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q1.number_vbg_treatment_date_in_the_interval = actif_in_Q1.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q1.number_prep_initiation_date_in_the_interval = actif_in_Q1.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q1.nbre_parenting_coupe_present = actif_in_Q1.nbre_parenting_coupe_present.astype(
    int16)
actif_in_Q1.number_contraceptive_reception_in_the_interval = actif_in_Q1.number_contraceptive_reception_in_the_interval.astype(
    int16)
actif_in_Q1.number_condoms_sensibilization_date_in_the_interval = actif_in_Q1.number_condoms_sensibilization_date_in_the_interval.astype(
    int16)

actif_in_Q1['parenting_detailed'] = actif_in_Q1.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q1['parenting'] = actif_in_Q1.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q1['curriculum_detailed'] = actif_in_Q1.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q1['curriculum'] = actif_in_Q1.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q1['condom'] = actif_in_Q1.apply(
    lambda df: condom(df), axis=1)
actif_in_Q1['hts'] = actif_in_Q1.number_test_date_in_the_interval.map(
    hts)
actif_in_Q1['contraceptive'] = actif_in_Q1.number_contraceptive_reception_in_the_interval.map(
    contraceptive)
actif_in_Q1['post_violence_care'] = actif_in_Q1.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q1['socioeco_app'] = actif_in_Q1.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q1['prep'] = actif_in_Q1.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q1['ps_1014'] = actif_in_Q1.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q1['ps_1519'] = actif_in_Q1.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q1['ps_2024'] = actif_in_Q1.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q1['secondary_1014'] = actif_in_Q1.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q1['secondary_1519'] = actif_in_Q1.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q1['secondary_2024'] = actif_in_Q1.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q1['complete_1014'] = actif_in_Q1.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q1['complete_1519'] = actif_in_Q1.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q1['complete_2024'] = actif_in_Q1.apply(
    lambda df: comp_2024(df), axis=1)

#############################################
# Q2

actif_in_Q2.nbre_pres_for_inter.fillna(0, inplace=True)
actif_in_Q2.has_comdom_topic.fillna('no', inplace=True)
actif_in_Q2.number_of_condoms_sensibilize.fillna(0, inplace=True)
actif_in_Q2.number_condoms_reception_in_the_interval.fillna(0, inplace=True)
actif_in_Q2.number_test_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q2.number_gynecological_care_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2.number_vbg_treatment_date_in_the_interval.fillna(0, inplace=True)
actif_in_Q2.number_prep_initiation_date_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2.nbre_parenting_coupe_present.fillna(0, inplace=True)
actif_in_Q2.number_contraceptive_reception_in_the_interval.fillna(
    0, inplace=True)
actif_in_Q2.number_condoms_sensibilization_date_in_the_interval.fillna(
    0, inplace=True)


actif_in_Q2.nbre_pres_for_inter = actif_in_Q2.nbre_pres_for_inter.astype(
    int16)
actif_in_Q2.number_of_condoms_sensibilize = actif_in_Q2.number_of_condoms_sensibilize.astype(
    int16)
actif_in_Q2.number_condoms_reception_in_the_interval = actif_in_Q2.number_condoms_reception_in_the_interval.astype(
    int16)
actif_in_Q2.number_test_date_in_the_interval = actif_in_Q2.number_test_date_in_the_interval.astype(
    int16)
actif_in_Q2.number_gynecological_care_date_in_the_interval = actif_in_Q2.number_gynecological_care_date_in_the_interval.astype(
    int16)
actif_in_Q2.number_vbg_treatment_date_in_the_interval = actif_in_Q2.number_vbg_treatment_date_in_the_interval.astype(
    int16)
actif_in_Q2.number_prep_initiation_date_in_the_interval = actif_in_Q2.number_prep_initiation_date_in_the_interval.astype(
    int16)
actif_in_Q2.nbre_parenting_coupe_present = actif_in_Q2.nbre_parenting_coupe_present.astype(
    int16)
actif_in_Q2.number_contraceptive_reception_in_the_interval = actif_in_Q2.number_contraceptive_reception_in_the_interval.astype(
    int16)
actif_in_Q2.number_condoms_sensibilization_date_in_the_interval = actif_in_Q2.number_condoms_sensibilization_date_in_the_interval.astype(
    int16)

actif_in_Q2['parenting_detailed'] = actif_in_Q2.nbre_parenting_coupe_present.map(
    parenting_detailed)
actif_in_Q2['parenting'] = actif_in_Q2.nbre_parenting_coupe_present.map(
    parenting)
actif_in_Q2['curriculum_detailed'] = actif_in_Q2.nbre_pres_for_inter.map(
    curriculum_detailed)
actif_in_Q2['curriculum'] = actif_in_Q2.nbre_pres_for_inter.map(
    curriculum)
actif_in_Q2['condom'] = actif_in_Q2.apply(
    lambda df: condom(df), axis=1)
actif_in_Q2['hts'] = actif_in_Q2.number_test_date_in_the_interval.map(
    hts)
actif_in_Q2['contraceptive'] = actif_in_Q2.number_contraceptive_reception_in_the_interval.map(
    contraceptive)
actif_in_Q2['post_violence_care'] = actif_in_Q2.apply(
    lambda df: postcare(df), axis=1)
actif_in_Q2['socioeco_app'] = actif_in_Q2.apply(
    lambda df: socioeco(df), axis=1)
actif_in_Q2['prep'] = actif_in_Q2.number_prep_initiation_date_in_the_interval.map(
    prep)

actif_in_Q2['ps_1014'] = actif_in_Q2.apply(
    lambda df: prim_1014(df), axis=1)
actif_in_Q2['ps_1519'] = actif_in_Q2.apply(
    lambda df: prim_1519(df), axis=1)
actif_in_Q2['ps_2024'] = actif_in_Q2.apply(
    lambda df: prim_2024(df), axis=1)
actif_in_Q2['secondary_1014'] = actif_in_Q2.apply(
    lambda df: sec_1014(df), axis=1)
actif_in_Q2['secondary_1519'] = actif_in_Q2.apply(
    lambda df: sec_1519(df), axis=1)
actif_in_Q2['secondary_2024'] = actif_in_Q2.apply(
    lambda df: sec_2024(df), axis=1)
actif_in_Q2['complete_1014'] = actif_in_Q2.apply(
    lambda df: comp_1014(df), axis=1)
actif_in_Q2['complete_1519'] = actif_in_Q2.apply(
    lambda df: comp_1519(df), axis=1)
actif_in_Q2['complete_2024'] = actif_in_Q2.apply(
    lambda df: comp_2024(df), axis=1)

# pure case

actif_in_Q2.date_interview = to_datetime(actif_in_Q2.date_interview)
actif_in_Q1.date_interview = to_datetime(actif_in_Q1.date_interview)
actif_in_Q1['complete_at_least'] = actif_in_Q1.apply(
    lambda df: complete_at_least(df), axis=1)
actif_in_Q2['complete_at_least'] = actif_in_Q2.apply(
    lambda df: complete_at_least(df), axis=1)
actif_in_Q1['isEnrolledQ2'] = actif_in_Q1.date_interview.map(isEnrolledQ2)
actif_in_Q2['isEnrolledQ2'] = actif_in_Q2.date_interview.map(isEnrolledQ2)

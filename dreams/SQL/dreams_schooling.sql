use caris_db;
set @start_date="2023-10-01";
set @end_date="2024-09-30";

SELECT 
    dm3.id_patient
FROM
    dream_member dm3
        INNER JOIN
    patient p1 ON p1.id = dm3.id_patient
        INNER JOIN
    gardening_beneficiary gb ON gb.code_dreams = p1.patient_code
WHERE
    (gb.date_modified BETWEEN @start_date AND @end_date)
        AND (gb.date_closed IS NULL)
GROUP BY dm3.id_patient

SELECT 
    vhs.*,
    vhs.a7_score + vhs.12_score + vhs.12a_score + vhs.12b_score + vhs.14a_score + vhs.15a_score AS total_score
FROM
    caris_db.view_hts_score vhs;
    
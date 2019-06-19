SELECT
    wt.wmech_db_id
    || '-'
    || wt.db_id AS wm_wt_db_id,
    md.server_path,
    md.db_id
FROM
    work_tasks               wt
    JOIN wt_work_instr_elements   wwie ON ( wwie.wtask_wmech_db_id = wt.wmech_db_id
                                          AND wwie.wtask_db_id = wt.db_id )
    JOIN media_details            md ON md.db_id = wwie.meddet_db_id
where
    md.create_date > :yesterday
    and lower(md.server_path) like '%.doc'
ORDER BY
    wmech_db_id DESC
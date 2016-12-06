# mimic III data access functions
# - postgres library is needed
# Honghan 2016

import psycopg2
import datetime
import json

# db connection string
db_cnn_str = "dbname='mimic' user='postgres' password='' host='localhost'"

# query templates
# patient cohort by diagnosis template
qt_patient_cohort = """
select distinct p.*
from mimiciii.diagnoses_icd d, mimiciii.patients p
where d.icd9_code = '{}'
and p.subject_id=d.subject_id
"""

# hospital admissions by diagnosis template
qt_admissions_by_diagnosis = """
select distinct a.hadm_id, a.admittime, a.dischtime, a.deathtime
from mimiciii.diagnoses_icd d, mimiciii.admissions a
where d.icd9_code = '{}'
and d.hadm_id=a.hadm_id
"""

# get admission labevents
qt_labevents_by_admssion = """
select l.*, d.label, d.category
from mimiciii.labevents l, mimiciii.d_labitems d
where hadm_id={}
and l.itemid = d.itemid
order by l.itemid, charttime
"""


# create db connection
def get_db_connection():
    db_conn = psycopg2.connect(db_cnn_str)
    cursor = db_conn.cursor()
    return {'db_conn': db_conn, 'cursor': cursor}


# release connection resources
def release_db_connection(cnn_obj):
    cnn_obj['db_conn'].close()


# query db to get data as a list of dic objects
def query_data(query, container):
    """
    query db to get data
    :param query: sql query
    :param container: the list container to save each row as a dic object
    :return:
    """
    conn_dic = get_db_connection()
    conn_dic['cursor'].execute(query)
    rows = conn_dic['cursor'].fetchall()
    columns = [column[0] for column in conn_dic['cursor'].description]
    for row in rows:
        obj = dict(zip(columns, row))
        for k in obj:
            if type(obj[k]) is datetime.datetime:
                obj[k] = str(obj[k].strftime("%Y-%m-%d %H:%M:%S"))
        container.append(obj)
    release_db_connection(conn_dic)


def get_patient_cohort(icd9_code):
    patients = []
    query_data(qt_patient_cohort.format(icd9_code), patients)
    return patients


def get_admissions(icd9_code):
    adms = []
    query_data(qt_admissions_by_diagnosis.format(icd9_code), adms)
    return adms


def get_labevents_by_admission(hadm_id):
    les = []
    query_data(qt_labevents_by_admssion.format(hadm_id), les)
    return les


if __name__ == "__main__":
    adms = get_admissions('99592')
    print '#admissions with diagnose of severe sepsis {}'.format(len(adms))
    print json.dumps(get_labevents_by_admission(adms[0]['hadm_id']))

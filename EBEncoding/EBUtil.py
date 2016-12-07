# Episode Bitwise Encoding Utils - an use case in ADE analytics
# but most functions can be reused in other similar situations
# Sep 2016
# Honghan Wu @KCL
#
# Util/helper funtions
#

import csv
import codecs
from datetime import datetime
from os import listdir
from os.path import isfile, join, splitext
from EBEncoding import EBEncoding, EBVector
import numpy as np
from scipy.sparse import dok_matrix, linalg, csc
import scipy.io as sio
import plotly.graph_objs as go
import plotly.plotly as py
import gutils as gu
import matplotlib.pyplot as plt
import math


# the known causes of enuresis from sider database
known_causes_enuresis = ["Aripiprazole", "Quetiapine", "Olanzapine",
                "Risperidone", "Clozapine", "Ropinirole", "Paliperidone", "Loxapine",
                "Mirtazapine", "Amoxapine", "Valproic Acid", "Zonisamide", "Citalopram",
                "Iloperidone", "Fluvoxamine", "Bupropion"]

# parse the string to datetime
def parse_date_str(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')


# don't do any temporal encoding
def simpleEncode(dStart, dEnd, dADE):
    return 1


# group the csv data rows by event id
# encode the drug episodes using encoding approaches
def encodeFile(filenamePrefix):
    count = 0
    with codecs.open(filenamePrefix + '.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames
        header.append('encoded')
        with codecs.open(filenamePrefix + '_o.csv', mode='w', encoding='utf-8') as ofile:
            writer = csv.DictWriter(ofile, fieldnames=header)
            writer.writeheader()
            for row in reader:
                # print row
                d1 = parse_date_str(row['EpisodeStartDate'])
                d2 = parse_date_str(row['EpisodeEndDate'])
                de = parse_date_str(row['ADE_Date'])
                row['encoded'] = EBEncoding.get_encoding(d1, d2, de).coding_value()
                writer.writerow(row)
                count += 1
                if count % 1000 == 0:
                    print('processed ', count, '...')


# generate sparse matrix from encoded ADE csv data file
def gen_sparse_matrix(file_path, mat_file=None):
    """
    generate a sparse (episode x event) matrix from a given csv file, which should take the format
    `Drug,EpisodeStartDate,EpisodeEndDate,id,type,ADE_Date`
    :param file_path: csv file path
    :param mat_file: (optional) matrix serialisation path
    :return:
    """
    drugs = []
    col_vecs = []
    with codecs.open(file_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames
        prev_eid = None
        eid_data = {}
        for row in reader:
            d = row['Drug']
            eid = row['id']
            coded = row['encoded']
            # d1 = parse_date_str(row['EpisodeStartDate'])
            # d2 = parse_date_str(row['EpisodeEndDate'])
            # de = parse_date_str(row['ADE_Date'])
            # eb = EBEncoding(int(coded), 32)
            # eb.scale_down(4)
            # coded = eb.coding_value()
            # coded = eb.score_bitorder()
            if eid != prev_eid:
                if prev_eid is not None:
                    col_vecs.append(eid_data)
                eid_data = {}
                prev_eid = eid

            if d not in drugs:
                drugs.append(d)
            eid_data[d] = coded

    drugs = sorted(drugs)
    d2idx = {}
    for i in range(len(drugs)):
        d2idx[drugs[i]] = i
    print 'data read. generating matrix ({}x{})...'.format(len(drugs), len(col_vecs))
    episode_event_matrix = dok_matrix((len(drugs), len(col_vecs)), dtype=np.float64)
    for i in range(len(col_vecs)):
        for d in col_vecs[i]:
            idx = d2idx[d]
            episode_event_matrix[idx, i] = col_vecs[i][d]

    if mat_file is not None:
        # save matrix
        print 'saving matrix...'
        sio.savemat(mat_file, {'drug-ade': episode_event_matrix, 'drugs': drugs})
    print 'all done'


def load_matrix(mfile, key):
    return sio.loadmat(mfile)[key]


# visualise top 100 columnes of given matrix using plotly service
def visualise_drug_ade_matrix(episode_matrix, fn):
    print('scatter the original matrix...')
    data = [
        go.Heatmap(
            z=episode_matrix.toarray()[:, :100]
        )
    ]
    py.iplot(data, filename=fn)


# do SVD analysis on given matrix (sparse)
def do_svd_analysis(episode_matrix, episode_labels, fn,
                    filter_func=None, known_knowledge=None,
                    label_conversion_map=None):
    """
    do svd analysis on given episode matrix and save the top k singular vector to plot.ly
    :param episode_matrix: rows are episodes (e.g., medications) and columns are events (e.g., ADEs)
    :param episode_labels: the labels of rows
    :param fn: the name of file to be saved in your plot.ly account
    :param filter_func: (optional) filer the singular vector
    :param known_knowledge: (optional, but needed if filter func is provided) the list of
      row labels that should be ignored
    :param label_conversion_map: the map to convert a set of labels into another set
    :return:
    """
    print 'doing svd...'
    u, s, v = linalg.svds(episode_matrix, k=50)
    print 'svd done, doing visualisation...'
    vec_pca = np.matrix(u) * np.diag(s)  # * np.matrix(v)
    arr_pca = np.array(vec_pca)
    traces = []

    x_arr = [l.strip() for l in episode_labels] if label_conversion_map is None \
        else [label_conversion_map[l.strip()] if l.strip() in label_conversion_map
              else '$'+l for l in episode_labels]
    x_dic = {}
    x_list = []
    for i in range(len(x_arr)):
        x = x_arr[i]
        x_dic[x] = [i] if x not in x_dic else x_dic[x] + [i]
        if x not in x_list:
            x_list.append(x)
    x_list = sorted(x_list)
    for i in range(5):
        y_vals = u[:, i] if filter_func is None else filter_func(u[:, i], episode_labels, known_causes=known_knowledge)
        y_arr = []
        for j in range(len(x_list)):
            y = 0
            for idx in x_dic[x_list[j]]:
                y += y_vals[idx]
            y_arr.append(y)
        traces.append(go.Bar(
            x=x_list,
            y=y_arr
        ))
        print ' -{}- \n'.format(i)
    py.plot(traces, filename=fn)
    print 'all done'


# filtered out known knowledge from Singular Vectors
def filter_known_knowledge(arr, drugs, known_causes):
    filtered_vals = []
    for i in range(len(arr)):
        label_arr = drugs[i].split(' ')
        bKnown = False
        for l in label_arr:
            if l in known_causes:
                bKnown = True
                break
        if abs(arr[i]) > 0.1 and not bKnown:
            filtered_vals.append(arr[i])
            print drugs[i]
        else:
            filtered_vals.append(0)
    return filtered_vals


# filtered out known knowledge from Singular Vectors
def y_threshold_filter(arr, drugs, known_causes):
    filtered_vals = []
    for i in range(len(arr)):
        if abs(arr[i]) > 0.1:
            filtered_vals.append(arr[i])
        else:
            filtered_vals.append(0)
    return filtered_vals


# generate EBEncoding for csv data
def process_csv_files(mypath='./'):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for f in onlyfiles:
        arr = splitext(f)
        if len(arr) == 2 and arr[1] == '.csv' and not (arr[0].endswith('_o')):
            print 'processing', mypath + arr[0]
            encodeFile(mypath + arr[0])


# doing the intersection
def self_intersect(idx, arr, container, file_path):
    ev = EBVector([int(r[idx]) for r in arr], 32)
    ret, keys = ev.intersection(ev, 3)
    container.append({'ret': ret, 'keys': keys})
    if len(container) % 1000 == 0:
        print '{} done.'.format(len(container))


# call back function when drug-drug interaction matrix is done
def intersection_call_back(a, ret, file_path):
    all_keys = set()
    ades = []
    for ro in ret:
        all_keys |= ro['keys']
        ades.append(ro['ret'])
    keys = sorted(all_keys)
    key2index = {}
    for i in range(len(keys)):
        key2index[keys[i]] = i
    drug_event_matrix = dok_matrix((len(all_keys), len(ades)), dtype=np.float64)
    for i in range(len(ades)):
        for rk in ades[i]:
            drug_event_matrix[key2index[rk], i] = ades[i][rk]
    sio.savemat(file_path, {'drug-drug-ADE': drug_event_matrix, 'keys': keys})
    print('all done')


# compute drug-drug interaction matrix by using EBVector's intersection operator
def compute_episode_interaction_matrix(mat_file, mat_key, thread_num, output_file):
    m = load_matrix(mat_file, mat_key)
    rows, cols = m.shape
    rets = []
    arr_m = m.toarray()
    gu.multi_thread_tasking([i for i in range(cols)], thread_num, self_intersect,
                            args=[arr_m, rets, output_file],
                            callback_func=intersection_call_back)


def do_single_drug_ade_analytics():
    # load drug name list
    m_dics = sio.loadmat('./data/drug-ade.mat')
    drugs = m_dics['drugs']
    matrix = m_dics['drug-ade']
    # load drug cats
    drug_cats = gu.load_json_data('./data/drug_cat.json')
    prim_dic = {}
    for d in drug_cats:
        prim_dic[d] = drug_cats[d]['primary']
    # do SVD analysis
    do_svd_analysis(matrix, drugs, 'Drug-ADE-SVD-Vectors', #label_conversion_map=prim_dic,
                    filter_func=y_threshold_filter)


# do medication ADE analysis
def do_drugdrug_ade_analysis():
    # load drug name list
    drugs = load_matrix('./data/drug-ade.mat', 'drugs')
    # load drug-drug mat dictionary
    m_dics = sio.loadmat('./data/drug_drug_ADE.mat')
    # convert index pairs into drug name pairs
    keys = m_dics['keys']
    drug_pairs = []
    # load drug cats
    drug_cats = gu.load_json_data('./data/drug_cat.json')

    for k in keys:
        arr = k.strip().split(' ')
        # names= [drugs[int(arr[0])].strip(), drugs[int(arr[1])].strip()]
        names = sorted([(drug_cats[drugs[int(idx)].strip()]['primary']
                         if drugs[int(idx)].strip() in drug_cats else 'drug') for idx in arr])
        drug_pairs.append('{} - {}'.format(names[0], names[1]))
    # do SVD analysis
    do_svd_analysis(m_dics['drug-drug-ADE'], drug_pairs, #'drug_drug_ADE_filtered',
                    'drug-durg_primary_ADE_filtered',
                    filter_func=filter_known_knowledge,
                    known_knowledge=known_causes_enuresis)


def spike_func(x):
    y = []
    for i in range(len(x)):
        y.append(10 if len(x)/4 < i < len(x)/2 else 0)
    return y

def zero_func(x):
    return [0 for v in x]

def fourier_transform_encoding():
    Fs = 150.0;  # sampling rate
    Ts = 1.0 / Fs;  # sampling interval
    t = np.arange(0, 1, Ts)  # time vector
    ff = 5
    # sin = np.sin(2 * np.pi * t * ff + np.pi / 6)
    sin = zero_func(t)
    print sin
    sp = np.fft.fft(sin)
    freq = np.fft.fftfreq(t.shape[-1])
    plt.plot(t, sin)
    plt.show()
    arr = [0 if v < 1.0/10000 else v for v in abs(sp)[range(len(sp)/2)]]
    phase = [0 if abs(v) < 1.0/10000 else math.atan2(v.imag, v.real) * 180 / np.pi + 90 for v in sp[range(len(sp)/2)]]
    print len(arr)
    print arr
    print phase


def save_drug_cat():
    fp = './data/drug_cat.csv'
    rows = gu.read_csv_file(fp)
    drug_dict = {}
    for r in rows:
            drug_dict[r['Generic_Name']] = {'third': r['Third_Category'],
                                            'second': r['Secondary_Category'],
                                            'primary': r['Primary_Category']}
    gu.save_json_obj(drug_dict, './data/drug_cat.json')

if __name__ == "__main__":
    # do_drugdrug_ade_analysis()
    # do_single_drug_ade_analytics()
    fourier_transform_encoding()




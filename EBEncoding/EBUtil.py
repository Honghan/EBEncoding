from xlrd import open_workbook
from sets import Set
import re, urllib, ctypes, csv, codecs, random
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile, join, splitext


# parse the string to datetime
def parseDate(dStr):
    return datetime.strptime(dStr, '%Y-%m-%d %H:%M:%S.%f')


# using each bit to indicate the presence of a drug usage at
# one particular day. High oder is closer to the ADE date.
def encodeDrugEpisode(dStart, dEnd, dADE):
    curD = dADE
    code = 0
    interval = 1  # change the setting to compress the timeline
    bIn = False
    for i in range(0, 30):
        if curD >= dStart and curD <= dEnd:
            bIn = True
        if i % interval == 0:
            if bIn:
                code = code | (1 << ((31 - i) / interval))
            bIn = False
        curD = curD + timedelta(days=-1)
    return code


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
                d1 = parseDate(row['EpisodeStartDate'])
                d2 = parseDate(row['EpisodeEndDate'])
                de = parseDate(row['ADE_Date'])
                row['encoded'] = encodeDrugEpisode(d1, d2, de)
                writer.writerow(row)
                count += 1
                if (count % 1000 == 0):
                    print('processed ', count, '...')


mypath = './'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for f in onlyfiles:
    arr = splitext(f)
    if len(arr) == 2 and arr[1] == '.csv' and not (arr[0].endswith('_o')):
        print 'processing', mypath + arr[0]
        encodeFile(mypath + arr[0])

print 'done'

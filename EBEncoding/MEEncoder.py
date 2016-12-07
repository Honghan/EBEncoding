from EBEncoding import EBEncoding
import mimicdao as md
import EBUtil as eu
from datetime import datetime, timedelta


def encode(event_list, coordinate_time, e_dt_attr, encoding_size, unit_in_hours,
           func_get_type=lambda event: 'event',
           func_is_abnormal=lambda event: event['flag'] == 'abnormal'):
    """
    encoding a list of abnormal events
    :param event_list: the list of events, each should have a) a time attribute identified by 'e_dt_attr'; b)
      a 'flag' attribute whose value indicates whether the event is 'abnormal' or not; c)
    :param coordinate_time: the coordinate time to do the encoding
    :param e_dt_attr: the attribute name
    :param encoding_size: size of the encoding
    :param unit_in_hours: the size one unit in hours
    :param func_get_type: a function to get the type of each event, which will be used to merge encodings
    :param func_is_abnormal: a function to check whether an event is abnormal or not; only abnormal events will
      be encoded
    :return: a dictionary
    """
    event_encodings = {}
    dt_format = '%Y-%m-%d %H:%M:%S'
    for idx in range(len(event_list)):
        t = func_get_type(event_list[idx])
        if t not in event_encodings:
            event_encodings[t] = EBEncoding(0, encoding_size)
        cur_encoding = event_encodings[t]
        if func_is_abnormal(event_list[idx]):
            et = preprocessing_datetime(eu.parse_date_str(event_list[idx][e_dt_attr], format_str=dt_format))
            cet = coordinate_time
            # print et, cet, event_list[idx]['category'], event_list[idx]['label'], event_list[idx]['flag']
            encoding = encoding_resolution(et, cet, time_delta=timedelta(hours=-unit_in_hours), num_bits=encoding_size)
            event_encodings[t] = EBEncoding.eb_or(encoding, cur_encoding)
    return event_encodings


def encoding_resolution(event_time, coord_time, time_delta=timedelta(hours=-1), num_bits=48):
    return EBEncoding.get_encoding(
        event_time, event_time - time_delta, coord_time, time_delta, num_bits=num_bits)


def preprocessing_datetime(dt):
    """
    preprocessing datetime by ignoring the finer grained components than hours
    :param dt: datetime to be processed
    :return: more coarse grained datetime by removing minutes, seconds and milliseconds
    """
    return dt.replace(minute=0, second=0, microsecond=0)


def get_admission_lab_event_encodings(adm, days_to_be_encoded, coding_size):
    """
    given an admission id, read all lab events and encode
    all abnormal events
    :param adm:
    :param days_to_be_encoded: how many days of events to be encoded (after the admission date)
    :param coding_size: the size (in bits) of the encoding
    :return:
    """
    unit_hours = days_to_be_encoded * 24 / coding_size
    anchor_time = preprocessing_datetime(
        eu.parse_date_str(
            adm['admittime'], format_str='%Y-%m-%d %H:%M:%S') + timedelta(days=days_to_be_encoded))
    lab_events = md.get_labevents_by_admission(adm['hadm_id'])
    return encode(lab_events, anchor_time, 'charttime', coding_size, unit_hours,
                  func_is_abnormal=lambda event: event['flag'] == 'abnormal',
                  func_get_type=lambda event: '{} - {}'.format(event['category'], event['label'])
                                #lambda event: event['label']
                  )


def get_admission_chart_event_encodings(adm, days_to_be_encoded, coding_size):
    """
    given an admission id, read all chart events and encode
    all abnormal events
    :param adm:
    :param days_to_be_encoded: how many days of events to be encoded (after the admission date)
    :param coding_size: the size (in bits) of the encoding
    :return:
    """
    unit_hours = days_to_be_encoded * 24 / coding_size
    anchor_time = preprocessing_datetime(
        eu.parse_date_str(
            adm['admittime'], format_str='%Y-%m-%d %H:%M:%S') + timedelta(days=days_to_be_encoded))
    chart_events = md.get_chartevents_by_admission(adm['hadm_id'])
    return encode(chart_events, anchor_time, 'charttime', coding_size, unit_hours,
                  func_is_abnormal=lambda event: event['warning'] == 1,
                  func_get_type=lambda event: '{} - {}'.format(event['category'], event['label'])
                  #lambda event: event['label']
                  )


def test_sepsis_encoding():
    adms = md.get_admissions('99592')  # severe sepsis diagnosis
    print '#admissions with diagnose of severe sepsis {}'.format(len(adms))
    print 'The first admission object:\n {}'.format(adms[0])

    print 'the lab events encoding of the first admission is as follows:'
    time_period_to_encode = 10  # in days
    encoding_size = 120  # number of bits in each encoding
    t2encodings = get_admission_lab_event_encodings(adms[0], time_period_to_encode, encoding_size)
    for t in t2encodings:
        print '{}\n{}'.format(t, ''.join(t2encodings[t].get_bin_list()))

    print 'chart events encoding is as follows:'
    t2encodings = get_admission_chart_event_encodings(adms[0], time_period_to_encode, encoding_size)
    for t in t2encodings:
        print '{}\n{}'.format(t, ''.join(t2encodings[t].get_bin_list()))


if __name__ == '__main__':
    test_sepsis_encoding()



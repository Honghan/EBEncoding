from os import listdir
from os.path import isfile, join
import Queue
import threading
import json
import codecs


# list files in a folder and put them in to a queue for multi-threading processing
def multi_thread_process_files(dir_path, file_extension, num_threads, process_func,
                               proc_desc='processed', args=None, multi=None,
                               file_filter_func=None, callback_func=None):
    onlyfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    num_pdfs = 0
    files = None if multi is None else []
    lst = []
    for f in onlyfiles:
        if f.endswith('.' + file_extension) if file_filter_func is None \
                else file_filter_func(f):
            if multi is None:
                lst.append(join(dir_path, f))
            else:
                files.append(join(dir_path, f))
                if len(files) >= multi:
                    lst.append(files)
                    files = []
            num_pdfs += 1
    if files is not None and len(files) > 0:
        lst.append(files)
    multi_thread_tasking(lst, num_threads, process_func, proc_desc, args, multi, file_filter_func, callback_func)


# do a task in multithreading mode
def multi_thread_tasking(lst, num_threads, process_func,
                         proc_desc='processed', args=None, multi=None,
                         file_filter_func=None, callback_func=None):
    """
    multithreading task execution
    :param lst: a list of job objects, each of which is a job or a handle to get a job. Specifically, one object will
    be passed to the call to the process_func.
    :param num_threads: number of threads
    :param process_func: the main function for doing a single job at a time
    :param proc_desc: the name of the task
    :param args: a list of additional arguments to be used in process_func
    :param multi:
    :param file_filter_func:
    :param callback_func: the call back function to be called when all jobs are done
    :return:
    """
    num_pdfs = len(lst)
    pdf_queque = Queue.Queue(num_pdfs)
    print('putting list into queue...')
    for item in lst:
        pdf_queque.put_nowait(item)
    thread_num = min(num_pdfs, num_threads)
    arr = [process_func] if args is None else [process_func] + args
    arr.insert(0, pdf_queque)
    print('queue filled, threading...')
    for i in range(thread_num):
        t = threading.Thread(target=multi_thread_do, args=tuple(arr))
        t.daemon = True
        t.start()

    print('waiting jobs to finish')
    pdf_queque.join()
    print('{0} files {1}'.format(num_pdfs, proc_desc))
    if callback_func is not None:
        callback_func(*tuple(args))


def multi_thread_do(q, func, *args):
    while True:
        p = q.get()
        try:
            func(p, *args)
        except:
            print u'error doing {0} on {1}'.format(func, p)
        q.task_done()


def save_json_obj(obj, file_path):
    with codecs.open(file_path, 'w', encoding='utf-8') as wf:
        json.dump(obj, wf)


def main():
    pass

if __name__ == "__main__":
    main()

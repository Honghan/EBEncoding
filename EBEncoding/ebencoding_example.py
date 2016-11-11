from EBEncoding import EBEncoding, EBVector
import numpy as np


def test_correlation():
    v1 = 0b01110000
    v2 = 0b00011101
    e1 = EBEncoding(v1, 8)
    e2 = EBEncoding(v2, 8)
    xval = EBEncoding.xcorr(e1, e2)
    print '\n>>> example of cross correlation between two episodes'
    print 'e1: [%s]' % ''.join(e1.get_bin_list())
    print 'e2: [%s]' % ''.join(e2.get_bin_list())
    print 'cross correlation of e1 and e2 is %s' % xval
    print 'e2 is %s units earlier' % EBEncoding.num_units_earlier(xval, e1)
    print 'the time delay is %s' % EBEncoding.time_delay(xval)


# sample usages of the EBEncoding class and EBVector class
def test_eb():
    print '\n>>create a EBEncoding instance'
    e = EBEncoding(123, 8) # arg1 - the encoding value, arg2 - the number of bits of this encoding
    print 'Value {} is encoded as {}, its score is {}'.format(
        e.coding_value(),  # get the int value of the encoding object
        ''.join(e.get_bin_list()),  # get the binary string of the encoding
        e.score_bitorder()  # get the score of the encoding
        )

    print '\n>>scale down an encoding'
    e.scale_down(3)
    print 'Value {} is encoded as {}, its score is {}'.format(
        e.coding_value(),  # get the int value of the encoding object
        ''.join(e.get_bin_list()),  # get the binary string of the encoding
        e.score_bitorder()  # get the score of the encoding
    )

    print '\n>>create a EBEncoding vector'
    vec1 = EBVector([7, 16, 32], 8)
    for i in range(len(vec1.coding_list())):
        print ''.join(vec1.get_coding(i).get_bin_list())

    print '\n>>compute intersection with the vector itself without a post expanding'
    ret_dic, nonzero_labels = vec1.intersection(vec1, 0)
    print 'intersection results of no post expanding: {}'.format(ret_dic)

    print '\n>>compute intersection with the vector itself with a two-bit post expanding'
    ret_dic, nonzero_labels = vec1.intersection(vec1, 2)
    print 'intersection results of two-bit expanding: {}'.format(ret_dic)

    print '\n>>transform a EBEncoding vector using a mapping matrix'
    ret_list = vec1.transform(np.matrix([[1, 1], [0, 1], [1, 0]]))
    for r in ret_list:
        print ''.join(r.get_bin_list())

if __name__ == "__main__":
    test_eb()
    test_correlation()

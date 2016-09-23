from EBEncoding import EBEncoding, EBVector
import numpy as np


# sample usages of the EBEncoding class and EBVector class
def test_eb():
    print '\n>>create a EBEncoding instance'
    e = EBEncoding(123, 8)
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

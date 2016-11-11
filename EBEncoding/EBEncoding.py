# Episode Bitwise Encoding
# May 2016
# Honghan Wu @KCL
#
# This encoding is designed for abstracting the medication
# episodes of a patient that are related to a certain event
# e.g., adverse drug event. Technically, it can be applied
# to any temporal events.

import math
from bitstring import BitArray
import numpy as np
from datetime import datetime, timedelta
from scipy.sparse import csc


# episode bitwise encoding class
class EBEncoding:
    """
    This class is designed for encoding episodic data and its operations
    The design and implementation was undergoing with a biomedical use case
    (adverse drug event analytics) in mind.
    However, it should be applied to any episodic data analytic scenarios.
    """

    def __init__(self, value, size):
        if value > 2**size - 1:
            raise Exception('value ({}) is too large to fit the size ({}) {}'.format(value, size, 2**size - 1))
        self.coding = value
        self.bit_size = size

    def size(self):
        return self.bit_size

    def magnitude(self):
        return bin(self.coding).count("1")

    def lshift(self, steps):
        return self.coding << steps

    def rshift(self, steps):
        return self.coding >> steps

    def coding_value(self):
        return self.coding

    def get_highest_bit_val(self):
        arr = BitArray(bin(self.coding))
        return 0 if len(arr) == 1 and arr[0] == 0 else 1 << len(arr) - 1

    def get_lowest_bit_val(self):
        arr = BitArray(bin(self.coding))
        idx = 0
        for i in range(len(arr)):
            if arr[len(arr) - i - 1]:
                idx = i
                break
        return 1 << idx

    # get the string list which lists the bits of the encoding with the highest bit starting from 0 position
    def get_bin_list(self):
        arr = BitArray(bin(self.coding))
        barr = ['0' if idx < self.size() - len(arr) else arr.bin[len(arr) - self.size() + idx]
                for idx in range(self.size())]
        return barr

    # scale down the encoding to reduce resolution
    def scale_down(self, bits2merge):
        """
        scale down the current encoding by merging consecutive bits
        :param bits2merge: the number of bits to be merged in each consecutive block starting from the highest order
        :return:
        """
        barr = self.get_bin_list()
        final_size = int(math.ceil(self.size() * 1.0 / bits2merge))
        result_coding = 0
        for i in range(final_size):
            num_one = barr[i * bits2merge: min((i + 1) * bits2merge, len(barr))].count("1")
            if num_one > 0:
                result_coding = (result_coding | (1 << (final_size - i - 1)))
        self.bit_size = final_size
        self.coding = result_coding

    # post expand is to expand the occurrences of the events(1s) in the encoding
    # it is useful to model the effects of those events, which last longer than events themselves
    def post_expand(self, num_bits):
        x = 1 << self.bit_size
        for i in range(num_bits):
            self.coding |= self.coding << 1
            x |= x << 1
        self.coding &= ~x

    # clone a new encoding instance from current one
    def clone(self):
        return EBEncoding(self.coding, self.size())

    # a scoring funciton to get importance quantity from the encoding
    # this is just an example to showcase how to score an encoded episode
    # users might define their own score functions based on their scenarios
    def score_bitorder(self):
        """
        a score function to calculate the importance of an encoding
        the score is simply the sum of order indices of non-zero bits.
        :return: the score value
        """
        score = 0
        for i in range(self.size()):
            if (1 << self.size() - i - 1) & self.coding != 0:
                score += self.size() - i
        return score

    @staticmethod
    def eb_and(e1, e2):
        if isinstance(e1, EBEncoding) and isinstance(e2, EBEncoding) and e1.size() == e2.size():
            v = e1.coding_value() & e2.coding_value()
            return EBEncoding(v, e1.size())
        else:
            raise Exception('one or more operands are not EBEncoding instances or they are not equally sized')

    @staticmethod
    def eb_or(e1, e2):
        if isinstance(e1, EBEncoding) and isinstance(e2, EBEncoding) and e1.size() == e2.size():
            v = e1.coding_value() | e2.coding_value()
            return EBEncoding(v, e1.size())
        else:
            raise Exception('one or more operands are not EBEncoding instances or they are not equally sized')

    @staticmethod
    def op_consistence(e1, e2):
        if not isinstance(e1, EBEncoding) or not isinstance(e2, EBEncoding) or e1.size() != e2.size():
            raise Exception('one or more operands are not EBEncoding instances or they are not equally sized')

    # compute the interaction of two episodic events - the co-occurrences of the two (post-expended) events
    # one usage example in biomedical scenario could be the drug-drug interaction
    @staticmethod
    def interaction(e1, e2, pe_bits):
        """
        post expand e1 and e2, then compute the interaction of the two post-expanded events
        :param e1: one episode encoding
        :param e2: the other episode encoding
        :param pe_bits: number of bits to post expand the two encodings
        :return: the interaction event
        """
        if e1.coding_value() == 0 or e2.coding_value() == 0:
            return EBEncoding(0, e1.size())
        EBEncoding.op_consistence(e1, e2)
        pe_e1 = e1.clone()
        pe_e1.post_expand(pe_bits)
        pe_e2 = e2.clone()
        pe_e2.post_expand(pe_bits)
        return EBEncoding.eb_and(pe_e1, pe_e2)

    @staticmethod
    def get_encoding(start_time, end_time, coordinate_time,
                     time_delta=timedelta(days=-1),
                     num_bits=32):
        cur = coordinate_time
        code = 0
        interval = 1  # change the setting to compress the timeline
        is_in = False
        for i in range(0, num_bits):
            if start_time <= cur <= end_time:
                is_in = True
            if i % interval == 0:
                if is_in:
                    code |= (1 << ((num_bits - 1 - i) / interval))
                is_in = False
            cur = cur + time_delta
        return EBEncoding(code, num_bits)

    @staticmethod
    # compute the cross correlation between two encoded episodes
    def xcorr(e1, e2):
        """
        the cross correlation is a metric to measure how two episodes are
        correlated. it can help derive their temporal relations, e.g.,
        begins earlier/later, overlaps, time delay analysis
        :param e1:
        :param e2:
        :return: a list of two-element-tuple, the first element is x value
         the second is the value of correlation(and op result)
        """
        # result sequence container
        ret = []
        x = 0
        # moving left
        max_size = max(len(BitArray(bin(e1.coding_value()))), len(BitArray(bin(e2.coding_value()))))
        w_e1 = EBEncoding(e1.coding_value(), max_size * 2)
        w_e2 = EBEncoding(e2.coding_value(), max_size * 2)
        t_e2 = w_e2.clone()
        while w_e1.get_highest_bit_val() >= t_e2.get_lowest_bit_val():
            r_and = EBEncoding.eb_and(w_e1, t_e2)
            ret.append( (x, r_and.coding_value()) )
            # shift e2 to the left until the and result becomes zero
            v2 = t_e2.lshift(1)
            t_e2 = EBEncoding(v2, w_e1.size())
            x += 1

        t_e2 = w_e2.clone()
        v2 = t_e2.rshift(1)
        t_e2 = EBEncoding(v2, w_e1.size())
        x = -1

        # moving right
        while w_e1.get_lowest_bit_val() <= t_e2.get_highest_bit_val():
            r_and = EBEncoding.eb_and(w_e1, t_e2)
            ret.append( (x, r_and.coding_value()) )
            # shift e2 to the left until the and result becomes zero
            v2 = t_e2.rshift(1)
            t_e2 = EBEncoding(v2, w_e1.size())
            x -= 1
        ret = sorted(ret, cmp=lambda v1, v2: v1[0] - v2[0])
        return ret

    @staticmethod
    def num_units_earlier(xcorr_val, e1):
        """
        calculate how many units e2 is earlier than e1 using their cross correlation
        results. if e2 is later than e1, a negative number will be returned.
        :param xcorr_val:
        :param e1:
        :return:
        """
        lv = e1.get_lowest_bit_val()
        max_x = 0
        for i in range(len(xcorr_val)):
            if xcorr_val[len(xcorr_val) - i - 1][1] & lv != 0:
                max_x = xcorr_val[len(xcorr_val) - i - 1][0]
                break
        return max_x

    @staticmethod
    def time_delay(xcorr_val):
        max_vals = []
        val_sorted = sorted(xcorr_val, cmp=lambda v1, v2: v2[1] - v1[1])
        max_vals.append(val_sorted[0])
        for i in range(1, len(val_sorted), 1):
            if val_sorted[i][1] == val_sorted[0][1]:
                max_vals.append(val_sorted[i])
        return max_vals

# the vector of EBEncoding
class EBVector:
    """
    Provide some operations for EBEncoding Vector
    """
    def __init__(self, eb_list, coding_size=32):
        self.ebvec = eb_list

        self.is_sparse = isinstance(eb_list, csc.csc_matrix)
        if not self.is_sparse and not isinstance(eb_list, list):
            raise Exception('eb_list should be either a list or a csc_matrix')
        self.coding_size = coding_size

    def get_coding(self, index):
        if self.is_sparse:
            return EBEncoding(int(self.ebvec[index, 0]), self.coding_size)
        else:
            return EBEncoding(self.ebvec[index], self.coding_size)

    def get_size(self):
        if self.is_sparse:
            m, n = self.ebvec.shape
            return m
        else:
            return len(self.ebvec)

    def coding_list(self):
        return self.ebvec

    # transform an EBEncoding vector by a dimension mapping matrix
    def transform(self, dm):
        """
        transform a vector of EBEncoding by a matrix that defines the dimension mappings
        :param dm: the dimension mapping matrix
        :return: the transformed vector
        """
        eb_vec = self.ebvec
        ret_list = []
        t_dm_arr = dm.getT().getA()
        for i in range(len(t_dm_arr)):
            merged = 0
            for j in range(len(eb_vec)):
                merged |= self.get_coding(j).coding_value() * t_dm_arr[i][j]
            ret_list.append(EBEncoding(merged, self.get_coding(0).size()))
        return ret_list

    # doing pair-wise intersection between this instance and other_vec
    def intersection(self, other_vec, pe_bits, labels1=None, labels2=None):
        """
        pair-wise intersection calculation between this and another EBEncoding Vector
        :param other_vec: the other vector used to compute intersection
        :param pe_bits: number of bits to post expand each encoding before doing intersection
        :param labels1: labels of current encoding vector
        :param labels2: labels of other_vec encoding vector
        :return: a two-element tuple:
         a) the dictionary of intersected vectors with the keys being none-zero labels
         in the form 'label1 - label2' if label paramenters were given, otherwise 'index1 index2';
         b) the keys of none-zero encodings.
        """
        if self.get_size() != other_vec.get_size():
            raise Exception('intersecting with an incompatible vector')

        ret_list = {}
        nonzero_keys = set()
        for i in range(self.get_size()):
            for j in range(i + 1, self.get_size()):
                key = '{} {}'.format(i, j) if labels1 is None or labels2 is None else \
                    '{} - {}'.format(labels1[i], labels2[j])
                inter_coding = EBEncoding.interaction(self.get_coding(i), other_vec.get_coding(j), pe_bits)
                if inter_coding.coding_value() != 0:
                    nonzero_keys.add(key)
                    ret_list[key] = inter_coding.coding_value()
        return ret_list, nonzero_keys


if __name__ == "__main__":
    pass

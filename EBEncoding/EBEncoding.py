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


# episode bitwise encoding class
class EBEncoding:
    """
    This class is designed for encoding episodic data and its operations
    The design and implementation was undergoing with a biomedical use case (adverse drug event analytics) in mind.
    However, it should be applied to any episodic data analytic scenarios.
    """

    def __init__(self, value, size):
        if value > math.pow(2, size + 1) - 1:
            raise Exception('value ({}) is too large to fit the size ({})'.format(value, size))
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
        print ''.join(barr)
        final_size = int(math.ceil(self.size() * 1.0 / bits2merge))
        result_coding = 0
        for i in range(final_size):
            num_one = barr[i * bits2merge: min((i + 1) * bits2merge, len(barr))].count("1")
            if num_one > 0:
                result_coding = (result_coding | (1 << (final_size - i - 1)))
        self.bit_size = final_size
        self.coding = result_coding
        print 'result:', ''.join(self.get_bin_list())

    # post expand is to expand the occurrences of the events(1s) in the encoding
    # it is useful to model the effects of those events, which last longer than events themselves
    def post_expand(self, num_bits):
        for i in range(num_bits):
            self.coding |= self.coding << 1

    # clone a new encoding instance from current one
    def clone(self):
        return EBEncoding(self.coding, self.size())

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
        EBEncoding.op_consistence(e1, e2)
        pe_e1 = e1.clone()
        pe_e1.post_expand(pe_bits)
        pe_e2 = e2.clone()
        pe_e2.post_expand(pe_bits)
        return EBEncoding.eb_and(pe_e1, pe_e2)


def test_eb():
    e = EBEncoding(678, 10)
    e1 = EBEncoding(600, 10)
    r = EBEncoding.interaction(e, e1, 1)

    print ''.join(e.get_bin_list())
    print ''.join(e1.get_bin_list())
    print ''.join(r.get_bin_list())


if __name__ == "__main__":
    test_eb()

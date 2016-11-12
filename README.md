# EBEncoding - efficient bitwise encoding for temporal (medical) data
Episode Bitwise Encoding is an encoding method designed for abstracting multiple medication episodes of a patient related to a certain event, e.g., an adverse drug event. This being said, such encoding is actually domain independent and can be applied to any temporal events. 

The motivation of such encoding is to make time series data easy to be consumed. One time series (e.g., a drug usage in past months) can be encoded as one numberic value. Multiple time series (e.g., multipharmacy) can be encoded as a vector. Therefore, after encoded, such data can be easily analysed (e.g., used in off-the-shelf machine learning algorithms). In our first use case, it is used for predicting adverse drug events for patients with mental health disorders.

## updates
- (11 November 2016) Cross correlation (similar to [the correlaiton in signal processing](https://en.wikipedia.org/wiki/Cross-correlation)) between two encodings is implemented. The correlation result is a list of 2-element tuple, of which the first element is the time shift and the second is the value of the correlation based on the time shift. This correlation enables the calculation of various time correlations between two encodings, e.g., which one is earlier than the other and how many time units; time delay analysis: at what time shift the correlation value achieves the maximum value. Also, a negative time delay analysis is on its way, which will be very useful for analysing the effectiveness of treatment episodes for certain symptoms/disorders.
  An example of usage can be found at the function of `test_correlation()` in [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/ebencoding_example.py).
- (23 September 2016) Define classess of EBEncoding and EBVector with opertators. The update was put on a new branch, which was set as the default branch. A sample usage file was added and the applicaiton of the encoding/vectors/matrix in Adverse Drug Event analytics was implemented in the `EBUtils.py`.

## Usage
The EBEncoding.py contains the encoding class and vector class definition. Two usage examples:
- the general usage example is available [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/ebencoding_example.py)
- the application of the encoding in Adverse Drug Event Analytics is [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/EBUtil.py)

## Analytics using the coding
- [Association Analysis of Adverse Drug Events and Polyphamacy](http://honghan.info/kcl/ade/) 
- Drug-drug interaction analysis: using SVD (Singular Value Decomposition) on the matrix of drug-drug interaction Episode Encodings over 47k Adverse Events has revealed some potential *new* knowledge. The top 5 singular vectors after removing known causes of the ADE are visualised [here](https://plot.ly/~honghan.wu/10/). The absolute y values represent the significances of each drug pair in terms of its correlation to the adverse event. (This study is an ongoing work and more details will be updated soon.)

##Questions?
This is my ongoing work (2016) at Kings College London. Any questions please email: honghan.wu@kcl.ac.uk.

##citation
Honghan Wu, Zina Ibrahim, Ehtesham Iqbal and Richard Dobson. Predicting Adverse Events from Multiple and Dynamic Medication Episodes - a preliminary result in a large mental health registry. Accepted by IJCAI 2016 - Workshop on Knowledge Discovery in Healthcare Data.

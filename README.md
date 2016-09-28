# EBEncoding - efficient bitwise encoding for temporal (medical) data
Episode Bitwise Encoding is an encoding method designed for abstracting multiple medication episodes of a patient related to a certain event, e.g., an adverse drug event. This being said, such encoding is actually domain independent and can be applied to any temporal events. 

The motivation of such encoding is to make time series data easy to be consumed. One time series (e.g., a drug usage in past months) can be encoded as one numberic value. Multiple time series (e.g., multipharmacy) can be encoded as a vector. Therefore, after encoded, such data can be easily analysed (e.g., used in off-the-shelf machine learning algorithms). In our first use case, it is used for predicting adverse drug events for patients with mental health disorders.

## updates
- (23 September 2016) Define classess of EBEncoding and EBVector with opertators. The update was put on a new branch, which was set as the default branch. A sample usage file was added and the applicaiton of the encoding/vectors/matrix in Adverse Drug Event analytics was implemented in the `EBUtils.py`.
<p/>
  (a preliminary result of encoding drug-drug interaction data in ADE analytics) The Singular Value Decomposition on the matrix of drug-drug interaction Episode Encodings over 47k Adverse Events has revealed some potential *new* knowledge as shown in the following picture. The absolute y values represent the significances of each drug pair in terms of its correlation to the adverse event. (This study is an ongoing work and more details will be updated soon.)
<p>
  <img src="https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/imgs/drug_drug_ADE_filtered.png" width="400"/>
</p>

## Usage
The EBEncoding.py contains the encoding class and vector class definition. Two usage examples:
- the general usage example is available [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/ebencoding_example.py)
- the application of the encoding in Adverse Drug Event Analytics is [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/EBUtil.py)

## Analytics using the coding
- [Association Analasis of Adverse Drug Events and Polyphamacy](http://honghan.info/kcl/ade/) 

##Questions?
This is my ongoing work (2016) at Kings College London. Any questions please email: honghan.wu@kcl.ac.uk.

##citation
Honghan Wu, Zina Ibrahim, Ehtesham Iqbal and Richard Dobson. Predicting Adverse Events from Multiple and Dynamic Medication Episodes - a preliminary result in a large mental health registry. Accepted by IJCAI 2016 - Workshop on Knowledge Discovery in Healthcare Data.

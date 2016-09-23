# EBEncoding - efficient bitwise encoding for temporal (medical) data
Episode Bitwise Encoding is an encoding method designed for abstracting multiple medication episodes of a patient related to a certain event, e.g., an adverse drug event. This being said, such encoding is actually domain independent and can be applied to any temporal events. 

The motivation of such encoding is to make time series data easy to be consumed. One time series (e.g., a drug usage in past months) can be encoded as one numberic value. Multiple time series (e.g., multipharmacy) can be encoded as a vector. Therefore, after encoded, such data can be easily analysed (e.g., used in off-the-shelf machine learning algorithms). In our first use case, it is used for predicting adverse drug events for patients with mental health disorders.

## updates
- (23 September 2016) Define classess of EBEncoding and EBVector with opertators. The update was put on a new branch, which was set as the default branch. A sample usage file was added and the applicaiton of the encoding/vectors/matrix in Adverse Drug Event analytics was implemented in the `EBUtils.py`.
<p/>
  The Singular Value Decomposition on the matrix of drug-drug interaction Episode Encodings over 47k Adverse Events has revealed some potential *new* knowledge as shown in the following picture. (This study is an ongoing work and hopefully, more details will be published soon.)
<p>
  <img src="https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/imgs/drug_drug_ADE_filtered.png" width="400"/>
</p>

## Example: Medication Episode Encoding for an Adverse Drug Event
<p>
  <img src="https://github.com/Honghan/EBEncoding/blob/master/EBEncoding/imgs/fig2.png" width="468"/>
</p>
*Figure 1. The bitwise encoding of dynamic medication episodes for a given adverse event*

Figure 1 illustrates an example encoding scenario. The upper part shows the sample medication episodes of a patient that are related to a certain inspecting time spot (marked as AE date in the figure). The encoding is realised through the following steps.

1. From the the inspecting time spot, look back to a certain period of time, e.g., 20 days. In our experiments, we selected 30 days. 
2. Split the time period into intervals using a unit of time, e.g., a day or a week. Number each interval in an ascendent order (started from zero) starting from the inspecting time spot. For example, 4 intervals are identified and numbered in `Figure 1`.
3. Add the patient's medication episodes to the timeline. 
4. For each medication episode, allocate a sequence of bits aligned with the interval order we obtained in step 2. The interval numbered zero is aligned with the most significant bit in the sequence. For each interval, set the corresponding bit to `1` if the interval intersects with the episode, and to `0` otherwise. For example, Medication Episode 2 (M2) in `Figure 1` spans across interval number `1` and `2`. Its encoding is `0110` in binary code.
5. Repeat step 4 for all medication episodes. We will get a vector representing all the relevant medication episodes of the inspecting time spot.

The resulting bitwise encoding has the following features: 
- *Simple and Succinct:* Each medication episode is represented as a numeric value which can used as the feature value in a predictive model which can be consumed by most machine learning algorithms. 
- *Informative:* The encoded number conveys both the duration information of an episode (i.e. occurrences across multiple time intervals are recorded in their corresponding bits) and also the distances of each occurrence (i.e., the orders of bits in the number). For example, for duration, M2 crosses two intervals and its encoded number has two bits set as `1` accordingly; for distances, M1 and M3 are both present in only one interval. However, M3 is encoded as `8` because it is closer to the event, while M1 is represented as `1`.
- *Flexible* Different units of time can be used in step 2, enabling variable levels of granularity. For example, if the unit used is 4 times bigger in `Figure1`, all three medication episodes will be encoded as `1`. The same number of bits can cover medication periods that are four folds longer. The obvious loss of information however must be taken into account when choosing a time unit. 

## Usage
The EBEncoding.py contains the encoding class and vector class definition. Two usage examples:
- the general usage example is available [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/ebencoding_example.py)
- the application of the encoding in Adverse Drug Event Analytics is [here](https://github.com/Honghan/EBEncoding/blob/eb_algebra/EBEncoding/EBUtil.py)

##Questions?
This is my ongoing work (2016) at Kings College London. Any questions please email: honghan.wu@kcl.ac.uk.

##citation
Honghan Wu, Zina Ibrahim, Ehtesham Iqbal and Richard Dobson. Predicting Adverse Events from Multiple and Dynamic Medication Episodes - a preliminary result in a large mental health registry. Accepted by IJCAI 2016 - Workshop on Knowledge Discovery in Healthcare Data.

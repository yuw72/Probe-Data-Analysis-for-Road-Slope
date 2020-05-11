# Probe-Data-Analysis-for-Road-Slope

See Documentation: [Probe Analysis Report.pdf](https://github.com/whywww/Probe-Data-Analysis-for-Road-Slope/blob/master/Probe%20Analysis%20Report.pdf)

Requirements (known works on):
- python == 3.7
- pandas == 1.0.3
- numpy == 1.18.4
- tqdm == 4.46.0

Run:

`python3 code/Preprocess.py`

__In/Out:__ Probe Data CSV, Link Data CSV

__Description:__ Transition from latitude/longitude to Cartesian Coord.

`python3 code/Division.py`

__In:__ Preprocessed Link Data CSV

__Out:__ Grouped Link Data Json file

__Description:__ Divide Link Data into groups with special group ID.

`python3 Viterbi.py`

__In:__ Probe Data CSV, Link Data CSV, Grouped Link Data Json file

__Out:__ Routes dictionary Json file

__Description:__ Route of highest probability for each sampleID (probe car).

`python3 Slope_cal.py`

__In:__ Routes dictionary Json file

__Out:__ MSE, Result Slope CSV

__Description:__ Calculate Slopes of links and Compare with Ground Truth.

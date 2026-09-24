title: Tri-Band Feed Horn S11 Explorer
author: Jael Rojas

Dataset
S11.txt — simulated input reflection-coefficient response of the proposed tri-band circular feed horn antenna. The file contains two whitespace-separated numeric columns: frequency in Hz and 
𝑆11 in dB.

S11_sim_measure.txt — measured input reflection-coefficient response of the feed horn obtained during an anechoic-chamber measurement. The file contains two whitespace-separated numeric columns: frequency in Hz and 
𝑆 11 in dB.

The app converts frequency from Hz to GHz for readable plots and combines both responses for comparison.

Target operating bands
Band 1: 1.40–1.47 GHz
Band 2: 1.55–1.65 GHz
Band 3: 1.80–1.86 GHz

S11 criterion
The design requirement is:  S11 ≤−15 dB. More-negative 𝑆11 values indicate lower reflected power and better impedance matching between the feed horn and its input transmission line.

Run
Activate the course environment:

bash
conda activate dataviz
Move to the folder that contains the app and data files:

Start the Streamlit app:
bash
python -m streamlit run app_s11_compare.py

bash
python -m streamlit run test1.py

What the app does:
Loads simulated and anechoic-chamber-measured 𝑆11 data from text files.
Converts the frequency values from Hz to GHz.
Shows an optional preview of the combined dataset.
Compares simulation and measurement using interactive Altair line charts.
Displays the three intended operating bands: 1.40–1.47 GHz, 1.55–1.65 GHz, and 1.80–1.86 GHz.

Marks the return-loss requirement at 
𝑆11 = −15
S11 =−15 dB.

Uses shaded frequency regions, color, and line style to distinguish the intended subbands and response sources.
Provides hover tooltips for frequency, 
𝑆11, and response source.

Includes written encoding justifications based on perceptual accuracy, plus Gestalt and preattentive design principles.

Provides a numerical table with the minimum 
𝑆11 value and its frequency within each target band for both simulation and measurement.

Visualization question
How consistently do the simulated and anechoic-chamber measured 
𝑆11 responses satisfy the −15 dB criterion within the three intended operating subbands?

Encoding choices
Frequency: horizontal position in GHz.
S11: vertical position in dB.
Response source: color in the primary comparison chart and solid/dashed line style in the grayscale-friendly comparison chart.
Operating subbands: translucent colored background regions or labeled subband limits.
Performance threshold: dashed horizontal reference line at −15 dB.

Position on shared Cartesian scales provides an accurate visual comparison of frequency, 𝑆1 magnitude, resonance locations, and compliance with the requirement. Color and line style distinguish the nominal categories of simulation and measurement, while line style provides an alternative that remains interpretable in grayscale.
Files: app_s11_compare.py — Streamlit application for comparing simulated and measured
S11.txt — simulated feed horn 
𝑆11.txt data.


requirements.txt — Python package dependencies.

README.md — project overview and run instructions.

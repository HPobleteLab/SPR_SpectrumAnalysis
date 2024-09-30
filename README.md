
# SPR_SpectrumAnalysis

SPR_SpectrumAnalysis is an automated Python script that processes surface plasmon resonance (SPR) spectra. The script performs tasks such as:
- Baseline subtraction
- Intensity (I) calculation
- Full width at half maximum (FWHM)
- Wavelength (λ)
- Stability index

## PREREQUISITES:


- **Python Version:** 3.10.12
- **Required Libraries:** 
  - pandas: version 2.1.4 
  - numpy: version 1.26.2
  - matplotlib: version 3.8.2
  - openpyxl: version 3.1.4

You can install these libraries using the following command:
```bash
pip install pandas==2.1.4 numpy==1.26.2 matplotlib==3.8.2 openpyxl==3.1.4
```
## Installation:
1. Clone this repository:
```bash
git clone https://github.com/your-repo/SPR_SpectrumAnalysis.git
cd SPR_SpectrumAnalysis
pip install -r requirements.txt
```

## Running the script: 


### Preparation:
Prepare a folder containing all the pending files (in `.txt` or `.csv` format) that you want to process.

### Execution:
To run the script, open your terminal and navigate to the directory containing `processData.py` and the folder with your files. Use the following command:
```bash
python3 processData.py <nameFolder>
```
### Usage Example:
To analyze SPR spectra data from the folder `25-06-2024`, you would run:
```bash
python3 processData.py 25-06-2024
```

### Output:
For each analyzed file, the script will create a new folder with the name of the file and will store the corresponding outputs there. Ensure that the folder has the necessary write permissions.
```lua
output/
├── file1_output/
│   ├── OutScript.xlsx
│   ├── Score_OutScript.xlsx
│   ├── {A1...H12}.png # Plots
└── file2_output/
│   ├── OutScript.xlsx
│   ├── Score_OutScript.xlsx
│   ├── {A1...H12}.png # Plots
```

## CONTRIBUTORS:
- Francisca Salas Sepúlveda [CBSM, UTALCA] , Horacio Poblete [CBSM, UTALCA] , Sergio David Garcia Schejtman [BEaTS program, University of Ottawa Heart Institute], Juan David Figueroa Alegria [BEaTS program, University of Ottawa Heart Institute]


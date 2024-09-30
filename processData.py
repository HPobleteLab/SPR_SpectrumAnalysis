#Authors:  
# Francisca Salas Sepulveda < fsalas17 at alumnos.utalca > 
# Horacio Poblete < hopoblete at utalca  >
# Sergio David Garcia Schejtman
# Juan David Figueroa Alegrias 

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import os  
import sys

def backgroundSubstraction(file):
    print('Substracting background...')
    print('-------------------------------')
    #Get background value 

    dataFrame = pd.read_csv(file, sep="\t")

    if file.endswith('csv'):
        dataFrame = pd.read_csv(file, sep=",")

    #delete the last row if it is empty
    if dataFrame.iloc[-1].isnull().all():
        dataFrame = dataFrame.iloc[:-1]
    
    #Substract C1 value from the rest of the columns
    for column in list(dataFrame.columns)[2:]:
        dataFrame[column] = dataFrame[column] - dataFrame['C1'] 

            
    #change all data type to float
    dataFrame = dataFrame.astype(float)
    return dataFrame

def calculateData(fileName,All_data,column,dataFrame):
    print('Calculating and ploting Data...')
    #Model the line between the first and last point of the column
    if column == 'C1':
        return
    x = dataFrame['Wavelength']
    y = dataFrame[column]
    #plot the column
    
    plt.plot(np.array(x), np.array(y), label='Original Data')
    #plt.ylim(0, 1.0)
    first_point = [x.iloc[0],y.iloc[0]]
    last_point = [x.iloc[-1],y.iloc[-1]]
    #get the line between the first and last point
    slope = (last_point[1]-first_point[1])/(last_point[0]-first_point[0])
    intercept = first_point[1] - slope*first_point[0]
    #get the x values
    x_values = np.linspace(first_point[0],last_point[0],100)
    #get the y values
    y_values = slope*x_values + intercept
    #plot the line
    plt.plot(x_values,y_values, 'r--', label='First and Last Point Line')

    #calculate the distance between the line and the max value
    #get the max value of the column
    max_value = dataFrame[column].max()
    #get the wavelength of the max value
    max_wavelength = dataFrame['Wavelength'].loc[dataFrame[column] == max_value].values[0]
  
    #calculate the distance between the line and the max value (distance point to line)
    distance = np.abs(slope*max_wavelength - max_value + intercept)/np.sqrt(slope**2 + 1)
    #plot the distance as a line that conects the max value with the line
    plt.plot([max_wavelength,max_wavelength],[max_value,slope*max_wavelength + intercept], 'r--')

    #calculate the point in the middle of the distance
    x_middle = max_wavelength
    y_middle = max_value - distance/2

    plt.plot(x_middle,y_middle, 'bo', label='Middle distance point')

    # Calculate the max point
    max_point = [dataFrame['Wavelength'].iloc[y.idxmax()], y.max()]

    #Find the nearest points
    x_above = x[y >= y_middle]
    y_above = y[y >= y_middle]
    x_below = x[y < y_middle]
    y_below = y[y < y_middle]

    # Find the maximum/minimum point above and below
    x_above_min = x_above[y_above == y_above.min()].values[0]
    y_above_min = y_above.min()

    x_below_max = x_below[y_below == y_below.max()].values[0]
    y_below_max = y_below.max()

    # if the wavelength of below max is less than the wavelength of x middle keep searching or
    # if the wavelength of above min is greater than the wavelength of x middle keep searching and 
    # x below max > x above min
    while (not y_below.empty and x_below_max < x_middle) or (not y_above.empty and x_above_min > x_middle):
        # if the wavelength of below max is less than the wavelength of x middle keep searching
        if not y_below.empty and x_below_max < x_middle:
            # get the next value of x below
            x_below = x_below[x_below != x_below_max]
            y_below = y_below[y_below != y_below_max]
            if not y_below.empty:
                x_below_max_index = y_below.idxmax()
                x_below_max = x[x_below_max_index]
                y_below_max = y_below.max()

        # if the wavelength of above min is greater than the wavelength of x middle keep searching
        if not y_above.empty and x_above_min > x_middle:
            # get the next value of x above
            x_above = x_above[x_above != x_above_min]
            y_above = y_above[y_above != y_above_min]
            if not y_above.empty:
                x_above_min_index = y_above.idxmin()
                x_above_min = x[x_above_min_index]
                y_above_min = y_above.min()
            
    # Calculate distance between poits
    width_at_half = abs(x_above_min - x_below_max)

    max_LPSR = max_wavelength
    extinction = distance

    #PLOT THE DATA
    plt.ylabel('Intensity')
    plt.xlabel('Wavelength [nm]')
    plt.title(column)
    plt.legend(loc='lower left')
    plt.grid(False)
    plt.savefig(fileName[0:-4]+'/'+column+'.png')
    plt.clf()
        
    data = [column, width_at_half, max_LPSR, extinction]
    All_data.append(data)

def createDataframe(fileName):
    print('Creating DataFrame with Width - Max SPR - Intensity values...')
    print('-------------------------------')

    data = backgroundSubstraction(fileName)
    All_data = []
    for column in list(data.columns)[1:]:
        #if cell is empty then skip
        if data[column].isnull().all():
            continue
        else:
            calculateData(fileName, All_data,column,data)
        
    columns = ["Sample Name", "FWHM", "Max SPR","Intensity"]

    #select the first element of every element in All_letters
    sample_Name = [list(x)[0] for x in All_data]
    width = [list(x)[1] for x in All_data]
    max_LSPR = [list(x)[2] for x in All_data]
    Extinction = [list(x)[3] for x in All_data]


    columns = ['Sample Name', 'FWHM', 'Max SPR', 'Intensity']
    data = {
        'Sample Name': sample_Name,
        'FWHM': width,
        'Max SPR': max_LSPR,
        'Intensity': Extinction
    }

    df = pd.DataFrame(data, columns=columns)
    
    #Save dataframe as excel file
    df.to_excel(fileName[0:-4]+'/OutScript.xlsx', header=True, engine='openpyxl', index=False)
    df = df.T
    return df

def calculateDelta(fileName,dataFrame):
    print('-------------------------------')
    print('Calculating Delta Values...')
    print('-------------------------------')

    deltaData = pd.DataFrame(index=['Delta Width (-) NaCl', 'Delta Width (+) NaCl', 'Delta LSPR (-) NaCl', 'Delta LSPR (+) NaCl', 'Relative Intensity (-) NaCl', 'Relative Intensity (+) NaCl'])
   
    
    #calculate the width for the samples without NaCl
    #get A1 value: AuNPs 
    A1_AuNPs_Width = dataFrame.loc['Width'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0]
    A1_AuNPs_Intensity = dataFrame.loc['Max LSPR'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0]

    for sampleName in dataFrame.loc['Sample Name'].values:
        #if sampleName[1:] not equals '1' then it is a sample with NaCl
        if '1' not in sampleName or (sampleName.endswith('10') or sampleName.endswith('11') or sampleName.endswith('12')):
            if '2' not in sampleName or (sampleName.endswith('12')):
            
                #subtract the B1 value from the sample value
                deltaWidth_without_NaCl = abs(dataFrame.loc['Width'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] - A1_AuNPs_Width)
                deltaWidth_with_NaCl = abs(dataFrame.loc['Width'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] - deltaWidth_without_NaCl)

                deltaLSPR_without_NaCl = abs(dataFrame.loc['Max LSPR'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] - A1_AuNPs_Intensity)
                deltaLSPR_with_NaCl = abs(dataFrame.loc['Max LSPR'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] - deltaLSPR_without_NaCl)
                
                #PEP+NP: without NaCl
                if sampleName[0] == 'A' or sampleName[0] == 'B' or sampleName[0] == 'C' or sampleName[0] == 'D' and (int(sampleName[1:]) in range(3,13)):
                    #If extincion is 0 then the relative intensity is infinity
                    if dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] == 0:
                        relative_Intensity_without_NaCl = np.inf
                    else:
                        relative_Intensity_without_NaCl = (dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0]/dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0])          
                    
                    #get ASCII value of the first character in sampleName and add 1 to it and then convert it back to a string
                    referenceName = chr(ord(sampleName[0]) + 4) + sampleName[1]
                    
                    deltaLSPR_with_NaCl = '--'
                    deltaWidth_with_NaCl = '--'
                    relative_Intensity_with_NaCl = '--'
                
                #PEP+NP+NaCl 100mM : with NaCl
                elif sampleName[0] == 'E' or sampleName[0] == 'F' or sampleName[0] == 'G' or sampleName[0] == 'H' and (int(sampleName[1:]) in range(3,13)):
                    #el delta width (+) NaCl correspondiente a B3 deberia ser solamente B3-A3.
                    if '1' not in sampleName or (sampleName.endswith('10') or sampleName.endswith('11') or sampleName.endswith('12')):
                        if '2' not in sampleName or (sampleName.endswith('12')):
                            referenceName = chr(ord(sampleName[0]) - 4) + sampleName[1:]
                            referenceName = chr(ord(sampleName[0]) - 4) + sampleName[1:]
                    else:
                        referenceName = chr(ord(sampleName[0]) - 4) + sampleName[1]
                    
                    deltaWidth_without_NaCl = abs(dataFrame.loc['Width'].loc[dataFrame.loc['Sample Name'] == referenceName].values[0])
                    deltaWidth_with_NaCl = abs(dataFrame.loc['Width'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] - deltaWidth_without_NaCl)

                    deltaLSPR_without_NaCl = abs(dataFrame.loc['Max LSPR'].loc[dataFrame.loc['Sample Name'] == referenceName].values[0])
                    deltaLSPR_with_NaCl = abs(dataFrame.loc['Max LSPR'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] - deltaLSPR_without_NaCl)
                    
                    if dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == referenceName].values[0] == 0:
                        relative_Intensity_without_NaCl = np.inf
                    else:
                        relative_Intensity_without_NaCl = (dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == referenceName].values[0]/dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0])  
                          
                    relative_Intensity_with_NaCl = (dataFrame.loc['Extinction'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0]/relative_Intensity_without_NaCl)

                    deltaWidth_without_NaCl = '--'
                    deltaLSPR_without_NaCl = '--'
                    relative_Intensity_without_NaCl='--'


                data = [deltaWidth_without_NaCl, deltaWidth_with_NaCl, deltaLSPR_without_NaCl, deltaLSPR_with_NaCl, relative_Intensity_without_NaCl, relative_Intensity_with_NaCl]
                deltaData[sampleName] = data
        else:
            pass
           
    to_excel_data = deltaData.T
    to_excel_data.to_excel(fileName[0:-4]+'/'+ 'Delta_OutScript.xlsx', engine='openpyxl')
    return deltaData

def newScore(fileName, dataFrame):

    deltaData = pd.DataFrame(index=['Relative FWHM (-) NaCl', 'Relative FWHM (+) NaCl', 'Relative SPR (-) NaCl', 'Relative SPR (+) NaCl', 'Relative Intensity (-) NaCl', 'Relative Intensity (+) NaCl'])
    
    #calculate the width for the samples without NaCl
    #get A1 value: AuNPs
    A1_AuNPs_Width_FWHM_0 = dataFrame.loc['FWHM'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0]
    A1_AuNPs_Intensity_0 = dataFrame.loc['Intensity'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0]
    A1_AuNPs_LSPR_0 = dataFrame.loc['Max SPR'].loc[dataFrame.loc['Sample Name'] == 'A1'].values[0]

    for sampleName in dataFrame.loc['Sample Name'].values:
        #if sampleName[1:] not equals '1' then it is a sample with NaCl
        if '1' not in sampleName or (sampleName.endswith('10') or sampleName.endswith('11') or sampleName.endswith('12')):
            if '2' not in sampleName or (sampleName.endswith('12')):
                #PEP+NP: without NaCl
                if sampleName[0] == 'A' or sampleName[0] == 'B' or sampleName[0] == 'C' or sampleName[0] == 'D' and (int(sampleName[1:]) in range(3,13)):

                    if dataFrame.loc['Intensity'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] == 0:
                        relative_Intensity_without_NaCl = np.inf
                    else:
                        relative_Intensity_without_NaCl = (dataFrame.loc['Intensity'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0]/A1_AuNPs_Intensity_0)       

                    relative_Width_without_NaCl = (A1_AuNPs_Width_FWHM_0/dataFrame.loc['FWHM'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0])
                    relative_LSPR_without_NaCl = (A1_AuNPs_LSPR_0/dataFrame.loc['Max SPR'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0])
                    #get ASCII value of the first character in sampleName and add 1 to it and then convert it back to a string
                    referenceName = chr(ord(sampleName[0]) + 4) + sampleName[1]
                    
                    relative_LSPR_with_NaCl = '--'
                    relative_Width_with_NaCl = '--'
                    relative_Intensity_with_NaCl = '--'
                
                #PEP+NP+NaCl 100mM : with NaCl
                elif (sampleName[0] == 'E' or sampleName[0] == 'F' or sampleName[0] == 'G' or sampleName[0] == 'H') and (int(sampleName[1:]) in range(3,13)):
                    if '1' not in sampleName or (sampleName.endswith('10') or sampleName.endswith('11') or sampleName.endswith('12')):
                            referenceName = chr(ord(sampleName[0]) - 4) + sampleName[1:]
                    else:
                        referenceName = chr(ord(sampleName[0]) - 4) + sampleName[1]

                   
                    if dataFrame.loc['Intensity'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0] == 0:
                        relative_Intensity_with_NaCl = np.inf
                    else:    
                        relative_Intensity_with_NaCl = (dataFrame.loc['Intensity'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0]/A1_AuNPs_Intensity_0)

                    #relative_Width_without_NaCl = (dataFrame.loc['Width'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0]/A1_AuNPs_Width_FWHM_i)
                    relative_Width_with_NaCl = (A1_AuNPs_Width_FWHM_0/dataFrame.loc['FWHM'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0])
                    
                    #relative_LSPR_without_NaCl = (dataFrame.loc['Max LSPR'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0]/A1_AuNPs_LSPR_i)
                    relative_LSPR_with_NaCl = (A1_AuNPs_LSPR_0/dataFrame.loc['Max SPR'].loc[dataFrame.loc['Sample Name'] == sampleName].values[0])

                    relative_Width_without_NaCl = '--'
                    relative_LSPR_without_NaCl = '--'
                    relative_Intensity_without_NaCl='--'


                data = [relative_Width_without_NaCl, relative_Width_with_NaCl, relative_LSPR_without_NaCl, relative_LSPR_with_NaCl, relative_Intensity_without_NaCl, relative_Intensity_with_NaCl]
                deltaData[sampleName] = data
        
    #Translocate the data to an excel file
    deltaData = deltaData.T

    #New column named Spectroscopical Changes with the sum of the relative values; ignore values when they are '--'
    deltaData['SC'] = deltaData.apply(lambda x: x[x != '--'].sum(), axis=1)
    deltaData.to_excel(fileName[0:-4]+'/'+ 'SC_OutScript.xlsx', engine='openpyxl')
    
    return deltaData

def main():
    directory = sys.argv[1]
    files = os.listdir(directory)
    fileNames = []

    for file in files:
        #skip the script file
        if file.endswith('.csv') or file.endswith('.txt'):
            tempName = directory + '/' + file
            fileNames.append(tempName)

    for fileName in fileNames:
        print('-------------------------------')

        if not os.path.exists(fileName[0:-4]):
            os.makedirs(fileName[0:-4])

        data=(createDataframe(fileName))
        newScore(fileName, data)    
        print('File analysis is complete: ' + fileName)
        print('-------------------------------')

main()

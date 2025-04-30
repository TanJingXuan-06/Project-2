# import 
import serial
from serial.tools import list_ports
import time 
import matplotlib.pyplot as plt
import csv 
import numpy as np 
from scipy import integrate

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# SAMPLES PARAMETERS
NOISE_LEVEL = 0        # to define the noise level 
TIME = 4               # time to gather 1 data 
SAMPLE_RATE = 5062

# FREQUENCY THRESHOLD
FREQ_THRESHOLD = 90 
WAVELENGTH_THRESHOLD = 3500 

# ERASER PARAMETERS  
ERASER_H30L10 = 1800 
ERASER_H10L30 = 550 

# COIN PARAMETERS 
# HEIGHT LENGTH 
COIN_HEIGHT_30 = 2400

# the target string to determine if STM 32 is connected 
STM32Name = "STMicroelectronics STLink Virtual COM Port"


def check_STM32_connectivity():
    """ 
    Attempts to find and connect to the STM32.
    
    Returns: 
        ListPortInfo: The STM32 port. 
        int: -1 if a port isn't found.
    """ 
    # get the list of ports
    listOfPorts = list_ports.comports()
    # loop through all the items in the list 
    for indexList in range (len(listOfPorts)) : 
        port = listOfPorts[indexList]   
        # convert the portName to string to use find()
        portNameStr = str(port)
        # find the index of the STM32 
        # if not found will return -1 
        if portNameStr.find(STM32Name) != -1 : 
            stm32_port = port
            return stm32_port 
            
        
    return -1 

def gather_data() : 
    # input : input from user to get data 
    # output : start stm 
    """ 
    Records and prints voltage reading from the sensor
    Gets 20 raw voltage data from the sensor including the mean of these 20 datas. 

    Returns: 
        Mean data received : if STM32 board is found.
        None: if STM32 board isn't found.
    """ 
    stm32_port = check_STM32_connectivity()
    data_list = []
    print(" ------------------------------------ GATHER DATA ------------------------------------")
    
    if stm32_port == -1 :
        print("STM32 board not found. Please ensure it is connected.")
        return 
    
    try : 
        ser = serial.Serial(port =stm32_port.name, baudrate=230400 , timeout=1)    
        ser.write(b"RUN")       #"Send RUN to STM32"
        print("Writing to STM.....")
        time.sleep(0.5)
        
        # calculate time 
        start_time = time.time() 
        end_time = time.time()
        time_diff = end_time - start_time

        # take data according to a time frame we set 
        while time_diff <= TIME : 
            
            data_received = ser.readline().decode("utf-8").strip()          
            # if STM sent any data 
            if data_received : 
                # if the data is Mean Value 
                if "= " in data_received:
                    print(data_received)
                    data = int(data_received.split('=')[1].strip())
                    data_list.append(data)
                    
            end_time = time.time()
            time_diff = end_time - start_time
            
        SAMPLE_RATE = len(data_list)
        return data_list
                 
    except (KeyboardInterrupt, serial.SerialException) as e:
        print("Error") 
        
    ser.write(b"STP")       #"Send RUN to STM32"
       
def filter_data(adc_values) : 
    
    ret = [] 
    
    for i in adc_values : 
        if i < NOISE_LEVEL : 
            ret.append(0)
            
        else : 
            ret.append(i)
            
    return ret 
            
def get_freq(adc_values) :
              
    data_count = 0
    last_idx = 0 
    peak = None 
    freq_list = []
    zero = 0 
    
    for idx in range (len(adc_values)-1) : 
        
        # if this is true 
        # means this is a peak 
        if idx > 0 : 
            if (adc_values[idx] > adc_values[idx+1]) and (adc_values[idx] > adc_values[idx-1]) : 
                
                # if data_count is 0 means this is the first peak 
                if peak == None and zero == 0 : 
                    last_idx = idx
                    peak = adc_values[idx]
                    data_count = 0 
  
                
                elif zero == 0 : 
                    # peak = None 
                    data_count = idx - last_idx
                    last_idx = idx 
                    peak = adc_values[idx]
                    period = (TIME/SAMPLE_RATE) * data_count
                    freq = 1/period
                    freq_list.append(freq)
                    data_count = 0 
                    
                zero = adc_values[idx]
                    
            if adc_values[idx] == 0 : 
                zero = 0 
        
                
    if len(freq_list) == 0 :
        return None    
    
    return round(sum(freq_list)/len(freq_list),2)

def get_avgamp(list) :
    # input  : a list of raw data from stm  
    # output : average of all spikes after NOISE_LEVEL

    total = 0
    count = 0
    
    for i in list:
        if (i > NOISE_LEVEL):
            total += i
            count += 1

    if count == 0 : 
        return 0 
    
    return total/count

def highest_amp(adc_values):
    
    return max(adc_values)
  
def prediction(wavelength,freq,amp,numOfPeaks,area,nonZero,model_c10, model_c30, model_e): 
    
    arr = np.array([wavelength, freq,amp,numOfPeaks,area,nonZero]).reshape(1,-1)
        
    if wavelength < WAVELENGTH_THRESHOLD : 

        if amp > ERASER_H30L10 : 
            print(f"AMP = {amp}")
            print("ERASER, 10CM, 30CM")
            
        elif amp < ERASER_H10L30 : 
            print(f"AMP = {amp}")
            print("ERASER, 30CM, 10CM") 
        
        # prediction model        
        else : 
            print(f"AMP = {amp}")
            pred = model_e.predict(arr)
            if pred == 1 :
                print("ERASER, 30CM, 30CM")

            else : 
                print("ERASER, 10CM, 10CM")
                     
    # if coin 
    else : 
        
        if amp > COIN_HEIGHT_30 : 
            pred = model_c30.predict(arr)
            print(f"AMP = {amp}")
            if pred == 1 : 
                print("COIN, 30CM , 30CM")

            else : 
                print("COIN, 10CM , 30CM")
                       
        else : 
            print(f"AMP = {amp}")
            pred = model_c10.predict(arr)            
            if pred == 1 : 
                print("COIN, 30CM, 10CM ")

            else : 
                print("COIN, 10CM, 10CM ")
               
def numOfPeaks(adc_values) :
    non_zero_list = [x for x in adc_values if x != 0]
    
    return len(non_zero_list)
                  
def areaUnderGraph(adc_values): 
    x = np.arange(0,len(adc_values),1)
    
    return integrate.simpson(adc_values,x)
     
def nonZeroData(adc_values) : 
    
    return np.count_nonzero(adc_values)     

def p2p(adc_values) :

    peakOld = 0 
    peakList = np.zeros(len(adc_values)) 
    counter = 0 
    peak_idx = 0 
    adc_copy = adc_values.copy()    
    
    
    for idx in range(1, len(adc_copy) - 1):
        
        # If less than 500 we ignore 
        if adc_copy[idx] <= 400:
            counter += 1
            adc_copy[idx] = 0 
        else:
            counter = 0

        # Peak detection
        if adc_copy[idx] > adc_copy[idx - 1] and adc_copy[idx] > adc_copy[idx + 1]:
            
            # if current peak more than last peak than update the peak 
            if adc_copy[idx] > peakOld:
                peakOld = adc_copy[idx]
                peak_idx = idx

        # If continuously 100 datas below 500 
        if counter >= 100:
            
            # if peak old not 0, set the peak old to the index it is suppose to be
            if peakOld > 0:
                peakList[peak_idx] = peakOld
            peakOld = 0
            counter = 0

    # Handle last wave
    if peakOld > 0:
        peakList[peak_idx] = peakOld         
                 
    return peakList

def filterPK(adc_values) : 
    
    nonzero_values = [value for value in adc_values if value != 0]
    nonzero_indices = [idx for idx, value in enumerate(adc_values) if value != 0]  
    
    return nonzero_indices, nonzero_values

def visualize_data(list) : 
    # input : a list of raw data from stm  
    # output : plot the graph to visualize the input
    x = []
    
    for i in range(0, len(list)):
        x.append(i)
    
    plt.plot(x, list)
    plt.scatter(x,list,color = 'red')
    plt.xlabel("Detection")
    plt.ylabel("Raw ADC Values")
    plt.savefig(f"Project 2/plots/DATA.png")
    plt.grid()
    plt.ylim(-100,4100) 

def model() : 
    data = pd.read_csv('./Project 2/data_set.csv', header=None)
    data = data.to_numpy()

    # Splitting Dataset by Item Dropped and Height
    c10 = data[0:65, :]
    c30 = data[65:140, :]
    e = data[140:200, :]
    ########## Coin at Height 10cm ##########
    c10_x = c10[:, 0:6]
    c10_y = c10[:, -1]
    model_c10 = LogisticRegression(max_iter=1000)
    model_c10.fit(c10_x, c10_y)
    ########## Coin at Height 30cm ##########
    c30_x = c30[:, 0:6]
    c30_y = c30[:, -1]
    model_c30 = LogisticRegression(max_iter=1000)
    model_c30.fit(c30_x, c30_y)
    ########## Eraser ##########
    e_x = e[:, 0:6]
    e_y = e[:, -1]
    model_e = LogisticRegression(max_iter=1000)
    model_e.fit(e_x, e_y)
    
    return model_c10, model_c30, model_e

def wave_length(adc_values) : 
    
    start = 0 
    end = 0 
    
    for i in range(0,len(adc_values)) : 
        if adc_values[i] != 0 : 
            start = i  
            break 
    
    for j in range(len(adc_values)-1,0,-1) :
        if adc_values[j] != 0 : 
            end = j 
            break 

    
    return (end-start)   

def main(): 
    print("START MENU")
    model_c10, model_c30, model_e = model()
    
    while True : 
        user = input("Y/N ?")
        
        if user == 'y' or user == 'Y' :
            
            mode = input("1: Data Collection\n2: Prediction\n3: Eraser Detection Mode ")
            
            if mode == "1" : 
            
                tag = input("Tag Name")
                time.sleep(0.5)
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(1, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                      
                data = gather_data()
                ori_data = data 
                SAMPLE_RATE = len(data)
                data = filter_data(data)
                freq = get_freq(data)
                max_amp = highest_amp(data)                
                area  = areaUnderGraph(data)
                nonZero = nonZeroData(data)
                
                length_wave = wave_length(ori_data)
                print(f"The length of wave is: {length_wave}")
               
                plt.subplot(2,1,1)
                visualize_data(data)
                plt.subplot(2,1,2)
                visualize_data(pk)
                plt.show()
                               
                
                with open("Project 2/data_set.csv", 'a', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow([length_wave,freq,max_amp,peaks,area,nonZero,tag])
                
            elif mode == '2' : 
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(1, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                
                
                data = gather_data()
                ori_data = data 
                data = filter_data(data)
                freq = get_freq(data)
                max_amp = highest_amp(data)
                
                area  = areaUnderGraph(data)
                nonZero = nonZeroData(data)
                
                # PEAKS 
                pk = p2p(data)
                __ , pk_y = filterPK(pk)
                
                peaks = numOfPeaks(pk_y)
                length_wave = wave_length(ori_data)
                prediction(length_wave,freq,max_amp,peaks,area,nonZero,model_c10, model_c30, model_e)
                
            
            elif mode == '3' :
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(1, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                    
                data = gather_data()
                
                max_amp = highest_amp(data)
                print(f"The highest peak is: {max_amp}")
                
                if max_amp != 0 : 
                    print("Eraser Detected")
                    
                visualize_data(data)
                plt.show()
                
                
                     
        elif user == 'n' or user == 'N' :
            break 
    else : 
        return None 
        
if __name__ == "__main__":
    main()
    

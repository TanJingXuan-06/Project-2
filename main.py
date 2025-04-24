# import 
import serial
from serial.tools import list_ports
import time 
import matplotlib.pyplot as plt
import csv 
import numpy as np 

# SAMPLES PARAMETERS
NOISE_LEVEL = 10        # to define the noise level 
TIME = 10               # time to gather 1 data 
SAMPLE_RATE = 584
SAMPLING_RATE = SAMPLE_RATE/TIME  # Number of samples / Time Period 

# FREQUENCY THRESHOLD
FREQ_THRESHOLD = 100 

# ERASER PARAMETERS  
# HEIGHT LENGTH   
ERASER_H_L_PARAM_30_10 = 1 
ERASER_H_L_PARAM_30_30 = 1 
ERASER_H_L_PARAM_10_10 = 1 
ERASER_H_L_PARAM_10_30 = 1 

# COIN PARAMETERS 
# HEIGHT LENGTH 
COIN_H_L_PARAM_30_10 = 1 
COIN_H_L_PARAM_30_30 = 1 
COIN_H_L_PARAM_10_10 = 1 
COIN_H_L_PARAM_10_30 = 1 


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
        ser = serial.Serial(port =stm32_port.name, baudrate=115200 , timeout=1)    
        # print(f"Stm32 Connected to {stm32_port}") 
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
                if "ADC Value = " in data_received:
                    print(data_received)
                    # print("DATA RECEIVED")
                    data = int(data_received.split('=')[1].strip())
                    data_list.append(data)
                    
            end_time = time.time()
            time_diff = end_time - start_time
        return data_list
                 
    except (KeyboardInterrupt, serial.SerialException) as e:
        print("Error") 
        
    ser.write(b"STP")       #"Send RUN to STM32"
             

def get_freq(adc_values) :
    valid_list = []
    noise_region = 0 
    
    # adc_values = [120, 150, 90, 85, 200, 180, 50, 95, 250, 80, 30, 40]
    # If NOISE_LEVEL = 100:
    # 120, 150, 200, 180, 250 would be added to valid_list.
    # After encountering 50, 95, the noise_region would increase.
    # If the noise_region exceeds 4, the loop would break, ignoring the remaining values (80, 30, 40).
    
    for idx in range (0,len(adc_values)) :     
        if adc_values[idx] > NOISE_LEVEL and noise_region <= 4: 
            valid_list.append(adc_values[idx])
            noise_region = 0 
            
        elif noise_region > 4 : 
            break 
        
        else : 
            noise_region += 1 
            
    data_count = 0
    peak = None 
    freq_list = []
    for idx in range (len(valid_list)-1) : 
        
        # if this is true 
        # means this is a peak 
        if idx > 0 : 
            if (valid_list[idx] > valid_list[idx+1]) and (valid_list[idx] > valid_list[idx-1]) : 
                
                # if data_count is 0 means this is the first peak 
                if peak == None : 
                    peak = valid_list[idx]
                    data_count = 0 
                    pass
                
                else : 
                    peak = None 
                    period = (TIME/SAMPLE_RATE) * data_count
                    freq = 1/period
                    freq_list.append(freq)
                    data_count = 0 
            
            # if not yet reach peak 
            else :         
                data_count += 1 
            
    return round(max(freq_list),2)

def get_avgamp(list) :
    # input  : a list of raw data from stm  
    # output : average of all spikes after NOISE_LEVEL
    
    # anything you find relavant to our project 
    # only take highest amplitude ?
    # take multiple highest ampltiude if there's different spikes ? 
    total = 0
    count = 0
    
    for i in list:
        if (i > NOISE_LEVEL):
            total += i
            count += 1

    return total/count

def highest_amp(adc_values, NOISE_LEVEL):
    # Input : list of raw data, NOISE_LEVEL for noise
    # output :  the highest amplitude from the list
    spike_segments = []
    max_spikes = []

    i = 0
    while i < len(adc_values):
    # Wait for a value BELOW NOISE_LEVEL
        if adc_values[i] < NOISE_LEVEL:
            # Look ahead for rising edge
            j = i + 1
            while j < len(adc_values) and adc_values[j] < NOISE_LEVEL:
                j += 1

            # Found start of a spike
            start = j

            # Move forward until signal drops back below NOISE_LEVEL
            while j < len(adc_values) and adc_values[j] >= NOISE_LEVEL:
                j += 1

            end = j

            if end > start:
                spike = adc_values[start:end]
                spike_segments.append(spike)
                max_spikes.append(np.max(spike))

            i = j  # skip to next search
        else:
            i += 1
    
    for idx, spike in enumerate(spike_segments):
        print(f"Spike {idx+1}: values = {spike}, max = {max_spikes[idx]}")
    
    return max(max_spikes)


def visualize_data(list) : 
    # input : a list of raw data from stm  
    # output : plot the graph to visualize the input
    x = []
    
    for i in range(0, len(list)):
        x.append(i)
    
    plt.plot(x, list)
    plt.xlabel("Detection")
    plt.ylabel("Raw ADC Values")
    
    plt.show()
    # plot the raw data 
    
def predict(freq, avg_amp):
    
    # if eraser  
    if freq < FREQ_THRESHOLD : 
        
        if avg_amp < ERASER_H_L_PARAM_10_30 : 
            print("ERASER: HEIGHT = 10 CM, LENGTH = 30 CM")
            
        elif avg_amp > ERASER_H_L_PARAM_10_30 and avg_amp < ERASER_H_L_PARAM_30_30: 
            print("ERASER: HEIGHT = 30 CM, LENGTH = 30 CM")
            
        elif avg_amp > ERASER_H_L_PARAM_30_30 and avg_amp < ERASER_H_L_PARAM_10_10: 
            print("ERASER: HEIGHT = 10 CM, LENGTH = 10 CM")
            
        elif avg_amp > ERASER_H_L_PARAM_10_10 and avg_amp < ERASER_H_L_PARAM_30_10: 
            print("ERASER: HEIGHT = 30 CM, LENGTH = 10 CM")
        
    # if coin 
    else : 
        
        if avg_amp < COIN_H_L_PARAM_10_30 : 
            print("COIN: HEIGHT = 10 CM, LENGTH = 30 CM")
            
        elif avg_amp > COIN_H_L_PARAM_10_30 and avg_amp < COIN_H_L_PARAM_30_30: 
            print("COIN: HEIGHT = 30 CM, LENGTH = 30 CM")
            
        elif avg_amp > COIN_H_L_PARAM_30_30 and avg_amp < COIN_H_L_PARAM_10_10: 
            print("COIN: HEIGHT = 10 CM, LENGTH = 10 CM")
            
        elif avg_amp > COIN_H_L_PARAM_10_10 and avg_amp < COIN_H_L_PARAM_30_10: 
            print("COIN: HEIGHT = 30 CM, LENGTH = 10 CM")
                 
def main(): 
    print("START MENU")
    
    while True : 
        user = input("Continue Y/N? ")
        
        if user == 'y' or user == 'Y' :
            
            mode = input("1: Data Collection\n2: Prediction ")
            
            if mode == "1" : 
            
                typeOfMaterial = input("Coin, Eraser, Others.")
                height = input("10, 30, other")
                height = height + ' cm'
                length = input("10, 30, other")
                length = length + ' cm'    
                
                time.sleep(0.5)
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(3, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                      
                data = gather_data()
                
                visualize_data(data)
                
                freq = get_freq(data)
                avg_amp = get_avgamp(data)
                max_amp = highest_amp(data)
                
                with open("Project 2/vibration.csv", 'a', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow([typeOfMaterial,height,length,data,freq,avg_amp,max_amp])
                
            elif mode == '2' : 
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(3, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                    
                data = gather_data()
                freq = get_freq(data)
                avg_amp = get_avgamp(data)
                max_amp = highest_amp(data)
                
                
                
        elif user == 'n' or user == 'N' :
            break 
    else : 
        return None 
        
        
if __name__ == "__main__":
    main()
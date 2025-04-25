# import 
import serial
from serial.tools import list_ports
import time 
import matplotlib.pyplot as plt
import csv 
import numpy as np 

# SAMPLES PARAMETERS
NOISE_LEVEL = 25        # to define the noise level 
TIME = 3               # time to gather 1 data 
SAMPLE_RATE = 5062
SAMPLING_RATE = SAMPLE_RATE/TIME  # Number of samples / Time Period 

# FREQUENCY THRESHOLD
FREQ_THRESHOLD = 150 

# ERASER PARAMETERS  
# HEIGHT LENGTH   
ERASER_H_L_PARAM_30_10 = 1 
ERASER_H_L_PARAM_30_30 = 1 
ERASER_H_L_PARAM_10_10 = 1 
ERASER_H_L_PARAM_10_30 = 1 

# COIN PARAMETERS 
# HEIGHT LENGTH 
COIN_H_L_PARAM_10_30 = 114
COIN_H_L_PARAM_30_30 = 127
COIN_H_L_PARAM_10_10 = 140
COIN_H_L_PARAM_30_10 = 160


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
                if "= " in data_received:
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
       
def filter_data(adc_values) : 
    
    ret = [] 
    
    for i in adc_values : 
        if i < NOISE_LEVEL : 
            ret.append(0)
            
        else : 
            ret.append(i)
            
    return ret 
            
              

def get_freq(adc_values) :
   
    # adc_values = [120, 150, 90, 85, 200, 180, 50, 95, 250, 80, 30, 40]
    # If NOISE_LEVEL = 100:
    # 120, 150, 200, 180, 250 would be added to valid_list.
    # After encountering 50, 95, the noise_region would increase.
    # If the noise_region exceeds 4, the loop would break, ignoring the remaining values (80, 30, 40).
    
    # for idx in range (0,len(adc_values)) :     
    #     if adc_values[idx] > NOISE_LEVEL and noise_region <= 4: 
    #         valid_list.append(adc_values[idx])
    #         noise_region = 0 
            
    #     elif noise_region > 4 : 
    #         break 
        
    #     else : 
    #         noise_region += 1 
            
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
                    
                    # print(idx)        
                    # print(f"THIS IS THE First PEAK AT {adc_values[idx]}")    
                
                elif zero == 0 : 
                    # peak = None 
                    data_count = idx - last_idx
                    last_idx = idx 
                    peak = adc_values[idx]
                    period = (TIME/SAMPLE_RATE) * data_count
                    freq = 1/period
                    # print(idx)        
                    # print(f"THIS IS THE PEAK AT {adc_values[idx]}")   
                    # print(f"Freq: {freq}") 
                    freq_list.append(freq)
                    data_count = 0 
                    
                zero = adc_values[idx]
                    
            if adc_values[idx] == 0 : 
                zero = 0 
        
                
    if len(freq_list) == 0 :
        return None    
    
    # print(f"Len {freq_list}")
    # print(freq_list)
    return round(sum(freq_list)/len(freq_list),2)

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

    if count == 0 : 
        return 0 
    
    return total/count

def highest_amp(adc_values):
    
    return max(adc_values)


def visualize_data(list,material,height,length) : 
    # input : a list of raw data from stm  
    # output : plot the graph to visualize the input
    x = []
    
    for i in range(0, len(list)):
        x.append(i)
    
    plt.plot(x, list)
    plt.scatter(x,list,color = 'red')
    plt.xlabel("Detection")
    plt.ylabel("Raw ADC Values")
    plt.title(f"{material},{height} ,{length} ")
    plt.savefig(f"Project 2/plots/{material},{height},{length}.png")
    plt.show()
    # plot the raw data 
    
def predict(freq, avg_amp,amp):
    
    # if eraser  
    if freq < FREQ_THRESHOLD : 
        
        print("Eraser")
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
        print("Coin")

        # Safeguard: High amplitude around 4000 is very likely LENGTH = 10
        if amp >= 3950:
            if avg_amp > 145:
                print("COIN: HEIGHT = 10 CM, LENGTH = 10 CM")
            else:
                print("COIN: HEIGHT = 30 CM, LENGTH = 10 CM")

        # Lower amplitudes (under 3100) more likely LENGTH = 30
        else:
            if avg_amp < COIN_H_L_PARAM_10_30:
                print("COIN: HEIGHT = 10 CM, LENGTH = 30 CM")
                
            elif avg_amp >= COIN_H_L_PARAM_10_30 and avg_amp < COIN_H_L_PARAM_30_30:
                print("COIN: HEIGHT = 30 CM, LENGTH = 30 CM")
                
            elif avg_amp >= COIN_H_L_PARAM_30_30 and avg_amp < COIN_H_L_PARAM_10_10:
                print("COIN: HEIGHT = 10 CM, LENGTH = 10 CM")
                
            elif avg_amp >= COIN_H_L_PARAM_10_10 and avg_amp < COIN_H_L_PARAM_30_10:
                print("COIN: HEIGHT = 30 CM, LENGTH = 10 CM")

            else:
                print("COIN: UNKNOWN — out of trained range")
                 
def main(): 
    print("START MENU")
    
    while True : 
        user = input("Continue Y/N? ")
        
        if user == 'y' or user == 'Y' :
            
            mode = input("1: Data Collection\n2: Prediction ")
            
            if mode == "1" : 
            
                typeOfMaterial = input("Coin, Eraser, Others ")
                height = input("Height : ")
                height = height + ' cm'
                length = input("Length : ")
                length = length + ' cm'    
                
                time.sleep(0.5)
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(1, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                      
                data = gather_data()
                SAMPLE_RATE = len(data)
                data = filter_data(data)
                freq = get_freq(data)
                avg_amp = get_avgamp(data)
                max_amp = highest_amp(data)
                visualize_data(data,typeOfMaterial,height,length)
                
                with open("Project 2/vibration.csv", 'a', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow([typeOfMaterial,height,length,freq,avg_amp,max_amp])
                
            elif mode == '2' : 
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(3, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                
                
                data = gather_data()
                SAMPLE_RATE = len(data)
                data = filter_data(data)
                freq = get_freq(data)
                avg_amp = get_avgamp(data)
                max_amp = highest_amp(data)
                predict(freq,avg_amp,max_amp)
                # visualize_data(data,"Pred","Pred","Pred")
                
                
                
        elif user == 'n' or user == 'N' :
            break 
    else : 
        return None 
        
        
if __name__ == "__main__":
    main()
    

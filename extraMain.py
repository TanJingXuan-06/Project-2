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
SAMPLING_RATE = SAMPLE_RATE/TIME  # Number of samples / Time Period 

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
            
        SAMPLE_RATE = len(data_list)
        return data_list
                 
    except (KeyboardInterrupt, serial.SerialException) as e:
        print("Error") 
        
    ser.write(b"STP")       #"Send RUN to STM32"
       
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
    plt.grid()
    plt.show()
    # plot the raw data 
    
def prediction(amp): 
    
    print(f"AMP: {amp}") 
    
    if amp > 240 :
        print("Softest,10CM, 30CM")
        
    elif amp < 30 : 
        print("Softest, 30CM, 10CM")
                
    
    else : 
        if amp > 150 :
            print("Softest, 30CM, 30CM")
            
        else :  
            print("Softest, 10CM, 10CM")
   
def visualize_data2(list) : 
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
    plt.ylim(-100,500)
    plt.show()
    # plot the raw data   
                
def main(): 
    print("START MENU")
    
    while True : 
        user = "y"
        
        if user == 'y' or user == 'Y' :
            
            mode = input("1: Data Collection\n2: Prediction ")
            
            if mode == "1" : 
                            
                print("Start gathering in", end=" ", flush=True)
                for i in range(1, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                    
                data = gather_data()
                amp = highest_amp(data)
                tag  = 1

                visualize_data2(data)                               
                
                with open("Project 2/data_soft.csv", 'a', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow([amp,tag])
                
            elif mode == '2' : 
                
                
                print("Start gathering in", end=" ", flush=True)
                for i in range(1, 0, -1):
                    print(f"\rStart gathering in {i}", end="", flush=True)
                    time.sleep(1)
                
                
                data = gather_data()
                amp = highest_amp(data)
                prediction(amp)
                     
        elif user == 'n' or user == 'N' :
            break 
    else : 
        return None 
        
if __name__ == "__main__":
    main()
    

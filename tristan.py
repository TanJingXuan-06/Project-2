# import 
import serial
from serial.tools import list_ports
import time 
import matplotlib.pyplot as plt
import csv 
import numpy as np 

# define constants 
NOISE_LEVEL = 10        # to define the noise level 
TIME = 10               # time to gather 1 data 
SAMPLING_RATE = 584/10  # Number of samples / Time Period 

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
            
    # calculate the FFT 
    n = len(valid_list)
    fft_result = np.fft.fft(valid_list)
    frequency = np.fft.fftfreq(n, d=1/SAMPLING_RATE)
    
    # Take magnitude and only keep the positive frequencies
    magnitude = np.abs(fft_result)[:n//2]
    frequency = frequency[:n//2]
    dominant_freq = frequency[np.argmax(magnitude)]
    
    return dominant_freq
    
            
            
def main(): 
    print("START MENU")
    user = input("Continue Y/N? ")
    
    if user == 'y' or user == 'Y' : 
        data = gather_data 
        
        freq = get_freq(data)
    
main()
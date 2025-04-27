# import 
import serial
from serial.tools import list_ports
import time 
import matplotlib.pyplot as plt
import csv 
import numpy as np 
from scipy import integrate
import pandas as pd
import matplotlib.pyplot as plt
import ast

# SAMPLES PARAMETERS
NOISE_LEVEL = 25        # to define the noise level 
TIME = 4               # time to gather 1 data 
SAMPLE_RATE = 5062
SAMPLING_RATE = SAMPLE_RATE/TIME  # Number of samples / Time Period 

# FREQUENCY THRESHOLD
FREQ_THRESHOLD = 150 

# ERASER PARAMETERS  
# HEIGHT LENGTH   

# COIN PARAMETERS 
# HEIGHT LENGTH 

COIN_HEIGHT_30 = 2900

PEAK_THRESHOLD = 1500 


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

def highest_amp(adc_values):
    
    return max(adc_values)

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
    # plt.savefig(f"Project 2/plots/DATA.png")
    plt.grid()
    plt.ylim(-100,4100)
    # plt.show()
    # plot the raw data             

def numOfPeaks(adc_values) :

    peak = None 
    zero = 0 
    peak_counter = 0 
    
    for idx in range (len(adc_values)-1) : 
        
        # Ignore the first data         
        if idx > 0 : 
            # If this a peak 
            if (adc_values[idx] > adc_values[idx+1]) and (adc_values[idx] > adc_values[idx-1]) : 
                
                # if data_count is 0 means this is the first peak 
                if peak == None and zero == 0 : 
                    peak = adc_values[idx]
                    
                    if adc_values[idx] > PEAK_THRESHOLD : 
                        peak_counter += 1 
                    
                # not the first peak 
                elif zero == 0 : 
                    peak = adc_values[idx]
                    
                    if adc_values[idx] > PEAK_THRESHOLD : 
                        peak_counter += 1 
                        
                zero = adc_values[idx]
                    
            if adc_values[idx] == 0 : 
                zero = 0 
    
    return peak_counter

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
        if adc_copy[idx] <= 500:
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
 
def diff_between_peaks(adc_values) :
    
    diff_list = []
    
    for idx in range(0,len(adc_values)-1) : 
        
        diff = adc_values[idx] - adc_values[idx+1]
        diff = abs(diff)
        diff_list.append(float(diff))
        
    print(diff_list)
    return diff_list
    
def time_between_peaks(adc_x) : 
    
    time_list = []
    
    for idx in range(0,len(adc_x)-1) : 
        
        diff = adc_x[idx+1] - adc_x[idx]
            
        # Number of points * (TIME PER SAMPLE)    
        time_taken = diff * (TIME/SAMPLE_RATE )
        time_list.append(round(time_taken,2))
        
        
    print(time_list)
    return time_list
  
def visualize_param(csv1, csv2):
    # Read the first CSV
    df1 = pd.read_csv(csv1, header=None, names=['name', 'num_peaks', 'area', 'non_zero'])

    # Read the second CSV
    df2 = pd.read_csv(csv2, header=None, names=['name', 'peak_amp_diff', 'peak_time_diff'])

    # Parse string representations of lists
    df2['peak_amp_diff'] = df2['peak_amp_diff'].apply(lambda x: ast.literal_eval(str(x)))
    df2['peak_time_diff'] = df2['peak_time_diff'].apply(lambda x: ast.literal_eval(str(x)))

    # Compute max values from the lists
    df2['max_peak_amp_diff'] = df2['peak_amp_diff'].apply(lambda x: max(x) if len(x) > 0 else 0)
    df2['max_peak_time_diff'] = df2['peak_time_diff'].apply(lambda x: max(x) if len(x) > 0 else 0)

    # Merge the two DataFrames on 'name'
    df = pd.merge(df1, df2, on='name')

    # Compute Effective Energy per Peak
    df['energy_per_peak'] = df['area'] / (df['num_peaks'] + 1e-6)  # small epsilon to avoid division by zero

    # Create a mapping from name to a numerical position
    name_to_num = {name: idx for idx, name in enumerate(sorted(df['name'].unique()))}

    # Create 6 subplots now
    fig, axs = plt.subplots(6, 1, figsize=(16, 34))
    fig.tight_layout(pad=5)

    # Scatter plot helper
    def scatter(ax, names, values, title, ylabel):
        x_positions = [name_to_num[name] for name in names]
        ax.scatter(x_positions, values, alpha=0.7)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xticks(list(name_to_num.values()))
        ax.set_xticklabels(list(name_to_num.keys()), rotation=90)

    # 1. Number of Peaks
    scatter(axs[0], df['name'], df['num_peaks'], 'Number of Peaks', 'Num Peaks')

    # 2. Area under the Curve
    scatter(axs[1], df['name'], df['area'], 'Area under Curve', 'Area')

    # 3. Number of Non-zero Points
    scatter(axs[2], df['name'], df['non_zero'], 'Non-zero Points', 'Non-zero Count')

    # 4. Max Peak Amplitude Difference per row
    scatter(axs[3], df['name'], df['max_peak_amp_diff'], 'Max Peak Amplitude Difference', 'Max Amp Diff')

    # 5. Max Peak Time Difference per row
    scatter(axs[4], df['name'], df['max_peak_time_diff'], 'Max Peak Time Difference', 'Max Time Diff')

    # 6. Effective Energy per Peak
    scatter(axs[5], df['name'], df['energy_per_peak'], 'Effective Energy per Peak', 'Energy per Peak')

    plt.show()



  
def main(): 
    print("START MENU")
    
    while True : 
        user = input("Continue Y/N? ")
        
        if user == 'y' or user == 'Y' :
            
            time.sleep(0.5)
            user = input("3010, 3030, 1030, 1010: \n")
            print("Start gathering in", end=" ", flush=True)
            for i in range(1, 0, -1):
                print(f"\rStart gathering in {i}", end="", flush=True)
                time.sleep(1)
                    
            data = gather_data()   
            
            data = filter_data(data)
            
            
            
            peaks = numOfPeaks(data)
            area  = areaUnderGraph(data)
            nonZero = nonZeroData(data)
            
            # PEAKS 
            pk = p2p(data)
            pk_x, pk_y = filterPK(pk)
            peak_amp = diff_between_peaks(pk_y)
            peak_time = time_between_peaks(pk_x)
            
            plt.subplot(2,1,1)
            visualize_data(data)
            plt.subplot(2,1,2)
            visualize_data(pk)
            plt.show()
            
            
            with open("Project 2/test1.csv", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user,peaks,area,nonZero])
                
            with open("Project 2/test2.csv", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user,peak_amp,peak_time])
            

                
        elif user == 'n' or user == 'N' :
            break 
    else : 
        return None 
        
        
# if __name__ == "__main__":
#     main()

def test() : 
    visualize_param("Project 2/test1.csv","Project 2/test2.csv")
    

test()

    

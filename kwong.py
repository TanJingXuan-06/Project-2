import matplotlib.pyplot as plt
import numpy as np

def get_avgamp(list) :
    # input  : a list of raw data from stm  
    # output : average of all spikes after threshold
    
    # anything you find relavant to our project 
    # only take highest amplitude ?
    # take multiple highest ampltiude if there's different spikes ? 
    total = 0
    count = 0
    
    for i in list:
        if (i > threshold):
            total += i
            count += 1

    return total/count


def highest_amp(list, threshold):
    # Input : list of raw data, threshold for noise
    # output :  the highest amplitude from the list
    spike_segments = []
    max_spikes = []

    i = 0
    while i < len(adc_values):
    # Wait for a value BELOW threshold
        if adc_values[i] < threshold:
            # Look ahead for rising edge
            j = i + 1
            while j < len(adc_values) and adc_values[j] < threshold:
                j += 1

            # Found start of a spike
            start = j

            # Move forward until signal drops back below threshold
            while j < len(adc_values) and adc_values[j] >= threshold:
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


adc_values = np.array([
    10, 20, 45, 55, 3000, 2900, 30,   # spike 1 (starts ~45, ends ~30)
    10, 8, 4095, 4050, 3990, 20,      # spike 2
    0, 100, 90, 120, 5,               # spike 3
    0, 0, 0
])

threshold = 0

print(get_avgamp(adc_values))
print(highest_amp(adc_values, 50))
visualize_data(adc_values)
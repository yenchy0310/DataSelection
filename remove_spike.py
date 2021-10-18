import numpy as np

def remove_spike(data, channel='583nm #1', threshold=0.1):

    AMS1_spike_index = data[abs(data[channel]-data[channel][0:10].mean())/data[channel][0:10].mean()>threshold].index
    AMS2_spike_index = data[abs(data[channel]-data[channel][0:10].mean())/data[channel][0:10].mean()>threshold].index
    print('AMS1_spike_index', AMS1_spike_index)
    print('AMS2_spike_index', AMS2_spike_index)
    spike_index = np.append(AMS1_spike_index, AMS2_spike_index)
    data.drop(labels=spike_index, inplace=True)
    return data
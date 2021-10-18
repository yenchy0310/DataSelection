import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes

def save_mapping_figure(data_path, sensor_sn, plot_channel, all_select_range):
    '''data: dataframe
       data_path: str
       sensor_sn: str
       plot_channel: list
       all_select_range: dictionary'''
    data = pd.read_csv(data_path)
    
    #create mapping data
    mapping = [None]*data.shape[0]   
    for index, datapoint in all_select_range.values():
        mapping[index-datapoint:index] = data[plot_channel[0]][index-datapoint:index]   
    fig = plt.figure(figsize=(15,5))
    #加圖層
    host = HostAxes(fig, [0.15, 0.1, 0.65, 0.8])
    par1 = ParasiteAxes(host, sharex=host)
    par2 = ParasiteAxes(host, sharex=host)
    par3 = ParasiteAxes(host, sharex=host)
    host.parasites.append(par1)
    host.parasites.append(par2)
    host.parasites.append(par3)
    #figure軸設定
    host.axis["right"].set_visible(False)
    par1.axis["right"].set_visible(True)
    par1.axis["right"].major_ticklabels.set_visible(True)
    par1.axis["right"].label.set_visible(True)
    par2.axis["right2"] = par2.new_fixed_axis(loc="right", offset=(60, 0))
    #匯入數據調整顏色
    fig.add_axes(host)
    x_data = [k for k in range(0, data.shape[0])]
    p1, = host.plot(x_data, data[plot_channel], label=plot_channel[0], color='green', alpha=0.7)
    p2, = host.plot(x_data, mapping, label='mapping', color='orange')
    p3, = par1.plot(x_data, data['External Temp'], label="Temperature", color='red', alpha=0.7)
    p4, = par2.plot(x_data, data['External Humidity'], label="Humidity", color='blue', alpha=0.7)
    # host.set_title(title)
    host.set_title(sensor_sn)
    host.set_xlabel("Data point")
    host.set_ylabel(plot_channel)
    par1.set_ylabel('Temperature')
    par1.set_ylim(-25, 50)
    par2.set_ylabel("Humidity")
    par2.set_ylim(-10, 100)
    host.axis["left"].label.set_color(p1.get_color())
    par1.axis["right"].label.set_color(p3.get_color())
    par2.axis["right2"].label.set_color(p4.get_color())
    fig.legend(bbox_to_anchor=(0., 1.02, 1., .102),  loc=3, ncol=5, mode="expand")   
    savePath = os.path.join(os.path.split(os.path.split(data_path)[0])[0], sensor_sn)
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    fig.savefig(savePath + '/' + sensor_sn + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.png', dpi=200, bbox_inches='tight')
    plt.close()
    print('{} save mapping figure complete'.format(sensor_sn))
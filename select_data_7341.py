import os
import pandas as pd
import numpy as np
from spectrum_convert_CIExy import convert_CIExy
from remove_spike import remove_spike

import plotly.graph_objects as go
# import plotly.offline as offline
# import cufflinks as cf
from plotly.offline import init_notebook_mode, iplot
# cf.go_offline(connected=True)

import warnings
warnings.filterwarnings('ignore')

import json

class select_data_7341():
    def __init__(self, data_path, sensor_sn, plot_channel , MFC1_max_flow_rate, total_flow_rate, cylinder_concentration, threshold=2000, datapoint=50, convert=True, remove_spike_switch= True):
        '''convert : boolean,  default: True
           spectrum convert to CIEx, CIEy on CIE1931 and Lab'''
        
        self.data_path = data_path
        self.sensor_sn = sensor_sn  
        self.datapoint = datapoint
        self.plot_channel = plot_channel
        self.MFC1_max_flow_rate = MFC1_max_flow_rate
        self.total_flow_rate = total_flow_rate
        self.cylinder_concentration = cylinder_concentration
        self.remove_spike_switch= remove_spike_switch
        self.threshold = threshold
        self.convert = convert
        self.data = pd.read_csv(self.data_path).reset_index(drop=True)
        self.moving_average_list = ['410nm #1', '440nm #1', '470nm #1', 
                                    '510nm #1', '550nm #1', '583nm #1', 
                                    '620nm #1', '670nm #1', '900nm #1',

                                    '410nm #2', '440nm #2', '470nm #2', 
                                    '510nm #2', '550nm #2', '583nm #2', 
                                    '620nm #2', '670nm #2', '900nm #2',

                                    'Temperature', 'Humidity']
        
        # Change columns name
        self.data.rename(columns={'External Temp':'Temperature', 'External Humidity':'Humidity'}, inplace=True)
        
        self.header = self.data.columns
        
        if(remove_spike_switch == True):
            self.data = remove_spike(self.data, plot_channel[0], self.threshold).reset_index(drop=True)
        
        # convert CIExy
        if self.convert == True:
            self.data = convert_CIExy(self.data)
            
    def __addPpmColumn(self):
        '''Adding ppm column by converting MFC1 value'''
        self.data['ppm'] = self.data['MFC#1']/100*self.MFC1_max_flow_rate/self.total_flow_rate*self.cylinder_concentration
        return self.data
  
    
    def select_data_A(self, select_range, movingAverage=10):
        '''selected range format
           please set datapoint
           select_range = {'all range': end} 
           or 
           select_range = {'10ppm 30%': 600,
                             '20ppm 30%': 780}'''
        
        self.data = pd.read_csv(self.data_path).reset_index(drop=True)
    
        for i in self.moving_average_list:
            if i in self.header:
                self.data['{}_mv'.format(i)] = self.data[i].rolling(window=movingAverage).mean()
            else:
                continue

        #Adding ppm column          
        self.data = self.__addPpmColumn()

        # selected data
        df_list=[]    
        for b in select_range.values():
            select_data = self.data[b-self.datapoint:b]
            df_list.append(select_data)
                
        # concate selected data
        self.df_select_data = pd.concat(df_list).reset_index(drop=True)
        print('Select data shape:', self.df_select_data.shape)
        
        
    def select_data_B(self, select_range, movingAverage=10):
        '''selected range format
           Don't need to set datapoint
           selected_range = {'region 1': (start, end),
                             'region 2': (900, 1200)}'''
        
        self.data = pd.read_csv(self.data_path).reset_index(drop=True)

        for i in self.moving_average_list:
                    if i in self.header:
                        self.data['{}_mv'.format(i)] = self.data[i].rolling(window=movingAverage).mean()
                    else:
                        continue

        # Adding ppm column        
        self.data = self.__addPpmColumn()

        # selected data
        df_list=[]    
        for a, b in select_range.values():
            select_data = self.data[a:b]
            df_list.append(select_data)
                
        # concate selected data
        self.df_select_data = pd.concat(df_list).reset_index(drop=True)
        print('Select data shape:', self.df_select_data.shape)
        
        
    def select_data_C(self, select_range, movingAverage=10):        
        '''selected range format
           Set datapoint in the dictionary
           selected_range = {'region 1': (end, datapoint),
                             'region 2': (900, 300), 
                             'region 3': (1200, 100),
                             'region 4': (1500, 100),}'''
        
            
        for i in self.moving_average_list:
            if i in self.header:
                self.data['{}_mv'.format(i)] = self.data[i].rolling(window=movingAverage).mean()
            else:
                continue

        # Adding ppm column
        self.data = self.__addPpmColumn()

        # selected data
        df_list=[]    
#         for b, datapoint in self.selected_range.values():
        for b, datapoint in select_range.values():
            select_data = self.data[b-datapoint:b]
            df_list.append(select_data)
                
        # concate selected data
        self.df_select_data = pd.concat(df_list).reset_index(drop=True)
        print('Select data shape:', self.df_select_data.shape)
        
    def save_data(self, saveName, select_range):
        # Save select data 
        self.savePath = os.path.join(os.path.split(os.path.split(self.data_path)[0])[0], self.sensor_sn)
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)
        self.df_select_data.to_csv(self.savePath + '/'+ saveName + '.csv', index=False)

        # Save select range
        temp = saveName.split('_')[2:]
        name = 'selected_range_{}.txt'.format(temp)
        savePath = os.path.join(self.savePath, name)
        with open(savePath, 'w') as fp:
            json.dump(select_range, fp)


    def plot_data_A(self, select_range):
        
        '''selected range format
           selected_range = {'all range': 14000} 
           or 
           selected_range = {'10ppm 30%': 600,
                             '20ppm 30%': 780}'''
        
        plot_data = []
        for j, i in enumerate(self.plot_channel):
            trace = go.Scatter(y=self.data[i], name=self.plot_channel[j])
            plot_data.append(trace)

            mapping = [None]*self.data.shape[0]
            for b in select_range.values():
                mapping[b-self.datapoint:b] = self.data[i][b-self.datapoint:b]

            trace_mapping = go.Scatter(y=mapping, name='mapping {}'.format(j))
            plot_data.append(trace_mapping)

        trace_ppm = go.Scatter(y=self.data['ppm'], name='ppm')
        plot_data.append(trace_ppm)
            
        trace_RH = go.Scatter(y=self.data['Humidity'], name='Humidity')
        plot_data.append(trace_RH)
        
        trace_temp = go.Scatter(y=self.data['Temperature'], name='Temperature')
        plot_data.append(trace_temp)

        layout = go.Layout(xaxis=dict(range=[0, self.data.shape[0]]), title=self.sensor_sn)

        fig = go.Figure(data=plot_data, layout=layout)

        cf.iplot(fig)
     
    def plot_data_B(self, select_range):
        
        '''selected range format
           selected_range = {'region 1': (600, 700),
                             'region 2': (900, 1200)}'''
        
        plot_data = []
        for j, i in enumerate(self.plot_channel):
            trace = go.Scatter(y=self.data[i], name=self.plot_channel[j])
            plot_data.append(trace)

            mapping = [None]*self.data.shape[0]
            for a, b in select_range.values():
                mapping[a:b] = self.data[i][a:b]

            trace_mapping = go.Scatter(y=mapping, name='mapping {}'.format(j))
            plot_data.append(trace_mapping)

        trace_ppm = go.Scatter(y=self.data['ppm'], name='ppm')
        plot_data.append(trace_ppm)
            
        trace_RH = go.Scatter(y=self.data['Humidity'], name='Humidity')
        plot_data.append(trace_RH)
        
        trace_temp = go.Scatter(y=self.data['Temperature'], name='Temperature')
        plot_data.append(trace_temp)

        layout = go.Layout(xaxis=dict(range=[0, self.data.shape[0]]), title=self.sensor_sn)

        fig = go.Figure(data=plot_data, layout=layout)

        cf.iplot(fig)

        
        
        
    def plot_data_C(self, select_range):
                
        '''selected range format
           selected_range = {'region 1': (700-datapoint, 700),
                             'region 2': (1200-datapoint, 1200)}'''
        
        plot_data = []
        for j, i in enumerate(self.plot_channel):
            trace = go.Scatter(y=self.data[i], name=self.plot_channel[j])
            plot_data.append(trace)

            mapping = [None]*self.data.shape[0]
#             for b, datapoint in self.selected_range.values():
            for b, datapoint in select_range.values():
                mapping[b-datapoint:b] = self.data[i][b-datapoint:b]

            trace_mapping = go.Scatter(y=mapping, name='mapping {}'.format(j))
            plot_data.append(trace_mapping)

        trace_ppm = go.Scatter(y=self.data['ppm'], name='ppm')
        plot_data.append(trace_ppm)
            
        trace_RH = go.Scatter(y=self.data['Humidity'], name='Humidity')
        plot_data.append(trace_RH)
        
        trace_temp = go.Scatter(y=self.data['Temperature'], name='Temperature')
        plot_data.append(trace_temp)

        layout = go.Layout(xaxis=dict(range=[0, self.data.shape[0]]), title=self.sensor_sn)

        fig = go.Figure(data=plot_data, layout=layout)

#         cf.iplot(fig)
        fig.show()
        
        
    def plot_select_data(self):
        plot_data = []
        for j, i in enumerate(self.plot_channel):
            trace = go.Scatter(y=self.df_select_data[i], name=self.plot_channel[j])
            plot_data.append(trace)
        
        trace_ppm = go.Scatter(y=self.df_select_data['ppm'], name='ppm')
        plot_data.append(trace_ppm)
            
        trace_RH = go.Scatter(y=self.df_select_data['Humidity'], name='Humidity')
        plot_data.append(trace_RH)
        
        trace_temp = go.Scatter(y=self.df_select_data['Temperature'], name='Temperature')
        plot_data.append(trace_temp)

        layout = go.Layout(xaxis=dict(range=[0, self.df_select_data.shape[0]]), title=self.sensor_sn + " select data")

        fig = go.Figure(data=plot_data, layout=layout)

#         cf.iplot(fig)
        fig.show()

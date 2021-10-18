# import os
# import pandas as pd
# import numpy as np
# import plotly.graph_objs as go

from collections import namedtuple
gaussian = namedtuple('Gaussian', ['mean', 'var'])
gaussian.__repr__ = lambda s: '𝒩(μ={:.3f}, 𝜎²={:.3f})'.format(s[0], s[1])


class One_Dimension_Filter():
    def __init__(self, data, channel):
        self.data = data
        self.channel = channel
        pass

    def predict(self, initial_state, process_model):
        return gaussian(initial_state.mean+process_model.mean, initial_state.var+process_model.var)
    
    def gaussian_multiply(self, pdf1, pdf2):  ## pdf: probability distribution function
        mean = (pdf1.var * pdf2.mean + pdf2.var * pdf1.mean)/(pdf1.var + pdf2.var)
        variance = (pdf1.var * pdf2.var)/(pdf1.var + pdf2.var)
        return gaussian(mean, variance)

    def update(self, prior, likelihood):
        posterior = self.gaussian_multiply(likelihood, prior)
        return posterior


# if __name__ == '__main__':
#     df = pd.read_csv('dual7341_#20210604094223_202108241353.csv')
#     # channel = '583nm #1'
#     channel = ['410nm #1', '440nm #1', '470nm #1',
#                 '510nm #1', '550nm #1', '583nm #1',
#                 '620nm #1', '670nm #1', '900nm #1']
#     # filter_data=[]
#     # process_std=.12
#     # process_model = gaussian(0., process_std)
#     # AMS_std = 1.8

#     # x=gaussian(10000, 3000) ## Initial state guess
#     # data = np.array(df['550nm #1'])

#     # test=One_Dimension_Filter(df, channel)
#     for wavelength in channel:
#         filter_data=[]
#         process_std=.12
#         process_model = gaussian(0., process_std)
#         AMS_std = 1.8

#         x=gaussian(10000, 3000) ## Initial state guess
#         data = np.array(df[wavelength])
#         test=One_Dimension_Filter(data, wavelength)

#         for signal in test.data:
#             prior=test.predict(x, process_model)
#             x=test.update(prior, gaussian(signal, AMS_std))

#             filter_data.append(x.mean)

#         fig=go.Figure()
#         fig.add_trace(go.Scatter(y=data[:], name= wavelength+' Raw Signal'))
#         fig.add_trace(go.Scatter(y=filter_data[:], name=wavelength+' Filtered Signal'))
#         fig.show()
#     print('Done!')
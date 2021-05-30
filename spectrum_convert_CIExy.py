import numpy as np
import pandas as pd
import colour
from scipy import interpolate


def _smoothSpectrum(wave_intensity):
    
    # smooth raw data
    wave = [410, 440, 470, 510, 550, 583, 620, 670]
    func = interpolate.interp1d(wave, wave_intensity, kind='cubic')
    new_wave = np.arange(410, 671, 1)
    new_wave_intensity = func(new_wave)
    sample_sd_data = dict(zip(new_wave, new_wave_intensity))
    
    return sample_sd_data

def _spectrumToCIExy(sample_sd_data):
    
    # start convert spectrum to CIExy
    sd = colour.SpectralDistribution(sample_sd_data, name='Sample')
    cmfs = colour.STANDARD_OBSERVERS_CMFS['CIE 1931 2 Degree Standard Observer']
    illuminant = colour.ILLUMINANTS_SDS['D65']
    XYZ = colour.sd_to_XYZ(sd, cmfs, illuminant)
    
    # select colourspace        
    CIExy = colour.XYZ_to_xy(XYZ) # CIE1931
    Lab = colour.XYZ_to_Lab(XYZ)
    
    return CIExy, Lab

def convert_CIExy(data):

    print('spectrum convert to CIE and Lab process ...')
     
    CIExy_1_list = []
    Lab_1_list = []
    CIExy_2_list = []
    Lab_2_list = []
    for _, series in data.iterrows():
        # smooth raw data
        # normalization
        wave_intensity_1 = series[['410nm #1', '440nm #1', '470nm #1', '510nm #1', '550nm #1', '583nm #1', '620nm #1', '670nm #1']]/65535 
        wave_intensity_2 = series[['410nm #2', '440nm #2', '470nm #2', '510nm #2', '550nm #2', '583nm #2', '620nm #2', '670nm #2']]/65535 
       
        # create a dictionary key:wavelength value:raw data
        sample_sd_data_1 = _smoothSpectrum(wave_intensity_1)
        sample_sd_data_2 = _smoothSpectrum(wave_intensity_2)

        CIExy_1, Lab_1 = _spectrumToCIExy(sample_sd_data_1)
        CIExy_1_list.append(CIExy_1)
        Lab_1_list.append(Lab_1)
        CIExy_2, Lab_2 = _spectrumToCIExy(sample_sd_data_2)
        CIExy_2_list.append(CIExy_2)
        Lab_2_list.append(Lab_2)

    # add CIExy columns
    df_1 = pd.DataFrame(data=CIExy_1_list, columns=['CIEx #1', 'CIEy #1'])
    df_2 = pd.DataFrame(data=Lab_1_list, columns=['L #1', 'a #1', 'b #1'])
    df_3 = pd.DataFrame(data=CIExy_2_list, columns=['CIEx #2', 'CIEy #2'])
    df_4 = pd.DataFrame(data=Lab_2_list, columns=['L #2', 'a #2', 'b #2'])
    data = pd.concat([data, df_1, df_2, df_3, df_4], axis=1)   
    
    print('spectrum convert to CIE and Lab process complete')

    return data


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 16:54:02 2025

@author: Ryoichi Koga
"""
import os
import numpy as np
import astropy.io.fits as iofits
import pandas as pd
from datetime import datetime

#Input directory name and period
dir_file = "(input path)"
period = "2013"
base_year = int(period)

#List file for the specified period
file = [f for f in os.listdir(dir_file) if"."+ period in f and f.endswith(".fits")]
#n_file = len(file)

#ROI range
xp1,xp2 = 800,900 #plot range (wavelength)
yp1,yp2 = 350,450
x1 = np.arange(1024)
y1 = np.arange(1024)

AobsT,ADOY,ALon,ALat,ALT,ARE,Arad, Ayear = [],[],[],[],[],[],[],[] #Create empty array
base_time = datetime(base_year, 1, 1, 0, 0, 0) #Base time

for filename in file:
    print(filename)
    #fits data open
    try:
        with iofits.open(dir_file+filename) as hdul: #Header/Data Unit
            header0 = hdul[0].header
            n_ext = header0["NEXTEND"]
    
            for i2 in np.arange(2,n_ext,1): #Skip primary header and 1day total count
                header1 = hdul[i2].header
                data1 = hdul[i2].data
                #Read geometric parameter
                obsT = header1["DATE-OBS"] #Time of the observation
                Lon = header1["SLONESC"] #[deg] Sub-s/c longitude of earth 
                Lat = header1["SLATESC"] #[deg] Sub-s/c lattude of earth 
                LT = header1["LTESC"] #[hr]  Local time of s/c seen from earth 
                RE = header1["RADIESC"]
                AobsT.append(obsT)
                ALon.append(round(Lon, 4))
                ALat.append(round(Lat, 4))
                ALT.append(round(LT, 4))
                ARE.append(round(RE, 1))
                #calculate elaped time from 2014/1/1
                time_obj = datetime.strptime(obsT, "%Y-%m-%dT%H:%M:%S")
                elapsed_seconds = (time_obj - base_time).total_seconds()
                DOY = elapsed_seconds / (24 * 60 * 60) + 1
                ADOY.append(round(DOY, 6))
                Ayear.append(time_obj.year)
                
                #total counts of ROI
                rad1 = np.sum(data1[yp1:yp2+1,xp1:xp2+1])
                Arad.append(rad1)
                
    except Exception as e:
        print(f"Error: {e}")

#List => numpy array
AobsT,ALon,ALat = np.asarray(AobsT),np.asarray(ALon),np.asarray(ALat)
ALT,ARE,ADOY = np.asarray(ALT),np.asarray(ARE),np.asarray(ADOY)
Arad = np.asarray(Arad)

dict1=dict(Time=AobsT,DOY=ADOY,Year=Ayear,Lon=ALon, Lat=ALat, LT=ALT,\
           Geocenter=ARE, Count=Arad) #Create DataFram from dictionary
df = pd.DataFrame(data=dict1)
df = df.sort_values(by="DOY").reset_index(drop=True) #sort by number of DOY
#Save file
dir_s = "(input the path which save the file)"
df.to_csv(dir_s+"Hisaki_geometry_radiation"+period+".csv",index = None)
print(df.head())

#print(file)

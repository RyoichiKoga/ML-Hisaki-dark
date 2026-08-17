#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 13 11:09:14 2025

@author: Ryoichi Koga
"""

#Load monthly DST data
import pandas as pd
import numpy as np
import datetime
import tqdm
import os

#Input file name
# (Example) WWW_aeasy01667914.dat => 2018/1/1 0:0 -2018/12/31 23:59
dir1 = "(input the path name)"
period = "2013"
file = f"WWW_aeasy{period}.dat" #Year 20XX + month YY
#Read DST text file
widths = np.concatenate([[12],[2],[2],[2],[1],[2],[3],[10],np.full(60,6)])#,[6]])
#last values (1h average) are not read
dfD = pd.read_fwf(dir1 + file,widths=widths,header=None,skipfooter=1)

#Create data array
Aloc = np.arange(8,68,1) #data array in one minute
#SYM-H in April
#Mask1 = (dfD.loc[:,2]==4)
Mask2 = (dfD.loc[:,4]=="H")
Mask3 = (dfD.loc[:,6]=="SYM")
filter = np.where((Mask2)&(Mask3))[0]
nt = len(dfD.loc[filter])

# Temporarily store all 60-minute values in a list 
# (each element is a NumPy array of length 60)
y_list = [dfD.loc[idx, Aloc].values for idx in filter]
# Flatten them into a single 1D array
ytest = np.concatenate(y_list)

    
#Create time priod array (x)
#extract Date information
A_year = 2000 + dfD.iloc[:,1].astype(int) 
A_month =  dfD.iloc[:,2]
A_day =  dfD.iloc[:,3]
A_hour = dfD.iloc[:,5]
#Standard time
A0 = datetime.datetime(int(period),1,1,0,0,0)

A_xtest= np.arange(0,60,1)
A1, Elap = [],[]
for i in tqdm.tqdm(np.arange(0,nt,1)):
    for j in A_xtest:
        Date1 = datetime.datetime(year=A_year[i],month=A_month[i]\
                                  ,day=A_day[i],hour=A_hour[i],minute=A_xtest[j])
        A1.append(Date1)
        ET = Date1 - A0 #DOY1 = 1/1
        Elap.append(ET.days + ET.seconds/(60.0*60.0*24.0) + 1)

#Create DataFrame
df_symh = pd.DataFrame({
    "Datetime": A1,
    "DOY":Elap,
    "SYM-H": ytest.astype(float)  # convert float if necessary 
})

# Set the save directory and file name
save_dir = "(input the path which save file)"
save_file = f"SYM-H_1min_{period}.csv"

# Save as CSV（no index）
df_symh.to_csv(os.path.join(save_dir, save_file), index=False)

# print information
print(save_file)
print(df_symh.head())

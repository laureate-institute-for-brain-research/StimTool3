#!/usr/bin/env python

# Format the schedule

import pandas as pd
import numpy as np


def main():
    
    old = pd.read_csv('main.csv', header=None)
   

    # new df
    df = pd.DataFrame([np.append( old.iloc[0,0:2].values,  old.iloc[1,0:2].values)], columns=list('ABCD'))

    for col in range(0,400,2):
        if col < 2: continue # skip first elm
        df2 = pd.DataFrame([np.append( old.iloc[0,col:col+2].values,  old.iloc[1,col:col+2].values)], columns=list('ABCD'))
        df = df.append(df2, ignore_index=True)
    
    df.to_csv('main_formatted.csv', index=False)

if __name__ == '__main__':
    main()
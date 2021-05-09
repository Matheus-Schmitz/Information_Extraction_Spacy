#!/usr/bin/env python
# coding: utf-8

import pandas as pd 

# Load the csvs as pandas DataFrames
csvObj1 = pd.read_csv('task1_run1.csv')
csvObj2 = pd.read_csv('task1_run2.csv')
csvObj3 = pd.read_csv('task1_run3.csv')
csvObj4 = pd.read_csv('task1_run4.csv')
csvObj5 = pd.read_csv('task1_run5.csv')

# Concatenate removing duplicates
df = pd.concat([csvObj1, csvObj2, csvObj3, csvObj4, csvObj5], ignore_index=True, sort=False).drop_duplicates(['url'], keep='last')
df = df.sample(frac=1)

# Save as a single csv , removing the header
df.to_csv('Matheus_Schmitz_hw02_bios.csv', header=False, index=False)





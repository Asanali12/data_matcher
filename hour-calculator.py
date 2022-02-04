import datetime
import sqlite3
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import time as t
from sklearn.preprocessing import OneHotEncoder
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tabulate import tabulate

#USERS 6 AND 12 HAD CORRUPTED DATA

def binary_search(arr, x, isStart):
    low = 0
    high = len(arr) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if arr.iloc[mid] < x:
            low = mid + 1
        elif arr.iloc[mid] > x:
            high = mid - 1
        else:
            return mid
    
    return mid + 1

def find_delta(dictionary):
    current = None
    previous = None
    gaps = {}

    for value in dictionary.values():
        for i in range(0, len(value) - 1):
            if i == 0 and previous == None:
                previous = value[i]['dateTime']
            else:    
                current = value[i]['dateTime']
                previous = value[i - 1]['dateTime']
                delta = round((current - previous).total_seconds(), 3)
                if delta < 7200:
                    if delta in gaps:
                        gaps[delta] += 1
                    else:
                        gaps[delta] = 1
    return gaps

def filter_present(dictionary, recorded_images):
    return dict(filter(lambda element: recorded_images.iloc[element[0]]['state'] == "Present", dictionary.items()))

def filter_non_empty(dictionary):
    return dict(filter(lambda element: len(element[1]) != 0, dictionary.items()))

def get_data(id):
    con = sqlite3.connect(id)
    
    cur = con.cursor()
    input_signals = []
    recorded_images = []
    matched = []
    
    input_signals = pd.read_sql('SELECT * FROM signals;', con)
    input_signals['dateTime']= pd.to_datetime(input_signals['dateTime'])
    
    recorded_images = pd.read_sql('SELECT id, dateTime, state FROM images;', con)
    recorded_images['dateTime']= pd.to_datetime(recorded_images['dateTime'])

    con.close()
    

    results = {}
    current = recorded_images.iloc[0]['dateTime']
    next = recorded_images.iloc[1]['dateTime']
    
    input_signals = input_signals.sort_values('dateTime')


    for i in range(0, len(recorded_images) - 2):
        fromIndex = binary_search(input_signals['dateTime'], current, True)
        toIndex = binary_search(input_signals['dateTime'], next, False)
        results[recorded_images['id'].iloc[i]] = [input_signals.iloc[x] for x in range(fromIndex, toIndex)]
        current = next
        next = recorded_images.iloc[i+2]['dateTime']


    non_empty = filter_non_empty(results)
    present = filter_present(results, recorded_images)
    present_and_non_empty = filter_non_empty(present)
    answer = [find_delta(non_empty), find_delta(present_and_non_empty)]
    return answer

time_results = {}
time_results['data'] = get_data('signals.sqlite')

#described_format = []
describe_list = []
for k, v in time_results['data'][0].items():
    helper_list = [float(k)]*v
    describe_list.extend(helper_list)
for_describe = sorted([item for item in describe_list if item > 0])
#described_format.append(for_describe)
total_seconds = 0
for i in for_describe:
    total_seconds += i
print("your hours:", total_seconds / 3600)
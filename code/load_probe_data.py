import os
import csv
from ProbeData import ProbeData

def read_csv(data_path):    
    f = open(data_path, 'r')
    probe_data = []
    with f:
        reader = csv.reader(f, delimiter=",")
        all_rows = []
        target_rows = []
        cnt = 0
        for row in reader:
            sampleID, dateTime, sourceCode, latitude, longitude, altitude, speed, heading = row
            probe_data.append(ProbeData(sampleID, dateTime, sourceCode, latitude, longitude, altitude, speed, heading))

    return probe_data
            
        
# data_path = "../data/Partition6467ProbePoints.csv"
# read_csv(data_path)

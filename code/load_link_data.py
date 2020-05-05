import os
import csv
from LinkData import LinkData
def read_csv(data_path):    
    f = open(data_path, 'r')
    link_data = []
    with f:
        reader = csv.reader(f, delimiter=",")
        
        for row in reader:
            linkPVID, refNodeID, nrefNodeID, length, functionalClass, directionOfTravel, speedCategory, fromRefSpeedLimit, toRefSpeedLimit, fromRefNumLanes, toRefNumLanes, multiDigitized, urban, timeZone, shapeInfo, curvatureInfo, slopeInfo = row
            link_data.append(LinkData(linkPVID, refNodeID, nrefNodeID, length, functionalClass, directionOfTravel, speedCategory, fromRefSpeedLimit, toRefSpeedLimit, fromRefNumLanes, toRefNumLanes, multiDigitized, urban, timeZone, shapeInfo, curvatureInfo, slopeInfo))
    return link_data
    
# data_path = "../data/Partition6467LinkData.csv"
# read_csv(data_path)
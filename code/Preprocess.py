import pandas as pd 
import math
from pyproj import Proj, transform
def preprocess(df_probe, df_link):
    ecef = Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = Proj(proj='latlong', ellps='WGS84', datum='WGS84')
 
    idx = 0
    for lat, lon, alt in zip(df_probe['latitude'], df_probe['longitude'], df_probe['altitude']):
        # if idx>10:
        #     break
        x,y,z=converter(ecef,lla, lat,lon,alt)
        df_probe['latitude'][idx] = x
        df_probe['longitude'][idx] = y
        df_probe['altitude'][idx] = z
        idx+=1
        
    # for lat, lon, alt in zip(df_probe['latitude'], df_probe['longitude'], df_probe['altitude']):
    #     print(lat,lon,alt)
    idx = 0
    for link_shape in df_link['shapeInfo']:
        # if idx>10:
        #     break
        link_shape = link_shape.split('|')
        newstr = ''
        for i in range(len(link_shape)):
            lat,lon,alt = link_shape[i].split('/')
            if alt=='':
                alt = '0'
            x,y,z=converter(ecef,lla, float(lat),float(lon),float(alt))
            newstr += str(x)+"/"+str(y)+"/"+str(z)+"|"
        newstr = newstr[:-1]
        df_link['shapeInfo'][idx] = newstr
        idx+=1  
    # idx = 0
    # for link_shape in df_link['shapeInfo']:
    #     if idx>10:
    #         break
    #     print(link_shape)
    #     idx+=1
    return df_probe, df_link

def converter(ecef, lla, lat, lon, alt):
    x,y,z = transform(lla, ecef, lon, lat, alt, radians=False)
    return x,y,z

probe_path = 'data/Partition6467ProbePoints.csv'
link_path = 'data/Partition6467LinkData.csv'
df_probe = pd.read_csv(probe_path,names=["sampleID", "dateTime", "sourceCode", "latitude", "longitude", "altitude", "speed", "heading"])
df_link = pd.read_csv(link_path,names=["linkPVID", "refNodeID", "nrefNodeID", "length", "functionalClass", "directionOfTravel", "speedCategory", "fromRefSpeedLimit", "toRefSpeedLimit", "fromRefNumLanes", "toRefNumLanes", "multiDigitized", "urban", "timeZone", "shapeInfo", "curvatureInfo", "slopeInfo"])
df_probe, df_link = preprocess(df_probe,df_link)
df_probe.to_csv('data/new_probe_data.csv', index=False)
df_link.to_csv('data/new_link_data.csv', index=False)
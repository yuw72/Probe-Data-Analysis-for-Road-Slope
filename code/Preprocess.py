import pandas as pd 
from math import *
import datetime
from pyproj import Proj, transform
def preprocess(df_probe, df_link):
    ecef = Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    # t1 = datetime.datetime.now()
    idx = 0
    for lat, lon, alt in zip(df_probe['latitude'], df_probe['longitude'], df_probe['altitude']):
        # if idx>1000:
        #     break
        if idx%1000==0:
            print("index: ",idx)
        x,y,z=converter(lat,lon,alt)
        df_probe.at[idx,'latitude'] = x
        df_probe.at[idx,'longitude'] = y
        df_probe.at[idx,'altitude'] = z

        idx+=1
    # t2 = datetime.datetime.now()
    # print(t2-t1)
    # for lat, lon, alt in zip(df_probe['latitude'], df_probe['longitude'], df_probe['altitude']):
    #     print(lat,lon,alt)
    # idx = 0
    # for link_shape in df_link['shapeInfo']:
    #     # if idx>100:
    #     #     break
    #     if idx%1000==0:
    #         print("index: ",idx)
    #     link_shape = link_shape.split('|')
    #     newstr = ''
    #     for i in range(len(link_shape)):
    #         lat,lon,alt = link_shape[i].split('/')
    #         if alt=='':
    #             alt = '0'
    #         x,y,z=converter(float(lat),float(lon),float(alt))
    #         newstr += str(x)+"/"+str(y)+"/"+str(z)+"|"
    #     newstr = newstr[:-1]
    #     df_link['shapeInfo'][idx] = newstr
    #     idx+=1  
    # print(datetime.datetime.now()-t2)
    # idx = 0
    # for link_shape in df_link['shapeInfo']:
    #     if idx>10:
    #         break
    #     print(link_shape)
    #     idx+=1
    return df_probe, df_link

def converter(latitude, longitude, height):
    """Return geocentric (Cartesian) Coordinates x, y, z corresponding to
    the geodetic coordinates given by latitude and longitude (in
    degrees) and height above ellipsoid. The ellipsoid must be
    specified by a pair (semi-major axis, reciprocal flattening).

    """
    WGS84 = 6378137, 298.257223563
    φ = radians(latitude)
    λ = radians(longitude)
    sin_φ = sin(φ)
    a, rf = WGS84           # semi-major axis, reciprocal flattening
    e2 = 1 - (1 - 1 / rf) ** 2  # eccentricity squared
    n = a / sqrt(1 - e2 * sin_φ ** 2) # prime vertical radius
    r = (n + height) * cos(φ)   # perpendicular distance from z axis
    x = r * cos(λ)
    y = r * sin(λ)
    z = (n * (1 - e2) + height) * sin_φ
    return x, y, z

probe_path = 'data/Partition6467ProbePoints.csv'
link_path = 'data/Partition6467LinkData.csv'
df_probe = pd.read_csv(probe_path,names=["sampleID", "dateTime", "sourceCode", "latitude", "longitude", "altitude", "speed", "heading"])
df_link = pd.read_csv(link_path,names=["linkPVID", "refNodeID", "nrefNodeID", "length", "functionalClass", "directionOfTravel", "speedCategory", "fromRefSpeedLimit", "toRefSpeedLimit", "fromRefNumLanes", "toRefNumLanes", "multiDigitized", "urban", "timeZone", "shapeInfo", "curvatureInfo", "slopeInfo"])
df_probe, df_link = preprocess(df_probe,df_link)
df_probe.to_csv('data/new_probe_data.csv', index=False)
# df_link.to_csv('data/new_link_data.csv', index=False)
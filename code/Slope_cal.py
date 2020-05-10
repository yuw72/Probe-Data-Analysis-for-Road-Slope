import numpy as np
import math
import pandas as pd
from sklearn.metrics import accuracy_score

# def cal_error():
#     # TODO:
#     return err

# pass
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

# pass
def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.cos(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))

# pass
def mapping(ref, non_ref, probe):
    """return distance away from reference node"""
    v1 = (ref[0]-non_ref[0], ref[1]-non_ref[1], ref[2]-non_ref[2])
    v2 = (ref[0]-probe[0], ref[1]-probe[1], ref[2]-probe[2])
    cosin = angle_between(v1,v2)
    dist = math.sqrt((probe[0]-ref[0])**2+(probe[1]-ref[1])**2+(probe[2]-ref[2])**2)*cosin
    return dist


# {sampleID0: [linkPVID0, linkPVID1, ...], sampleID1: [linkPVID0, linkPVID1, ...], ...]
# pass
def get_dictionary(routes):
    """input: routes dictionary"""
    """return: new dictionary"""
    probe_dict = {}
    for probe in routes.keys():
        for i,link in enumerate(routes[probe]):
            if link not in probe_dict:
                probe_dict[link] = []
                probe_dict[link].append((probe,i))
            else:
                probe_dict[link].append((probe,i))
    return probe_dict

# pass
def get_link(df_link, linkPVID):
    return df_link.loc[df_link['linkPVID'] == linkPVID]

# pass
def get_probe(df_probe, probe_id):
    sample_id = probe_id[0]
    idx = probe_id[1]
    return df_probe.loc[df_probe['sampleID'] == sample_id].iloc[idx]

# pass
def find_two_closest_point(dist, points): 
    min_dist = math.inf
    min_point = None
    for point in points:
        p_dist = point[0]
        diff = abs(dist-p_dist)
        if diff<min_dist:
            min_dist = diff
            min_point = point
    min_dist = math.inf
    min_point2 = None
    for point in points:
        p_dist = point[0]
        diff = abs(dist-p_dist)
        if diff<min_dist and point!=min_point:
            min_dist = diff
            min_point2 = point
    return min_point, min_point2

# pass
def cal_slope(dist, points):
    point1, point2 = find_two_closest_point(dist,points)
    dist1,alt1 = point1
    dist2,alt2 = point2
    length = math.sqrt(abs((dist1-dist2)**2-(alt1-alt2)**2))
    if length ==0:
        length = 1
    slope = abs(alt1-alt2)/length
    return slope
    

def calc(probe_dict, df_probe, df_link, linkPVID):
    link = get_link(df_link, linkPVID)
    shape_info = link['shapeInfo'].values[0]
    shape_info = shape_info.split('|')
    lat, lon, alt = shape_info[0].split('/')
    ref = (float(lat),float(lon),float(alt))
    lat, lon, alt = shape_info[len(shape_info)-1].split('/')
    non_ref = (float(lat),float(lon),float(alt))
    points = []
    for probe_id in probe_dict[linkPVID]:
        probe = get_probe(df_probe, probe_id)
        probe_loc = (probe['latitude'], probe['longitude'], probe['altitude'])
        dist = mapping(ref, non_ref, probe_loc)
        points.append((dist,probe_loc[2]))
    slope_info = link['slopeInfo'].values[0]
    if slope_info != slope_info:
        return None,None
    # slope_info = link['slopeInfo'].values[0].split('|')
    
    slope_info = slope_info.split('|')
    
    slopes = []
    slope_truths = []
    
    if len(points) <2:
        if len(points)==0:
            points.append(non_ref)
        for i,info in enumerate(slope_info):            
            dist, slope_truth = slope_info[i].split('/')
            dist = float(dist)
            slope_truth = float(slope_truth)
            point = points[0]
            div = abs(point[0]**2-(ref[2]-point[1])**2)
            if div ==0 :
                div = 1
            slope = (ref[2]-point[1])/math.sqrt(div)
            slopes.append(slope)
            slope_truths.append(slope_truth)    
        return slopes, slope_truths
    else:
        for i,info in enumerate(slope_info):            
            dist, slope_truth = slope_info[i].split('/')
            dist = float(dist)
            slope_truth = float(slope_truth)
            slope = cal_slope(dist, points)
            slopes.append(slope)
            slope_truths.append(slope_truth)
        return slopes, slope_truths
    

def get_slope(routes, df_probe, df_link):
    count = 0
    err = 0
    probe_dict = get_dictionary(routes)
    result = []
    for linkPVID in probe_dict.keys():
        slopes, slope_truths = calc(probe_dict, df_probe, df_link, linkPVID)
        if slopes == None:
            continue
        res = [linkPVID, slope_truths, slopes]
        result.append(res)
        for i, slope in enumerate(slopes):
            err += abs(slope-slope_truths[i])**2
            count += 1
        # print("slope: ",slopes," truth: ", slope_truths)
    err = err/count
    print(err)
    df_result = pd.DataFrame(result, columns = ['linkPVID','GivenSlope','SlopeExperiment']) 
    df_result.to_csv('data/result.csv', index=False)


# probe_path = 'data/new_probe_data.csv'
# link_path = 'data/new_link_data.csv'

# df_probe = pd.read_csv(probe_path,nrows=1000)
# df_link = pd.read_csv(link_path,nrows = 1000)


# routes = {3496:[62007637,51881672,51881767,51881768,51881825],4552:[62007637,51881672,51881767,51881768]}
# # dist = mapping(ref=(2,2),probe=[0,1])
# get_slope(routes, df_probe, df_link)

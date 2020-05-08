import numpy as np
import pandas as pd
# from Preprocess import *
from Prob_cal import *
# from Slope_cal import *

def take_value(e):
    return e[1]


def find_near_links(probe, df_link):
    """find nearest links of a probe points within some threshold

    Arguments:
        probe {dataframe} -- a probe point
        df_link {dataframe} -- all link data

    Returns:
        list -- list of links found within threshold
    """

    threshold = 4  # (meters)
    num = 4  # choose nearest 4 links
    links_dis = []  # list of tuples
    links = []

    # Calculate four coords
    x_min = float(probe['latitude']) - 4
    x_max = float(probe['latitude']) + 4
    y_min = float(probe['longitude']) - 4
    y_max = float(probe['longitude']) + 4

    # find links with ref and nref both in the coord range
    for index, link in df_link.iterrows():
        link_shape = link['shapeInfo'].split('|')
        flag = 1
        # check if all the points are inside the distance
        for index in range(len(link_shape)):
            p = link_shape[index].split('/')
            if (float(p[0]) > x_max) or (float(p[0]) < x_min) or (float(p[1]) > y_max) or (float(p[1]) < y_min):
                flag = 0
                break
        # yes
        if flag == 1:
            dis = get_dist(probe, link)
            links_dis.append((link['linkPVID'], dis))

    # find top 4
    links_dis.sort(key=take_value)
    for link in links_dis[:4]:
        links.append(link[0])
    
    return links


def gen_routes(df_probe, df_link):
    """ generate sets of possible routes (each contains a set of connected, ordered links) of current sample.  
        Each of n probe points are mapped to a link. Links can be the same. Output links number should match probe number.

    Arguments:
        df_probe {dataframe} -- probe points of this sample (so same sampleID) in time order
        df_link {dataframe} -- all links

    Returns:
        routes list of array -- list of possible routes [[linkPVID0, linkPVID1, linkPVID2, ...], [linkPVID0, linkPVID1, linkPVID2, ...]]
    """

    links = []
    routes = []
    num = df_probe.shape[0]
    
    for index, probe in df_probe.iterrows():
        links.append(find_near_links(probe, df_link))

    links = np.array(links)  # n * 4

    routes = links[0].reshape(links.shape[1],1)
    for state in links[1:]:
        new_route = []
        for route in routes:
            for link in state:
                new_route.append(np.append(route, link))
        routes = new_route
    return routes


def viterbi(df_probe, df_link):
    """ Get the route (set of links in order) with the highest probability

    Arguments:
        df_probe {dataframe} -- all probe data
        df_link {dataframe} -- all link data

    Returns:
        v_route dictionary -- dic of links with highest prob for each sample {sampleID0: [linkPVID0, linkPVID1, ...], sampleID1: [linkPVID0, linkPVID1, ...], ...]
    """

    samples = df_probe.sampleID.unique()
    num_samples = len(samples) 
    v_route = {}

    for sample in samples:
        df = df_probe.loc[df_probe['sampleID'] == sample]  # df of probes of current sample
        df = df.sort_values(by=['dateTime'])
        routes = gen_routes(df, df_link)  # set of possible routes for this sample
        max_prob = 0
        
        for route in routes:
            # P(link0)
            link0 = df.loc[df['linkPVID'] == route[0]]
            p_link0 = get_initial_prob(df[0], link0, df_link)

            # Multiplication of emission probs
            p_emis = 1
            for i in range(len(route)) + 1:
                probe = df[i]
                link = df.loc[df['linkPVID'] == route[i]]
                p_emis *= get_emission_prob(probe, link)

            # Multiplication of transition probs
            p_trans = 1
            for i in range(len(route) - 1):
                link1 = df.loc[df['linkPVID'] == route[i]]
                link2 = df.loc[df['linkPVID'] == route[i+1]]
                p_trans *= get_transition_prob(link1, link2, df_link)
            
            # calculate viterbi prob of this route
            p_tot = p_link0 * p_emis * p_trans
            if p_tot > max_prob:
                max_route = route
                max_prob = p_tot

        # store route of highest probability for each sample
        v_route[sample] = max_route

    return v_route


if __name__ == "__main__":
    probe_path = 'data/Partition6467ProbePoints.csv'
    link_path = 'data/Partition6467LinkData.csv'

    df_probe = pd.read_csv(probe_path, nrows=10)
    df_link = pd.read_csv(link_path, nrows=10)

    df_probe.columns = ['sampleID', 'dataTime', 'sourceCode', 'latitude', 'longitude', 'altitude', 'speed', 'heading']
    df_link.columns = ['linkPVID', 'refNodeID', 'nrefNodeID', 'length', 'functionalClass', 'directionofTravel',
                       'speedCategory', 'fromRefSpeedLimit',
                       'toRedSpeedLimit', 'fromRefNumLanes', 'toRefNumLanes', 'multiDigitized', 'urban', 'timeZone',
                       'shapeInfo', 'curvatureInfo', 'slopeInfo']

    # preprocess data
    df_probe, df_link = preprocess(df_probe, df_link)

    # Mapmatching
    routes = viterbi(df_probe, df_link)

    # calculate slope
    slopes = get_slope(routes, df_link)

    # calculate error
    err = cal_error(slopes, df_link)
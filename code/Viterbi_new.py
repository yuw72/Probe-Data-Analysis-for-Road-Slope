import numpy as np
import pandas as pd
from Prob_cal import *
from tqdm import tqdm
import json

def take_value(e):
    return e[1]


def find_near_links(probe, df_link):
    """find nearest links of a probe points within some threshold

    Arguments:
        probe {dataframe} -- a probe point
        df_link {dataframe} -- all link data

    Returns:
        list -- list of links found within threshold (linkPVID)
    """

    threshold = 200  # (meters)
    num = 4  # choose nearest 4 links
    links_dis = []  # list of tuples
    links = []

    # Calculate four coords
    x_min = float(probe['latitude']) - threshold
    x_max = float(probe['latitude']) + threshold
    y_min = float(probe['longitude']) - threshold
    y_max = float(probe['longitude']) + threshold

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
            links_dis.append((link, dis))

    # find top 4
    links_dis.sort(key=take_value)
    for link in links_dis[:num]:
        links.append(link[0])
    
    return links


def viterbi_new(df_probe, df_link):
    """ Get the route (set of links in order) with the highest probability

    Arguments:
        df_probe {dataframe} -- all probe data
        df_link {dataframe} -- all link data

    Returns:
        v_route dictionary -- dic of links with highest prob for each sample {sampleID0: [linkPVID0, linkPVID1, ...], sampleID1: [linkPVID0, linkPVID1, ...], ...}
    """

    samples = df_probe['sampleID'].unique()
    v_route = {}

    for sample in tqdm(samples):
        df = df_probe.loc[df_probe['sampleID'] == sample]  # df of probes of current sample
        df = df.sort_values(by=['dateTime'])
        T1 = np.zeros((4, df.shape[0]))
        T2 = np.zeros((4, df.shape[0]), dtype=int)
        links = np.empty((df.shape[0], 4), dtype=object)
        route = [None]*df.shape[0]

        # Initial
        links0 = find_near_links(df.iloc[0], df_link) # Need change return format
        links[0,:len(links0)] = links0
        for i in range(len(links0)):
            T1[i,0] = get_initial_prob(df.iloc[0], links0[i], df_link) * get_emission_prob(df.iloc[0], links0[i])

        # Forward
        for j in range(1, df.shape[0]):
            probe = df.iloc[j]  # current probe
            curr_links = find_near_links(probe, df_link)  # links of current probe
            links[j,:len(curr_links)] = curr_links
            for i in range(len(curr_links)):
                link = curr_links[i]
                max_prob = 0
                for k in range(4):  # iter prev links
                    if T1[k, j-1] != 0:
                        prob = T1[k,j-1] * get_transition_prob(link, links[j-1,k], df_link) * get_emission_prob(probe, link)
                    else:
                        continue
                    if prob >= max_prob:
                        T1[i,j] = prob
                        max_prob = prob
                        T2[i,j] = k
                
        # Backward
        ind = np.argmax(T1[:, -1])  # index of link in final layer with max prob
        route[-1] = links[-1,ind]['linkPVID']
        for j in range(df.shape[0]-1, 0, -1):
            ind = T2[ind, j]
            route[j-1] = links[j-1, ind]['linkPVID']
        v_route[int(sample)] = route

    return v_route

    
if __name__ == "__main__":
    probe_path = 'data/new_probe_data.csv'
    link_path = 'data/new_link_data.csv'

    df_probe = pd.read_csv(probe_path)
    df_link = pd.read_csv(link_path)

    # Mapmatching
    routes = viterbi_new(df_probe, df_link)

    # Write to json
    with open('data/routes.txt', 'w') as file:
        file.write(json.dumps(routes))
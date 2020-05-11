import numpy as np
import pandas as pd
from Prob_cal import *
from tqdm import tqdm
import json
import heapq

def take_value(e):
    return e[1]


def find_near_links(probe, df_link, grouped_link):
    """find nearest links of a probe points within some threshold

    Arguments:
        probe {dataframe} -- a probe point
        df_link {dataframe} -- all link data

    Returns:
        list -- list of link dataframes found within threshold
    """

    num = 4  # choose nearest 4 links
    links = []

    # Calculate g_id of probe
    g_lat = int(float(probe['latitude'])/250)
    g_lon = int(float(probe['longitude'])/250)
    g_id = str(g_lat).zfill(5) + str(g_lon).zfill(5)

    # find links within the group
    cnt = 0
    while g_id not in grouped_link:
        if cnt > 5:
            cnt = 0
            break
        g_lat -= 1
        g_id = str(g_lat).zfill(5) + str(g_lon).zfill(5)
        cnt += 1
    while g_id not in grouped_link:
        g_lat += 1
        g_lon += 1
        g_id = str(g_lat).zfill(5) + str(g_lon).zfill(5)
        cnt += 1
    links_id = grouped_link[g_id]
    links_id = np.unique(np.array(links_id))
    h = []  # heap
    links = []
    for link in links_id:
        ind = df_link.loc[df_link['linkPVID'] == link].index.tolist()[0]
        heapq.heappush(h, (get_dist(probe, df_link.iloc[ind]), df_link.iloc[ind]))
    for i in range(4):
        if len(h) != 0:
            links.append(heapq.heappop(h)[1])
    return links


def viterbi_new(df_probe, df_link, grouped_link):
    """ Get the route (set of links in order) with the highest probability

    Arguments:
        df_probe {dataframe} -- all probe data
        df_link {dataframe} -- all link data

    Returns:
        v_route dictionary -- dic of links with highest prob for each sample {sampleID0: [linkPVID0, linkPVID1, ...], sampleID1: [linkPVID0, linkPVID1, ...], ...}
    """

    samples = df_probe['sampleID'].unique()
    v_route = {}
    cnt = 0

    for sample in tqdm(samples):            
        df = df_probe.loc[df_probe['sampleID'] == sample]  # df of probes of current sample
        df = df.sort_values(by=['dateTime'])
        T1 = np.zeros((4, df.shape[0]))
        T2 = np.zeros((4, df.shape[0]), dtype=int)
        links = np.empty((df.shape[0], 4), dtype=object)
        route = [None]*df.shape[0]

        # Initial
        links0 = find_near_links(df.iloc[0], df_link, grouped_link) # Need change return format
        links[0,:len(links0)] = links0
        for i in range(len(links0)):
            T1[i,0] = get_initial_prob(df.iloc[0], links0[i], df_link, grouped_link) * get_emission_prob(df.iloc[0], links0[i])

        # Forward
        for j in range(1, df.shape[0]):
            probe = df.iloc[j]  # current probe
            curr_links = find_near_links(probe, df_link, grouped_link)  # links of current probe
            links[j,:len(curr_links)] = curr_links
            for i in range(len(curr_links)):
                link = curr_links[i]
                max_prob = 0
                for k in range(4):  # iter prev links
                    if T1[k, j-1] != 0:
                        prob = T1[k,j-1] * get_transition_prob(link, links[j-1,k], df_link, grouped_link) * get_emission_prob(probe, link)
                    else:
                        continue
                    if prob >= max_prob:
                        T1[i,j] = prob
                        max_prob = prob
                        T2[i,j] = k
                
        # Backward
        ind = np.argmax(T1[:, -1])  # index of link in final layer with max prob
        route[-1] = int(links[-1,ind]['linkPVID'])
        for j in range(df.shape[0]-1, 0, -1):
            ind = T2[ind, j]
            route[j-1] = int(links[j-1, ind]['linkPVID'])
        v_route[int(sample)] = route

        if cnt % 10 == 0:
            # Write to json
            with open('data/routes.txt', 'w') as file:
                file.write(json.dumps(v_route))

        cnt += 1
        
    return v_route

    
if __name__ == "__main__":
    probe_path = 'data/new_probe_data.csv'
    link_path = 'data/new_link_data.csv'
    grouped_link_path = 'data/group_link_data.txt'

    df_probe = pd.read_csv(probe_path, skiprows=[i for i in range(1,15568)])
    df_link = pd.read_csv(link_path)
    with open(grouped_link_path, 'r') as openfile: 
        grouped_link = json.load(openfile) 

    # Mapmatching
    routes = viterbi_new(df_probe, df_link, grouped_link)
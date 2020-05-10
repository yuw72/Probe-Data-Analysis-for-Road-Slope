import pandas as pd
import numpy as np
import json


link_path = 'data/new_link_data.csv'
df_link = pd.read_csv(link_path)
dic = {}


for ind, link in df_link.iterrows():
    link_shape = link['shapeInfo'].split('|')
    for index in range(len(link_shape)):
        p = link_shape[index].split('/')
        g_lat = str(int(float(p[0])/200)).zfill(5)
        g_lon = str(int(float(p[1])/200)).zfill(5)
        g_id = g_lat + g_lon
        if g_id not in dic:
            dic[g_id] = [link['linkPVID']]
        else:
            dic[g_id].append(link['linkPVID'])

# Write to json
with open('data/group_link_data.txt', 'w') as file:
    file.write(json.dumps(dic))


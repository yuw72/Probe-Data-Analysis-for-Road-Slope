import pandas as pd
import numpy as np
import json


def point_to_line(p1, p2, p):
    x1, y1 = float(p1[0]), float(p1[1])
    x2, y2 = float(p2[0]), float(p2[1])
    x0, y0 = float(p[0]), float(p[1])

    a = y2 - y1
    b = -(x2 - x1)
    c = (x2 - x1) * y1 - (y2 - y1) * x1

    return np.abs(a * x0 + b * y0 + c) / np.sqrt(a ** 2 + b ** 2)


def get_dist(probe, link):  # calculate the closest distance from probe to a road
    lat, long = probe['latitude'], probe['longitude']
    link_shape = link['shapeInfo']

    link_shape = link_shape.split('|')

    min_dist = float('inf')

    for index in range(1, len(link_shape)):
        p1 = link_shape[index - 1].split('/')
        p2 = link_shape[index].split('/')

        dist = point_to_line(p1, p2, (lat, long))
        # print(f'dist is {dist}')
        if dist < min_dist:
            min_dist = dist

    return min_dist


def get_initial_prob(probe, link, df_link, grouped_link):
    """Get initial state probability of the link given the first probe

    Arguments:
        probe {dataframe} -- the first probe data of a route
        link {dataframe} -- the link we are calculate probability
        df_link {dataframe} -- all link data

    Returns:
        link_prob float -- probability P(link)
    """

    g_lat = int(float(probe['latitude'])/250)
    g_lon = int(float(probe['longitude'])/250)
    g_id = str(g_lat).zfill(5) + str(g_lon).zfill(5)
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

    distance = []
    links_id = grouped_link[g_id]
    links_id = np.unique(np.array(links_id))
    denominator = len(links_id)

    return 1 / denominator


def get_emission_prob(probe, link):
    """calculate emission probability of a probe given a link. P(probe | link)

    Arguments:
        probe {dataframe} -- one probe point
        link {dataframe} -- one link

    Returns:
        prob float -- P(probe | link)
    """

    # variance parameters (empirically choosen) CHANGE IF YOU WANT!
    v_phi = 1  # radian angle
    v_b = 40  # meters

    # calculate the heading of the link and b
    b = get_dist(probe, link)

    link_shape = link['shapeInfo'].split('|')
    p = (probe['latitude'], probe['longitude'])

    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0

    for index in range(1, len(link_shape)):
        p1 = link_shape[index - 1].split('/')
        p2 = link_shape[index].split('/')

        dist = point_to_line(p1, p2, p)
        if dist == b:
            x1, y1 = float(p1[0]), float(p1[1])
            x2, y2 = float(p2[0]), float(p2[1])

            break

    angle = np.arctan2(x2 - x1, y2 - y1)  # * 180 / np.pi  # in radian
    if angle < 0:
        angle += 2 * np.pi

    # cal delta heading
    delta_heading = probe['heading'] / 180 * np.pi - angle  # in radian

    # calculate normal distributions
    p_b = 1 / (np.sqrt(2 * np.pi) * v_b) * np.exp(-0.5 * (b / v_b) ** 2)
    p_phi = 1 / (np.sqrt(2 * np.pi) * v_phi) * np.exp(-0.5 * (delta_heading / v_phi) ** 2)

    return p_b * p_phi


def get_transition_prob(link1, link2, df_link, grouped_link):
    """calculate transition probability of a probe going from link1 to link2. P(link2 | link1) or P(link1 -> link2)

    Arguments:
        link1 {dataframe} -- from the link1
        link2 {dataframe} -- from the link2
        df_link {dataframe} -- set of all links data

    Returns:
        prob float -- probability P(link1 -> link2)
    """

    ID = None

    if link1['refNodeID'] == link2['refNodeID']:
        ID = link1['refNodeID']
    elif link1['refNodeID'] == link2['nrefNodeID']:
        ID = link1['refNodeID']
    elif link1['nrefNodeID'] == link2['refNodeID']:
        ID = link1['nrefNodeID']
    elif link1['nrefNodeID'] == link2['nrefNodeID']:
        ID = link1['nrefNodeID']

    # (1) link1 and link2 are not connected
    if ID is None:
        return 0
    # (2) Connected
    else:
        k = 0
        link_shape = link1['shapeInfo']
        link_shape = link_shape.split('|')
        p = link_shape[0].split('/')

        g_lat = int(float(p[0])/250)
        g_lon = int(float(p[1])/250)
        g_id = str(g_lat).zfill(5) + str(g_lon).zfill(5)
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
        

        links_id = grouped_link[g_id]
        links_id = np.unique(np.array(links_id))

        for link in links_id:
            ind = df_link.loc[df_link['linkPVID'] == link].index.tolist()[0]
            rows = df_link.iloc[ind]
            # if rows['refNodeID'] not in grouped_link or rows['nrefNodeID'] not in grouped_link:
            #     continue
            if rows['refNodeID'] == ID or rows['nrefNodeID'] == ID:
                k += 1

        return 1 / k
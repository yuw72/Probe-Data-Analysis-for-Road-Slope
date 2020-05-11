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


def get_group(probe_id, df_link):
    grouped_link_path = '../data/group_link_data.txt'
    # print(probe_id)
    with open(grouped_link_path, 'r') as openfile:
        grouped_link = json.load(openfile)
        return grouped_link[probe_id]


def get_initial_prob(probe, link, df_link):
    """Get initial state probability of the link given the first probe

    Arguments:
        probe {dataframe} -- the first probe data of a route
        link {dataframe} -- the link we are calculate probability
        df_link {dataframe} -- all link data

    Returns:
        link_prob float -- probability P(link)
    """

    # threshold of distance (meters)
    # threshold = 200
    # num_roads = 10

    grouped_link_path = 'data/group_link_data.txt'

    lat, long = probe['latitude'], probe['longitude']
    g_lat = str(int(float(lat) / 200)).zfill(5)
    g_lon = str(int(float(long) / 200)).zfill(5)
    probe_id = g_lat + g_lon

    group_id = get_group(probe_id, df_link)

    denominator = 0
    # find all links in the threshold

    numerator = 1 / get_dist(probe, link)

    distance = []
    for index, rows in df_link.iterrows():
        if rows['linkPVID'] in group_id:
            distance.append(get_dist(probe, rows))

    # mean = np.mean(distance)
    # std = np.std(distance)

    threshold = min(distance) + 200
    # distance.sort()

    # while distance[0] > threshold:
    #     threshold += 100

    for d in distance:
        if d < threshold:
            denominator += 1 / d

    return numerator / denominator

    # while True:
    #     for index, rows in df_link.iterrows():
    #         dist = get_dist(probe, rows)
    #         if dist < threshold:
    #             denominator += 1 / dist
    #     if denominator != 0:
    #         return numerator / denominator
    #     else:
    #         threshold += 100

    # calculate prob for all links = (1/dis(probe, link))/sum(1/dis(probe, links))

    # return links_prob


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

    # calculate the heading of the link
    # cal b
    b = get_dist(probe, link)
    # print(f'dist from probe to link is {b}')

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
    # x1, y1 = float(p1[0]), float(p1[1])
    # x2, y2 = float(p2[0]), float(p2[1])

    # print(f'p1 coord is {x1}, {y1}')
    # print(f'p2 coord is {x2}, {y2}')
    # print(f'delta is {x2-x1}, {y2-y1}')

    angle = np.arctan2(x2 - x1, y2 - y1)  # * 180 / np.pi  # in radian
    if angle < 0:
        angle += 2 * np.pi
    # print(f'angle is {angle}')

    # cal delta heading
    # print('probe heading is', {probe['heading'] / 180 * np.pi})
    delta_heading = probe['heading'] / 180 * np.pi - angle  # in radian
    # print(f'delta heading is {delta_heading}')

    # calculate normal distributions

    p_b = 1 / (np.sqrt(2 * np.pi) * v_b) * np.exp(-0.5 * (b / v_b) ** 2)
    p_phi = 1 / (np.sqrt(2 * np.pi) * v_phi) * np.exp(-0.5 * (delta_heading / v_phi) ** 2)

    # print(f'prob by dist is {p_b}')
    # print(f'prob by angle is {p_phi}')
    # return prob
    return p_b * p_phi


def get_transition_prob(link1, link2, df_link):
    """calculate transition probability of a probe going from link1 to link2. P(link2 | link1) or P(link1 -> link2)

    Arguments:
        link1 {dataframe} -- from the link1
        link2 {dataframe} -- from the link2
        df_link {dataframe} -- set of all links data

    Returns:
        porb float -- probability P(link1 -> link2)
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

    # (1) link1 and link2 are connected
    # if link1['refNodeID'] == link2['refNodeID'] or link1['refNodeID'] == link2['nrefNodeID'] or link1['nrefNodeID'] == \
    #         link2['refNodeID'] or link1['nrefNodeID'] == link2['nrefNodeID']:
    #     k = 0
    #
    #     for index, rows in df_link.iterrows():
    #
    #         if rows['refNodeID'] == link1['refNodeID'] or rows['refNodeID'] == link2['refNodeID'] or rows[
    #             'refNodeID'] == link1['nrefNodeID'] or rows['refNodeID'] == link2['nrefNodeID'] or rows['nrefNodeID'] == \
    #                 link1['refNodeID'] or rows['nrefNodeID'] == link2['refNodeID'] or rows['nrefNodeID'] == link1[
    #             'nrefNodeID'] or rows['nrefNodeID'] == link2['nrefNodeID']:
    #             k += 1
    #
    #     return 1 / k
    # Compute number of links at this intersection
    # prob = 1/k

    # (2) Not connected
    if ID is None:
        return 0

    else:
        k = 0

        for index, rows in df_link.iterrows():
            if rows['refNodeID'] == ID or rows['nrefNodeID'] == ID:
                k+=1

        return 1/k
    # return prob


if __name__ == '__main__':
    probe_path = '../data/new_probe_data.csv'
    link_path = '../data/new_link_data.csv'

    df_probe = pd.read_csv(probe_path, engine='python', nrows=100)
    df_link = pd.read_csv(link_path, engine='python', nrows=100)

    df_probe.columns = ['sampleID', 'dataTime', 'sourceCode', 'latitude', 'longitude', 'altitude', 'speed', 'heading']
    df_link.columns = ['linkPVID', 'refNodeID', 'nrefNodeID', 'length', 'functionalClass', 'directionofTravel',
                       'speedCategory', 'fromRefSpeedLimit',
                       'toRedSpeedLimit', 'fromRefNumLanes', 'toRefNumLanes', 'multiDigitized', 'urban', 'timeZone',
                       'shapeInfo', 'curvatureInfo', 'slopeInfo']

    # get_dist(df_probe.iloc[0], df_link.iloc[0])

    # get_initial_prob(df_probe.iloc[0], df_link.iloc[0], df_link)
    # get_group(123, df_link)
    idx = np.random.randint(0, 100, 2)
    p = get_initial_prob(df_probe.iloc[idx[0]], df_link.iloc[idx[1]], df_link)

    # print(f'index is {idx}')
    # get_dist(df_probe.iloc[idx[0]], df_link.iloc[idx[1]])

    # print('coordinate of probe is ', df_probe['latitude'], df_probe['longitude'])

    # e_prob = get_emission_prob(df_probe.iloc[idx[0]], df_link.iloc[idx[1]])
    # print(f'emission probability = {e_prob}')

    # p = get_transition_prob(df_link.iloc[0], df_link.iloc[0], df_link)

    # for index, rows in df_probe.iterrows():
    #     rows = np.array(rows)
    #
    #     print(rows[3:5])
    #     break
    #
    # for index, rows in df_link.iterrows():
    #     rows = np.array(rows)
    #     print(rows[14])
    #     print(type(rows[14]))
    #     break

import pandas as pd
import numpy as np


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

        if dist < min_dist:
            min_dist = dist

    return min_dist


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
    threshold = 200
    denominator = 0
    # find all links in the threshold

    numerator = 1 / get_dist(probe, link)

    for index, rows in df_link.iterrows():
        dist = get_dist(probe, rows)
        if dist < threshold:
            denominator += 1 / dist

    return numerator / denominator

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
    v_b = 4  # meters

    # calculate the heading of the link
    # cal b
    b = get_dist(probe, link)

    link_shape = link['shapeInfo'].split('|')
    p = (probe['latitude'], probe['longitude'])

    for index in range(1, len(link_shape)):
        p1 = link_shape[index - 1].split('/')
        p2 = link_shape[index].split('/')

        dist = point_to_line(p1, p2, p)
        if dist == b:
            break
    x1, y1 = float(p1[0]), float(p1[1])
    x2, y2 = float(p2[0]), float(p2[1])

    angle = np.arctan2(x2 - x1, y2 - y1)  # * 180 / np.pi in radian

    # cal delta heading

    delta_heading = probe['heading'] / 180 * np.pi - angle  # in radian

    # calculate normal distributions

    p_b = 1 / (np.sqrt(2 * np.pi) * v_b) * np.exp(-0.5 * (b / v_b) ** 2)
    p_phi = 1 / (np.sqrt(2 * np.pi) * v_phi) * np.exp(-0.5 * (delta_heading / v_phi) ** 2)
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

    # (1) link1 and link2 are connected
    if link1['refNodeID'] == link2['refNodeID'] or link1['refNodeID'] == link2['nrefNodeID'] or link1['nrefNodeID'] == \
            link2['refNodeID'] or link1['nrefNodeID'] == link2['nrefNodeID']:
        k = 0

        for index, rows in df_link.iterrows():
            if rows['refNodeID'] == link1['refNodeID'] or rows['refNodeID'] == link2['refNodeID'] or rows[
                'refNodeID'] == link1['nrefNodeID'] or rows['refNodeID'] == link2['nrefNodeID'] or rows['nrefNodeID'] == \
                    link1['refNodeID'] or rows['nrefNodeID'] == link2['refNodeID'] or rows['nrefNodeID'] == link1[
                'nrefNodeID'] or rows['nrefNodeID'] == link2['nrefNodeID']:
                k += 1

        return 1 / k
        # Compute number of links at this intersection
        # prob = 1/k

    # (2) Not connected
    else:
        return 0

    # return prob


if __name__ == '__main__':
    probe_path = '../data/Partition6467ProbePoints.csv'
    link_path = '../data/Partition6467LinkData.csv'

    df_probe = pd.read_csv(probe_path, engine='python', nrows=100)
    df_link = pd.read_csv(link_path, engine='python', nrows=100)

    df_probe.columns = ['sampleID', 'dataTime', 'sourceCode', 'latitude', 'longitude', 'altitude', 'speed', 'heading']
    df_link.columns = ['linkPVID', 'refNodeID', 'nrefNodeID', 'length', 'functionalClass', 'directionofTravel',
                       'speedCategory', 'fromRefSpeedLimit',
                       'toRedSpeedLimit', 'fromRefNumLanes', 'toRefNumLanes', 'multiDigitized', 'urban', 'timeZone',
                       'shapeInfo', 'curvatureInfo', 'slopeInfo']

    # get_dist(df_probe.iloc[0], df_link.iloc[0])

    # get_initial_prob(df_probe.iloc[0], df_link.iloc[0], df_link)

    # get_emission_prob(df_probe.iloc[0], df_link.iloc[0])

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

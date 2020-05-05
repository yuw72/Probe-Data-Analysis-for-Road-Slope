import pandas as pd
import numpy as np


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
    threshold = 4

    # find all links in the threshold

    # calculate prob for all links = (1/dis(probe, link))/sum(1/dis(probe, links))

    return links_prob


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

    # cal delta heading
    
    # cal b
    
    # calculate normal distributions

    return prob

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
    if (link1['refNodeID' == link2['refNodeID'] or link1['refNodeID' == link2['nrefNodeID'] or link1['nrefNodeID' == link2['refNodeID'] or link1['nrefNodeID' == link2['nrefNodeID']):
        # Compute number of links at this intersection
        # prob = 1/k

    # (2) Not connected
    prob = 0

    return prob

    
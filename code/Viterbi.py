from Prob_cal import *
from Slope_cal import *

def find_near_links(probe, df_link):
    """find nearest links of a probe points within some threshold

    Arguments:
        probe {dataframe} -- a probe point
        df_link {dataframe} -- all link data

    Returns:
        list -- list of links found within threshold
    """

    links = []
    # TODO

    return links


def gen_routes(df_probe, df_link):
    """ generate sets of possible routes (each contains a set of connected, ordered links) of current sample.  
        Each of n probe points are mapped to a link. Links can be the same. Output links number should match probe number.

    Arguments:
        df_probe {dataframe} -- probe points of this sample (so same sampleID)
        df_link {dataframe} -- all links

    Returns:
        routes list/array -- list of possible routes [[linkPVID0, linkPVID1, linkPVID2, ...], [linkPVID0, linkPVID1, linkPVID2, ...]]
    """

    routes = []

    # TODO

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
        routes = gen_routes(df, df_link)  # set of possible routes for this sample
        max_prob = 0
        
        for route in routes:
            # P(link0)
            df = df.sort_values(by=['dateTime'])
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

    df_probe, df_link = pd.read_csv(probe_path, link_path)

    routes = viterbi(df_probe, df_link)

    # calculate slope
    slopes = get_slope(routes, df_link)

    # calculate error
    err = cal_error(slopes, df_link)
"""
This is an automatically generated script by ABrox GUI.
Created on 2017-10-16 10:57:28.251604.
"""

# Required imports
import numpy as np
from scipy import stats
from abrox.core.algorithm import Abc


def summary(data):
    return data.flatten()


def simulate_PDG(params):
    C_priv = params['C_priv']
    C_pub = params['C_pub']

    A_priv_wh_m = params['A_priv_wh_m']
    A_pub_wh_m = params['A_pub_wh_m']

    A_priv_wh_f = params['A_priv_wh_f']
    A_pub_wh_f = params['A_pub_wh_f']

    A_priv_bl_m = params['A_priv_bl_m']
    A_pub_bl_m = params['A_pub_bl_m']

    A_priv_bl_f = params['A_priv_bl_f']
    A_pub_bl_f = params['A_pub_bl_f']

    G = params['G']

    # PRIVATE condition

    probs = {"private":
                 {"WT" : {"m" : None, "f": None},
                  "WG":  {"m": None, "f": None},
                  "BT":  {"m": None, "f": None},
                  "BG":  {"m": None, "f": None}},
             "public":
                 {"WT": {"m": None, "f": None},
                  "WG": {"m": None, "f": None},
                  "BT": {"m": None, "f": None},
                  "BG": {"m": None, "f": None}}
             }

    # probability to say tool after white prime
    probs['private']['WT']['m'] = C_priv + (1-C_priv) * A_priv_wh_m + (1-C_priv)*(1-A_priv_wh_m)*G
    probs['private']['WT']['f'] = C_priv + (1-C_priv) * A_priv_wh_f + (1-C_priv)*(1-A_priv_wh_f)*G

    # probability to say gun after white prime
    probs['private']['WG']['m'] = C_priv + (1-C_priv)*(1-A_priv_wh_m)*(1-G)
    probs['private']['WG']['f'] = C_priv + (1 - C_priv) * (1 - A_priv_wh_f) * (1 - G)

    # probability to say tool after black prime
    probs['private']['BT']['m'] = C_priv + (1-C_priv)*(1-A_priv_bl_m)*G
    probs['private']['BT']['f'] = C_priv + (1 - C_priv) * (1 - A_priv_bl_f) * G

    # probability to say gun after black prime
    probs['private']['BG']['m'] = C_priv + (1-C_priv)*A_priv_bl_m + (1-C_priv)*(1-A_priv_bl_m)*(1-G)
    probs['private']['BG']['f'] = C_priv + (1 - C_priv) * A_priv_bl_f + (1 - C_priv) * (1 - A_priv_bl_f) * (1 - G)

    # PUBLIC condition

    # probability to say tool after white prime
    probs['public']['WT']['m'] = C_pub + (1-C_pub) * A_pub_wh_m + (1-C_pub)*(1-A_pub_wh_m)*G
    probs['public']['WT']['f'] = C_pub + (1-C_pub) * A_pub_wh_f + (1-C_pub)*(1-A_pub_wh_f)*G

    # probabilit to say gun after white prime
    probs['public']['WG']['m'] = C_pub + (1 - C_pub) * (1 - A_pub_wh_m) * (1 - G)
    probs['public']['WG']['f'] = C_pub + (1 - C_pub) * (1 - A_pub_wh_f) * (1 - G)

    # probability to say tool after black prime
    probs['public']['BT']['m'] = C_pub + (1 - C_pub) * (1 - A_pub_bl_m) * G
    probs['public']['BT']['f'] = C_pub + (1 - C_pub) * (1 - A_pub_bl_f) * G

    # probability to say gun after black prime
    probs['public']['BG']['m'] = C_pub + (1 - C_pub) * A_pub_bl_m + (1 - C_pub) * (1 - A_pub_bl_m) * (1 - G)
    probs['public']['BG']['f'] = C_pub + (1 - C_pub) * A_pub_bl_f + (1 - C_pub) * (1 - A_pub_bl_f) * (1 - G)


    N_pub = 65
    N_priv = 62
    trials = 384 // 8

    results = {"private":
                   {"WT": {'m': 0, 'f': 0},
                    "WG": {'m': 0, 'f': 0},
                    "BT": {'m': 0, 'f': 0},
                    "BG": {'m': 0, 'f': 0}},
               "public":
                   {"WT": {'m': 0, 'f': 0},
                    "WG": {'m': 0, 'f': 0},
                    "BT": {'m': 0, 'f': 0},
                    "BG": {'m': 0, 'f': 0}}
               }

    contexts = ['private', 'public']
    combination = ['WT','WG','BT','BG']
    gender = ['m','f']
    sample_size = [N_priv, N_pub]

    # simulate_PDG_PDG

    for context in np.repeat(contexts, [N_priv, N_pub]):

        for comb in combination:
            for sex in gender:
                results[context][comb][sex] += np.sum(np.random.uniform(0, 1, trials) < probs[context][comb][sex])

    # divide by N

    for i, context in enumerate(contexts):
        for comb in combination:
            for sex in gender:
                results[context][comb][sex] /= sample_size[i]

    out = np.empty(shape=(8, 2))
    
    for i, context in enumerate(contexts):
        for j, sex in enumerate(gender):
            for k, comb in enumerate(combination):
                out[k + (j*4), i] = results[context][comb][sex]

    return out


def simulate_SG(params):
    C_priv = params['C_priv']
    C_pub = params['C_pub']

    A_priv_wh_m = params['A_priv_wh_m']
    A_pub_wh_m = params['A_pub_wh_m']

    A_priv_wh_f = params['A_priv_wh_f']
    A_pub_wh_f = params['A_pub_wh_f']

    A_priv_bl_m = params['A_priv_bl_m']
    A_pub_bl_m = params['A_pub_bl_m']

    A_priv_bl_f = params['A_priv_bl_f']
    A_pub_bl_f = params['A_pub_bl_f']

    G = params['G']

    # PRIVATE condition

    probs = {"private":
                 {"WT": {"m": None, "f": None},
                  "WG": {"m": None, "f": None},
                  "BT": {"m": None, "f": None},
                  "BG": {"m": None, "f": None}},
             "public":
                 {"WT": {"m": None, "f": None},
                  "WG": {"m": None, "f": None},
                  "BT": {"m": None, "f": None},
                  "BG": {"m": None, "f": None}}
             }

    # probability to say tool after white prime
    probs['private']['WT']['m'] = A_priv_wh_m + (1 - A_priv_wh_m) * C_priv + (1-A_priv_wh_m)*(1-C_priv)*G
    probs['private']['WT']['f'] = A_priv_wh_f + (1 - A_priv_wh_f) * C_priv + (1-A_priv_wh_f)*(1-C_priv)*G

    # probability to say gun after white prime
    probs['private']['WG']['m'] = (1-A_priv_wh_m) * C_priv + (1-A_priv_wh_m)*(1-C_priv)*(1-G)
    probs['private']['WG']['f'] = (1-A_priv_wh_f) * C_priv + (1-A_priv_wh_f)*(1-C_priv)*(1-G)

    # probability to say tool after black prime
    probs['private']['BT']['m'] = (1-A_priv_bl_m) * C_priv + (1-A_priv_bl_m)*(1-C_priv)*G
    probs['private']['BT']['f'] = (1-A_priv_bl_f) * C_priv + (1-A_priv_bl_f)*(1-C_priv)*G

    # probability to say gun after black prime
    probs['private']['BG']['m'] = A_priv_bl_m + (1-A_priv_bl_m)*C_priv + (1-A_priv_bl_m)*(1-C_priv)*(1-G)
    probs['private']['BG']['f'] = A_priv_bl_f + (1-A_priv_bl_f)*C_priv + (1-A_priv_bl_f)*(1-C_priv)*(1-G)

    # PUBLIC condition

    # probability to say tool after white prime
    probs['public']['WT']['m'] = A_pub_wh_m + (1 - A_pub_wh_m) * C_pub + (1 - A_pub_wh_m) * (1 - C_pub) * G
    probs['public']['WT']['f'] = A_pub_wh_f + (1 - A_pub_wh_f) * C_pub + (1 - A_pub_wh_f) * (1 - C_pub) * G

    # probability to say gun after white prime
    probs['public']['WG']['m'] = (1 - A_pub_wh_m) * C_pub + (1-A_pub_wh_m)*(1-C_pub) * (1 - G)
    probs['public']['WG']['f'] = (1 - A_pub_wh_f) * C_pub + (1-A_pub_wh_f)*(1-C_pub) * (1 - G)

    # probability to say tool after black prime
    probs['public']['BT']['m'] = (1 - A_pub_bl_m) * C_pub + (1 - A_pub_bl_m) * (1 - C_pub) * G
    probs['public']['BT']['f'] = (1 - A_pub_bl_f) * C_pub + (1 - A_pub_bl_f) * (1 - C_pub) * G

    # probability to say gun after black prime
    probs['public']['BG']['m'] = A_pub_bl_m + (1 - A_pub_bl_m) * C_pub + (1 - A_pub_bl_m) * (1 - C_pub) * (1 - G)
    probs['public']['BG']['f'] = A_pub_bl_f + (1 - A_pub_bl_f) * C_pub + (1 - A_pub_bl_f) * (1 - C_pub) * (1 - G)



    N_pub = 65
    N_priv = 62
    trials = 384 // 8

    results = {"private":
                   {"WT": {'m' : 0, 'f' : 0 },
                    "WG": {'m' : 0, 'f' : 0 },
                    "BT": {'m' : 0, 'f' : 0 },
                    "BG": {'m' : 0, 'f' : 0 }},
               "public":
                   {"WT": {'m': 0, 'f': 0},
                    "WG": {'m': 0, 'f': 0},
                    "BT": {'m': 0, 'f': 0},
                    "BG": {'m': 0, 'f': 0}}
               }

    contexts = ['private', 'public']
    combination = ['WT','WG','BT','BG']
    gender = ['m','f']
    sample_size = [N_priv, N_pub]

    # simulate_SG_SG

    for context in np.repeat(contexts, [N_priv, N_pub]):

        for comb in combination:
            for sex in gender:
                results[context][comb][sex] += np.sum(np.random.uniform(0, 1, trials) < probs[context][comb][sex])

    # divide by N

    for i, context in enumerate(contexts):
        for comb in combination:
            for sex in gender:
                results[context][comb][sex] /= sample_size[i]

    out = np.empty(shape=(8, 2))
    
    for i, context in enumerate(contexts):
        for j, sex in enumerate(gender):
            for k, comb in enumerate(combination):
                out[k + (j*4), i] = results[context][comb][sex]

    return out


CONFIG = {
    "data": {
        "datafile": "None",
        "delimiter": "None"
    },
    "models": [
        {
        "name": "PDG",
        "priors": [
            {"C_priv": stats.beta(a=3.0, b=3.0, loc=0.0)},
            {"C_pub": stats.beta(a=3.0, b=3.0, loc=0.0)},
            {"A_priv_wh_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_wh_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_priv_wh_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_wh_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_priv_bl_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_bl_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_priv_bl_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_bl_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"G": stats.beta(a=10.0, b=10.0, loc=0.0)},
        ],
        "simulate": simulate_PDG
        },
        {
        "name": "SG",
        "priors": [
            {"C_priv": stats.beta(a=3.0, b=3.0, loc=0.0)},
            {"C_pub": stats.beta(a=3.0, b=3.0, loc=0.0)},
            {"A_priv_wh_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_wh_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_priv_wh_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_wh_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_priv_bl_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_bl_m": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_priv_bl_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"A_pub_bl_f": stats.beta(a=2.0, b=10.0, loc=0.0)},
            {"G": stats.beta(a=10.0, b=10.0, loc=0.0)},
        ],
        "simulate": simulate_SG
        },
    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
         'fixedparameters': {'A_priv_bl_f': 0.28,
                             'A_priv_bl_m': 0.19,
                             'A_priv_wh_f': 0.23,
                             'A_priv_wh_m': 0.12,
                             'A_pub_bl_f': 0.35,
                             'A_pub_bl_m': 0.27,
                             'A_pub_wh_f': 0.15,
                             'A_pub_wh_m': 0.2,
                             'C_priv': 0.5,
                             'C_pub': 0.5,
                             'G': 0.5},
         'method': 'rejection',
         'modeltest': 1,
         'objective': 'comparison',
         'outputdir': '/Users/ulf.mertens/Seafile/Uni/approxbayes/abrox/project_files/mptree/analysis',
         'percentile': 0.01,
         'simulations': 10000.0,
         'threshold': -1
    }
}


if __name__ == "__main__":
    # Create and run an Abc instance
    abc = Abc(config=CONFIG)
    abc.run()

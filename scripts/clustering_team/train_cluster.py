""" TODO:
    - obsluga knn (kdt potrzebne, bo nigdy sie nie doliczy)
    - przejscie na sklearna, bo tam pewnie to wszystko jest
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import sys
import argparse
import glob, os
import pickle

ALLOWED_ALGOS = ["Kmeans","GaussianMixture"]
SUBSETS = ["train", "validate"]
INFI = 2000000000

def ParseArguments():
    parser = argparse.ArgumentParser(description="Project ")
    parser.add_argument('--features-dir',
                            default = "features/cats_dogs/sifts/",
                            required = False,
                            help = 'data set directory name (features/cats_dogs/sifts/)')
    parser.add_argument('--algorithm',
                            default = "kmeans",
                            required = False,
                            help='clustering alg. One of [kmeans] (def. kmeans)')
    parser.add_argument('--k',
                            default = 100,
                            required = False,
                            help = "depends on used algorithm. In k-means it's number of centers")
    parser.add_argument('--knn',
                            default = 0,
                            required = False,
                            help = "number of nearest neighbours in KNN. If 0, then we take the closest center")


    args = parser.parse_args()

    return args.features_dir, args.algorithm, int(args.k), int(args.knn)

def load_class_features(class_path):
    pickle_path = class_path + "/feats.pickle"

    try:
        feats_file = open(pickle_path, 'rb')
    except:
        print("Couldn't open {}.".format(pickle_path))
        exit(5)

    feats_per_utt = pickle.load(feats_file)

    return feats_per_utt


"""
    Main part
"""

# Process args

feats_dir, algorithm, k_par, knn  =  ParseArguments()

if algorithm not in ALLOWED_ALGOS:
    print("Algorithm {} not allowed. Try one of {}".format(algorithm, ALLOWED_ALGOS))
    exit(2)

# Load all features

try:
    feats_path = feats_dir + "sifts_all.pickle"
    feats_file = open(feats_path, "rb")
except:
    print("Couldn't open features file: {}.".format(feats_path))
    exit(3)

all_feats = pickle.load(feats_file)
feats_file.close()

# Train and save cluster

cluster = None
params_str = ""

if algorithm == "Kmeans":
    object = KMeans(k_par) # numpy's k-means requires it
    object.fit(all_feats)
    params_str += str(k_par)
	
if algorithm == "GaussianMixture":
    object = GaussianMixture(k_par) # numpy's gmm's requires it
    object.fit(all_feats)
    params_str += str(k_par)


cluster_path = "dict/" + "/".join(feats_dir.split("/")[1:3]) + "/" + algorithm + params_str + "/"
	
	

if not os.path.exists(cluster_path):
       os.makedirs(cluster_path)


# Load features per utterance (image)

for subs in SUBSETS:
    all_classess = glob.glob(feats_dir + "/" + subs + "/*")

    for class_path in all_classess:
        feats_per_utt = load_class_features(class_path)

        for utt in feats_per_utt.keys():
            utt_splt = list(filter(None, utt.split("/"))) # remove empty strings (coz of ///// in paths)
            no_ext = ".".join(utt_splt[-1].split(".")[:-1])
            utt_path = cluster_path + "/knn" + str(knn) + "/" + "/".join(utt_splt[2:-1]) + "/"

            if not os.path.exists(utt_path):
                os.makedirs(utt_path)

            out_clustered = open(utt_path + no_ext + ".txt", 'w')

            hist = [0] * k_par

            for feat in feats_per_utt[utt]:
                hist[object.predict([feat])] += 1

            for i in range(k_par):
                out_clustered.write(str(hist[i]) + '\n')

            out_clustered.close()

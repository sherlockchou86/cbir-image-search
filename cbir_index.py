
# (1) create index for image source, support 3 types of image hash, region-based color histogram feature
# (2) create index-tree(VP-Tree) for quick search operation
# (3) do search operation

import os
from PIL import Image
import numpy as np
import json
import pickle
import vptree
import time
import cv2
import cbir_paths
import cbir_hash
import cbir_ch_feature

image_source_path = "./static/image_sources"

# hash names
hash_names = ["ahash", "phash", "dhash"]
# hash maps serialized files
hash_map_files = ["pickles/ahash.pickle", "pickles/phash.pickle", "pickles/dhash.pickle"]
# hash vptree serialized files
hash_vptree_files = ["pickles/a_vptree.pickle", "pickles/p_vptree.pickle", "pickles/d_vptree.pickle"]
# loaded hash maps and vptrees
hash_maps = []
vptrees = []

color_histogram_feature_map_file = "pickles/ch_feature.pickle"
color_histogram_feature_vptree_file = "pickles/ch_feature_vptree.pickle"

color_histogram_feature_map = []
color_histogram_feature_vptree = []

# create image index if not created
# load image index from disk
def init_index():
    if (not os.path.exists(hash_map_files[0])) or (not os.path.exists(hash_vptree_files[0])):
        create_hash_index(0)
    if (not os.path.exists(hash_map_files[1])) or (not os.path.exists(hash_vptree_files[1])):
        create_hash_index(1)
    if (not os.path.exists(hash_map_files[2])) or (not os.path.exists(hash_vptree_files[2])):
        create_hash_index(2)
    
    if (not os.path.exists(color_histogram_feature_map_file)) or (not os.path.exists(color_histogram_feature_vptree_file)):
        create_color_histogram_index()

    print("[INFO] loading VP-Tree and hashes...")
    for (i, name) in enumerate(hash_names):
        hash_maps.append(pickle.loads(open(hash_map_files[i], "rb").read()))
        vptrees.append(pickle.loads(open(hash_vptree_files[i], "rb").read()))
    
    print("[INFO] loading VP-Tree and features...")
    color_histogram_feature_map.append(pickle.loads(open(color_histogram_feature_map_file, 'rb').read()))
    color_histogram_feature_vptree.append(pickle.loads(open(color_histogram_feature_vptree_file, 'rb').read()))


# perform the hash-based search accordding to some config, return json string
# query_image:  image uploaded by user, PIL Image
# max_distance: hamming distance threshold
# hash_type:    3 types of hash supported which user could choose
def hash_search(query_image, max_distance, hash_type):
    # calculate hash for query image
    print("[INFO] calculating {} for query image...".format(hash_names[hash_type]))
    query_hash = None
    if hash_type == 0:
        query_hash = cbir_hash.average_hash(query_image)
    elif hash_type == 1:
        query_hash = cbir_hash.phash(query_image)
    else:
        query_hash = cbir_hash.dhash(query_image)
    print("[INFO] query image hash:{}".format(query_hash))

    # perform the search
    print("[INFO] performing search...")
    start = time.time()
    results = vptrees[hash_type].get_all_in_range(query_hash, max_distance)
    results = sorted(results)
    end = time.time()
    print("[INFO] search took {} seconds".format(end - start))
    
    # generate json result
    print("[INFO] generating json...")
    result_map = {}
    result_map["query_hash_type"] = hash_names[hash_type]
    result_map["query_image_hash"] = str(query_hash)
    result_map["max_distance"] = max_distance
    result_map["similar_images_count"] = len(results)
    result_map["similar_images"] = []

    for (d, h) in results:
        # grab all image paths in hash map with the same hash
        resultPaths = hash_maps[hash_type].get(h, [])
        print("[INFO] {} total image(s) with d: {}, h: {}".format(len(resultPaths), d, h))
        # loop over the result paths
        for resultPath in resultPaths:
            img_map = {}
            img_map["image_url"] = resultPath.replace("./", "").replace("\\", "/")  ## convert
            img_map["image_hash"] = str(h)
            img_map["distance_with_query"] = d
            result_map["similar_images"].append(img_map)

    result_map["similar_images_count"] = len(result_map["similar_images"])
    # serialize map to json
    print(result_map)
    json_result = json.dumps(result_map, sort_keys=True, indent=4)
    return json_result
            
# perform the color histogram search accordding to some config, return json string
# query_image:  image uploaded by user, OpenCV Image
# limit      :  max record count returned by algorithm
def color_histogram_search(query_image, limit):
    # calculate color histogram feature fro query image
    print("[INFO] calculating color histogram feature for query image...")
    query_feature = cbir_ch_feature.describe(query_image)

    print("[INFO] query image color histogram feature:{}".format(query_feature))

    # perform the search
    print("[INFO] performing search...")
    start = time.time()
    results = color_histogram_feature_vptree[0].get_n_nearest_neighbors(query_feature, limit)
    results = sorted(results)
    end = time.time()
    print("[INFO] search took {} seconds".format(end - start))

    # generate json result
    print("[INFO] generating json...")
    result_map = {}
    # feature vector is too large to transfer, ignore it
    # result_map["query_image_feature"] = query_feature
    result_map["limit"] = limit
    result_map["similar_images_count"] = len(results)
    result_map["similar_images"] = []

    for (d, f) in results:
        # grab all image paths in feature map with the same feature
        str_f = str(list(f))
        resultPaths = color_histogram_feature_map[0].get(str_f, [])
        print("[INFO] {} total image(s) with d: {}, f: {}".format(len(resultPaths), d, str_f))
        # loop over the result paths
        for resultPath in resultPaths:
            img_map = {}
            img_map["image_url"] = resultPath.replace("./", "").replace("\\", "/")  ## convert
            # feature vector is too large to transfer, ignore it
            # img_map["image_feature"] = f
            img_map["distance_with_query"] = d
            result_map["similar_images"].append(img_map)
    
    result_map["similar_images_count"] = len(result_map["similar_images"])
    # serialize map to json
    print(result_map)
    json_result = json.dumps(result_map, sort_keys=True, indent=4)
    return json_result

# create hash index and vp-tree, save into disk
# 0 for ahash
# 1 for phash
# 2 for dhash
def create_hash_index(hash_type):
    print("[INFO] create image index, hash type:[{}]...".format(hash_names[hash_type]))
    imagePaths = list(cbir_paths.list_images(image_source_path))
    hashes = {}

    # loop over the image paths and create hash map
    for (i, imagePath) in enumerate(imagePaths):
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))

        # compute the hash for the image
        h = None
        if hash_type == 0:
            h = cbir_hash.average_hash(Image.open(imagePath))
        elif hash_type == 1:
            h = cbir_hash.phash(Image.open(imagePath))
        else:
            h = cbir_hash.dhash(Image.open(imagePath))
        
        # update the hashes map
        l = hashes.get(h, [])
        l.append(imagePath)
        hashes[h] = l
    
    # build the VP-Tree
    print("[INFO] building VP-Tree...")
    points = list(hashes.keys())
    tree = vptree.VPTree(points, hamming)

    # serialize the VP-Tree to disk
    print("[INFO] serializing VP-Tree...")
    f = open(hash_vptree_files[hash_type], "wb")
    f.write(pickle.dumps(tree))
    f.close()

    # serialize the hashes to dictionary
    print("[INFO] serializing hashes...")
    f = open(hash_map_files[hash_type], "wb")
    f.write(pickle.dumps(hashes))
    f.close()


# create color histogram feature index and vp-tree, save into disk
def create_color_histogram_index():
    print("[INFO] create image color histogram feature index...")
    imagePaths = list(cbir_paths.list_images(image_source_path))
    features = {}

    # loop over the image paths and create feature map
    for (i, imagePath) in enumerate(imagePaths):
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))

        # compute the color histogram feature for the image
        f = cbir_ch_feature.describe(cv2.imread(imagePath))
        
        # update the features map
        str_f = str(f)
        l = features.get(str_f, [])
        l.append(imagePath)
        features[str_f] = l
    
    # build the VP-Tree
    print("[INFO] building VP-Tree...")
    points = list(features.keys())
    points = [eval(f) for f in points]
    tree = vptree.VPTree(points, chi2_distance)

    # serialize the VP-Tree to disk
    print("[INFO] serializing VP-Tree...")
    f = open(color_histogram_feature_vptree_file, "wb")
    f.write(pickle.dumps(tree))
    f.close()

    # serialize the features to dictionary
    print("[INFO] serializing features...")
    f = open(color_histogram_feature_map_file, "wb")
    f.write(pickle.dumps(features))
    f.close()

# calculate hamming distance between 2 hash values
def hamming(a, b):
    return a - b


# calculate chi-squared distance between 2 color histogram features
def chi2_distance(a, b, eps = 1e-10):
    # compute the chi-squared distance
    d = 0.5 * np.sum([((i - j) ** 2) / (i + j + eps)
        for (i, j) in zip(a, b)])

    # return the chi-squared distance
    return d
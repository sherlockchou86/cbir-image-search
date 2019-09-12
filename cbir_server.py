
# CBIR image search engine server script

from flask import Flask
from flask import request
from PIL import Image
import cv2
import numpy as np

import cbir_index

app = Flask(__name__)

# hash-based search API entry
# calculate hash for uploaded image and get duplicated/near-duplicated images from image source
# return json string to client
@app.route("/hash-search", methods=["POST", "GET"])
def hash_search():
    if request.method == "POST":
        max_distance = int(request.form["max_distance"])
        query_hash_type = int(request.form["query_hash_type"])
        query_image = Image.open(request.files["query_image"].stream)  # PIL Image

        # perform search
        return cbir_index.hash_search(query_image, max_distance, query_hash_type)
    else:
        return "http method not allowed!"


# region-based color histogram search API entry
# calculate color feature for uploaded image and get similar images from image source
# return json string to client
@app.route("/color-histogram-search", methods=["POST", "GET"])
def color_histogram_search():
    if request.method == "POST":
        limit = int(request.form["limit"])
        query_image = Image.open(request.files["query_image"].stream)  # PIL Image
        query_image = cv2.cvtColor(np.asarray(query_image),cv2.COLOR_RGB2BGR)  # opencv Image

        # perform search
        return cbir_index.color_histogram_search(query_image, limit)
    else:
        return "http method not allowed!"


if __name__ == "__main__":
    cbir_index.init_index()
    app.run(host="0.0.0.0", port=8080, debug=True)

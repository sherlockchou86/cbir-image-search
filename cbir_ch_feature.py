
# calculate region-based color histogram feature, refer to https://www.pyimagesearch.com/2014/12/01/complete-guide-building-image-search-engine-python-opencv/

import numpy as np
import cv2

# bins for each channel in HSV color space
# we can change this to tune the effect
bins = (8, 12, 3)

# calculate region-based color histogram feature, the feature vector dimension is bins[0]*bins[1]*bins[2]*5
# image: input image which need to be calculated, OpenCV Image
def describe(image):
    # convert the image to the HSV color space and initialize
    # the features used to quantify the image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    features = []

    # grab the dimensions and compute the center of the image
    (h, w) = image.shape[:2]
    (cX, cY) = (int(w * 0.5), int(h * 0.5))

    # divide the image into four rectangles/segments (top-left,
    # top-right, bottom-right, bottom-left)
    segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h),
        (0, cX, cY, h)]

    # construct an elliptical mask representing the center of the
    # image
    (axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
    ellipMask = np.zeros(image.shape[:2], dtype = "uint8")
    cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)

    # loop over the segments
    for (startX, endX, startY, endY) in segments:
        # construct a mask for each corner of the image, subtracting
        # the elliptical center from it
        cornerMask = np.zeros(image.shape[:2], dtype = "uint8")
        cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
        cornerMask = cv2.subtract(cornerMask, ellipMask)

        # extract a color histogram from the image, then update the
        # feature vector
        hist = histogram(image, cornerMask)
        features.extend(hist)

    # extract a color histogram from the elliptical region and
    # update the feature vector
    hist = histogram(image, ellipMask)
    features.extend(hist)

    # return the feature vector
    # the vector contains 4 corner regions and 1 center region, 5 parts totally
    # the dimension equals bins[0]*bins[1]*bins[2]*5
    return features


# calculate color histogram feature for a single region
# image: image to be calculated
# mask:  region to be calculated
def histogram(image, mask):
    # extract a 3D color histogram from the masked region of the
    # image, using the supplied number of bins per channel
    hist = cv2.calcHist([image], [0, 1, 2], mask, bins, [0, 180, 0, 256, 0, 256])

    # normalize the histogram
    hist = cv2.normalize(hist, hist).flatten()

    # return the histogram
    return hist
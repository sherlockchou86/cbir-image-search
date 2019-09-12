
'''
import numpy as np

def chi2_distance(a, b, eps = 1e-10):
    # compute the chi-squared distance
    d = 0.5 * np.sum([((i - j) ** 2) / (i + j + eps)
        for (i, j) in zip(a, b)])

    # return the chi-squared distance
    return d


a = [0.2, 0.3, 0.1, 0.2, 0.05, 0.15]
b = [0.2, 0.3, 0.1, 0.2, 0.05, 0.15]

print(chi2_distance(a,b))
'''

'''

import numpy as np
import cv2
import matplotlib.pyplot as plt

img1 = cv2.imread('static/image_sources/20190905085342.jpg')          # queryImage
img2 = cv2.imread('static/image_sources/20190905085305..jpg') # trainImage

# Initiate ORB detector
orb = cv2.ORB_create()

# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

# create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors.
matches = bf.match(des1,des2)

# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)

# Draw first 10 matches.
img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10],None, flags=2)

plt.imshow(img3),plt.show()

'''

'''

import numpy as np
import cv2
import matplotlib.pyplot as plt

img1 = cv2.imread('static/image_sources/20190905085342.jpg') # queryImage
img2 = cv2.imread('static/image_sources/20190905085305.jpg') # trainImage

# Initiate SIFT detector
sift = cv2.xfeatures2d.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

# BFMatcher with default params
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1,des2, k=2)

# Apply ratio test
good = []
for m,n in matches:
    if m.distance < 0.75*n.distance:
        good.append([m])

# cv.drawMatchesKnn expects list of lists as matches.
img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=2)

plt.imshow(img3)
plt.show()

'''


import numpy as np
import cv2
import matplotlib.pyplot as plt

img1 = cv2.imread('static/image_sources/20190905085342.jpg')          # queryImage
img2 = cv2.imread('static/image_sources/20190905085305.jpg') # trainImage

# Initiate ORB detector
orb = cv2.ORB_create()

# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

# create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors.
matches = bf.match(des1,des2)

# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)

# Draw first 10 matches.
img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10],None, flags=2)

plt.imshow(img3),plt.show()
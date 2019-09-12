# cbir-image-search
use image hash, region-based color histogram to create image search engine(CBIR)

# how to use
1. run `python cbir_server.py` to start server
2. open .sln file in cbir-client-demo with visual studio 2015+. press F5 to run client app
3. search images which are similar with those in static/images_sources directory

you can delete .pickle file to recreate cache if you have any more image file to be tested in image_sources directory

![](https://github.com/sherlockchou86/cbir-image-search/blob/master/demo.jpg)
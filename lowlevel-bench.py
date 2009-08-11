#!/usr/bin/env python
#
# Low-level TileCache benchmark

__author__ = "Sylvain Pasche (sylvain.pasche@gmail.com)"

import cStringIO as StringIO
import time
import sys

import PIL.Image as Image

from config import *

ITERATIONS = 50
NUM_LAYERS = 59

IMAGE_PATHS = DATA_PATH + "/veloland/%s/17/000/000/006/000/000/006.png"
ALL_IMAGES = [IMAGE_PATHS % l for l in LAYERS]

class Timer:
    def __init__(self):
        self.times_by_tag = {}
        self.starts = []
        # for tag ordering
        self.tags = []
    def reset(self):
        self.starts.append(time.time())
    def mark(self, tag):
        end = time.time()
        assert len(self.starts) > 0
        duration = end - self.starts.pop()
        if not tag in self.times_by_tag.keys():
            self.tags.append(tag)
        times = self.times_by_tag.setdefault(tag, [])
        times.append(duration)
    def dump(self):
        for tag in self.tags:
            times = self.times_by_tag[tag]
            print("tag " + tag)
            import numpy
            import scipy, scipy.stats
            times = [tt * 1000 for tt in times]
            amean = sum(times) / len(times)
            gmean = scipy.stats.gmean(times)
            print "\tarith mean duration: ", amean, " gmean", gmean, " ms stddev:", numpy.std(times)

t = Timer()

def main():
    layers = LAYERS[:NUM_LAYERS]
    images = [IMAGE_PATHS % l for l in layers]

    result = None
    start = time.time()
    for i in images:
        t.reset()
        image = Image.open(i)
        # force load
        image.load()
        t.mark("decode")

        if not result:
            result = image
        else:
            t.reset()
            result.paste(image, None, image)
            t.mark("merge")

    image_str = None

    t.reset()
    buffer = StringIO.StringIO()
    result.save(buffer, result.format)
    buffer.seek(0)
    image_str = buffer.read()
    assert image_str[:4] == '\x89PNG'
    if image_str:
        open(DATA_PATH + "/result.png", "w").write(image_str)
    t.mark("encode")

    duration = time.time() - start
    return duration

def decode():
    for img in ALL_IMAGES:
        image = Image.open(img)
        image.load()

if __name__ == "__main__":
    if "--generate-headers" in sys.argv:
        images_header = "// Generated file, do not edit\n"
        images_header += "\n".join(['DATA_PATH "/veloland/%s/17/000/000/006/000/000/006" SUFFIX "." EXT,' % l for l in LAYERS])
        open("images.h", "w").write(images_header)
        open("data_path.h", "w").write('// Generated file, do not edit\n#define DATA_PATH "%s"' % DATA_PATH)
        sys.exit(0)

    for i in range(ITERATIONS):
        t.reset()
        main()
        t.mark("global")
    t.dump()

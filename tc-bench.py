#!/usr/bin/env python
#
# Tilecache merging benchmark

__author__ = "Sylvain Pasche (sylvain.pasche@gmail.com)"

import time
import urllib2
import threading
import sys
import pdb
from optparse import OptionParser

from TileCache.Service import Service

from config import *

class Fetcher:
    def check_image(self, image):
        assert image[:4] == '\x89PNG', "Didn't get a PNG file from server"

class HTTPFetcher(Fetcher):
    def fetch(self, options, bbox, layers):
        layer_param = ','.join(layers)
        if not options.server:
            raise Exception("Missing server. Use --server parameter")
        url = TILES_URL % {'server': options.server, 'layers': layer_param, 'bbox': bbox}

        if options.verbose:
            print url
        if options.dummy:
            return

        start = time.time()
        response = urllib2.urlopen(url)
        image = response.read()
        duration = time.time() - start
        self.check_image(image)
        return duration

class TCFetcher(Fetcher):
    def __init__(self):
        TC_CONFIG = TC_CONFIG_IN[:-len(".in")]
        new_content = open(TC_CONFIG_IN).read().replace("@@DATA_PATH@@", DATA_PATH)
        f = open(TC_CONFIG, "w")
        f.write(new_content)
        f.close()

        self.tc_service = Service.load(TC_CONFIG)


    def fetch(self, options, bbox, layers):
        # TODO: generate TILES_URL with those parameters.
        params = {'WIDTH': ['256'], 'SERVICE': ['WMS'],
                  'FORMAT': ['image/png'], 'REQUEST': ['GetMap'], 'HEIGHT': ['256'],
                  'SRS': ['EPSG:21781'], 'VERSION': ['1.1.1']}
        params["LAYERS"] = ','.join(layers)
        params["BBOX"] = bbox
        start = time.time()
        format, image = self.tc_service.dispatchRequest(params)
        duration = time.time() - start
        assert format == "image/png"
        self.check_image(image)
        return duration

def main():
    parser = OptionParser()
    parser.add_option("-t", "--thread-count", type="int", default=1)
    parser.add_option("-l", "--layer-count", type="int", default=1)
    parser.add_option("-c", "--iterations", type="int", default=10)
    parser.add_option("-v", "--verbose", action="store_true")
    parser.add_option("-d", "--dummy", action="store_true")
    parser.add_option("--profile", action="store_true")
    parser.add_option("", "--server")

    parser.add_option("", "--fetcher", default="tc",
                      help='Fetcher type. Can be tc or http')
    (options, args) = parser.parse_args()

    assert options.thread_count == 1, "More than one thread not implemented yet"
    times = []

    if options.layer_count > len(LAYERS):
        print("Too many layers (max is %i)" % len(LAYERS))
        sys.exit(1)

    opt_to_fetcher = {
        "http": HTTPFetcher,
        "tc": TCFetcher,
    }
    if not options.fetcher in opt_to_fetcher:
        print("Invalid fetcher")
        sys.exit(1)
    fetcher = opt_to_fetcher[options.fetcher]()

    def do_iterations():
        for i in range(options.iterations):
            selected_layers = LAYERS[0:options.layer_count]
            t = fetcher.fetch(options, BBOX, selected_layers)
            if t:
                times.append(t)
    if options.profile:
        import cProfile
        cProfile.runctx('do_iterations()', globals(), locals(), 'prof_results')
    else:
        do_iterations()

    if times:
        print "mean duration: ", (sum(times) / len(times)) * 1000, " ms"

if __name__ == "__main__":
    main()

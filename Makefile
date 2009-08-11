bench-cairo: bench-cairo.cpp images.h
	g++ -o bench-cairo bench-cairo.cpp -O6 -g -Wall $$(pkg-config --cflags --libs cairo gdk-pixbuf-2.0 gdk-2.0)

clean:
	rm -f *pyc bench-cairo images.h data_path.h data/tilecache.cfg data/output_cairo.png data/result.png


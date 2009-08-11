// Cairo TileCache benchmark
//
// Author: Sylvain Pasche (sylvain.pasche@gmail.com)
// based on png-flatten.c, by Carl Worth (see Cairo licence)

#include <stdio.h>
#include <sys/time.h>

#include <cairo.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <gdk/gdk.h>

#include "data_path.h"

#include <stack>
#include <map>
#include <list>
#include <iostream>
#include <algorithm>

using namespace std;

// Paths and options:

// Number of iteration to run

const int ITERATION_COUNT = 2;

// Number of images to merge (shouldn't be modified).
const int IMAGE_COUNT = 59;

// Image suffix to use

#define SUFFIX ""
//#define SUFFIX "_uncompressed"
//#define SUFFIX "_compressed"
//#define SUFFIX "_compressed_im"

// Image size, should match the size of the tiles used.

#define IMAGE_WIDTH 256
#define IMAGE_HEIGHT 256

// Image extension

#define EXT "png"
//#define EXT "tiff"

// PNG image output path

#define PNG_OUTPUT DATA_PATH "/output_cairo.png"

// Whether to use the Cairo loader, or Gdk-Pixbuf
const int use_cairo_png_loader = 0;
// Whether to use the write stream function instead of writing result to a file.
const int write_stream = 0;

// End of configuration section

const char* images[] = {
#include "images.h"
};

static cairo_status_t png_write_func(void* closure, const unsigned char* data, unsigned int length)
{
  //printf("Got %u png bytes in stream\n", length);
  return CAIRO_STATUS_SUCCESS;
}


typedef struct timeval timeval_t;

/**
 * Simple time measurement class.
 */
class Timer {

public:
  void reset() {
    timeval_t t;
    gettimeofday(&t, NULL);
    starts_.push(t);
  };
  void mark(const char* tag) {
    timeval_t end;
    gettimeofday(&end, NULL);
    timeval_t start = starts_.top();
    double duration = (end.tv_sec - start.tv_sec) * 1000.0; // sec to ms
    duration += (end.tv_usec - start.tv_usec) / 1000.0; // us to ms
    starts_.pop();

    if (times_.find(tag) == times_.end()) {
      time_pair p(tag, time_list());
      times_.insert(p);
      tags_.push_back(tag);
    }
    times_.find(tag)->second.push_back(duration);
  };

  void dump() {
    for (list<string>::const_iterator it = tags_.begin(); it != tags_.end(); ++it) {
      show_times(times_.find(*it));
    }
  };

private:
  typedef list<double> time_list;
  typedef map<string, time_list > times_map;
  typedef pair<string, time_list > time_pair;

  static void show_times(const times_map::const_iterator& p) {
    cout << "Time for tag " << p->first << endl;
    cout << "  mean " << mean(p->second) << endl;
  };

  static double mean(const time_list& tl) {
    double sum = 0;
    for (time_list::const_iterator it = tl.begin(); it != tl.end(); ++it)
      sum += *it;
    return sum / tl.size();
  };

  list<string> tags_;
  stack<timeval_t> starts_;
  times_map times_;
};

Timer t;

static int
do_merge(const char* images[], int image_count)
{
    cairo_t *cr = 0;
    cairo_surface_t *argb = 0, *rgb24 = 0;
    cairo_status_t status;
    const char *input;
    int i;

    GError *error = NULL;
    GdkPixbuf *pixbuf = NULL;

    rgb24 = cairo_image_surface_create (CAIRO_FORMAT_RGB24,
                                        IMAGE_WIDTH,
                                        IMAGE_HEIGHT);

    if (!rgb24) {
      printf("Failed to create surface\n");
      return 1;
    }
    cr = cairo_create (rgb24);
    cairo_set_source_rgb (cr, 1.0, 1.0, 1.0); /* white */
    cairo_paint (cr);

    for (i = 0; i < image_count; i++) {
      input = images[i];
      t.reset();

      if (use_cairo_png_loader) {
        argb = cairo_image_surface_create_from_png (input);
        status = cairo_surface_status (argb);
        t.mark("decode");
        if (status) {
            fprintf (stderr, "Error: Failed to load %s: %s\n",
                     input, cairo_status_to_string (status));
            return 1;
        }

        t.reset();
        cairo_set_source_surface (cr, argb, 0, 0);
      } else {

        t.reset(); // decode_global
        pixbuf = gdk_pixbuf_new_from_file(input, &error);
        t.mark("decode");
        if (!pixbuf) {
          fprintf (stderr, "Unable to read file: %s\n", error->message);
          g_error_free (error);
          return 1;
        }
#if 0
        printf("Pixbuf: %p\n", pixbuf);

        printf("Pixbuf info:\n  n_channels: %d\n  has_alpha: %d\n  width: %d\n  height: %d\n",
          gdk_pixbuf_get_n_channels(pixbuf),
          gdk_pixbuf_get_has_alpha(pixbuf),
          gdk_pixbuf_get_width(pixbuf),
          gdk_pixbuf_get_height(pixbuf)
        );
#endif
        t.reset();
        gdk_cairo_set_source_pixbuf (cr, pixbuf, 0, 0);
        t.mark("set source pixbuf");
        t.mark("decode_global");
        t.reset();
        g_object_unref(pixbuf);
      }

      cairo_paint (cr);
      t.mark("merge");

      if (use_cairo_png_loader) {
        cairo_surface_destroy (argb);
      }
    }

    if (cr)
      cairo_destroy (cr);

    t.reset();


    if (write_stream) {
      status = cairo_surface_write_to_png_stream (rgb24, png_write_func, 0);
    } else {
      status = cairo_surface_write_to_png (rgb24, PNG_OUTPUT);
    }

    cairo_surface_destroy (rgb24);
    if (status) {
        fprintf (stderr, "Error: Failed to write %s: %s\n",
                 PNG_OUTPUT, cairo_status_to_string (status));
        return 1;
    }

    t.mark("encode");
    return 0;
}

int
main (int argc, char *argv[])
{
  int rv, i;
  int tot_images = sizeof(images) / sizeof(*images);
  if (IMAGE_COUNT > tot_images) {
    printf("Error, too many images\n");
    return 1;
  }

  g_type_init();

  for (i = 0; i < ITERATION_COUNT; i++) {
    t.reset();
    if ((rv = do_merge(images, IMAGE_COUNT))) {
      fprintf (stderr, "Aborting because of an error\n");
      return rv;
    }
    t.mark("global");
  }
  t.dump();

  return 0;
}

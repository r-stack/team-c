#!/usr/bin/env python

import os
import sys
import json

from clarifai.client import ClarifaiApi


def tag_images_in_directory(path, api):
  images = []
  path = path.rstrip(os.sep)
  for fname in os.listdir(path):
    images.append((open(os.path.join(path, fname), 'rb'), fname))
  return api.tag_images(images)



def check_pretty(imageurl):
    api = ClarifaiApi()
    #api.set_model("")
    if imageurl.startswith('http'):
        response = api.tag_image_urls(imageurl, select_classes="pretty,human")
    elif os.path.isdir(imageurl):
        response = tag_images_in_directory(imageurl)
    elif os.path.isfile(imageurl):
        with open(imageurl,'rb') as image_file:
            response = api.tag(image_file, select_classes="pretty,human,man,woman")
    else:
        raise Exception("Must input url, directory path, or file path")
    
    print json.dumps(response, indent=2)
    return response

def main(argv):
  if len(argv) > 1:
    imageurl = argv[1]
  else:
    imageurl = 'http://clarifai-img.s3.amazonaws.com/test/toddler-flowers.jpeg'

  api = ClarifaiApi()
  #api.set_model("")
  if imageurl.startswith('http'):
    response = api.tag_image_urls(imageurl)
  elif os.path.isdir(imageurl):
    response = tag_images_in_directory(imageurl)
  elif os.path.isfile(imageurl):
    with open(imageurl,'rb') as image_file:
      response = api.tag(image_file, select_classes="pretty,man,woman")
  else:
    raise Exception("Must input url, directory path, or file path")

  resultCode = json.dumps(response, indent=2
                          )
  print resultCode


if __name__ == '__main__':
  main(sys.argv)

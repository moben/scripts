#!/bin/env python

# Set your screen's width and height here, until I find a way to 
# get them automatically or turn this into a cli parameter.
# This doesn't scale the result, as that tends to turn out bad
# Instead it just discards all pictures that don't fit onto the target.
screenwidth  = 1600
screenheight = 900

# Update frequency in minutes
# Don't set this to high, that wouldn't be nice
freq = 30

# Directory to save to
# "~" is automagically expanded
dir  = "~/Bilder/xkcd-background/"

# Filename to save to (extension needed!)
file = "xkcd.png"

# Font to use (needs to be in a format that ImageMagick can understand)
# Get the default for free (as in beer) from
# http://hvdfonts.com/assets/Document/15/HVD_Comic_Serif_Pro.zip
font = "HVD-Comic-Serif-Pro-Regular"

# The url to fetch from
# Probably shouldn't change
url  = "http://dynamic.xkcd.com/random/comic/"

color = "#ffffff80"
convertargs = [ '-background', color, '-fill', 'black', '-gravity', 'center', '-font', font, '-size' ]


import sys, os, textwrap, subprocess, tempfile
import urllib2
from time import sleep
try:
	from lxml import etree
except ImportError:
	exit("This script needs the libxml2 python bindings (e.g. libxml2-python on Fedora)")

try:
	subprocess.check_call(['convert', '-version'])
	subprocess.check_call(['identify', '-version'])
except OSError:
	exit("This script needs the convert and identify tools from the ImageMagick project")


def urlopen2(url):
	while True:
		try:
			x = urllib2.urlopen(url)
		except urllib2.URLError, reason:
			print "Got an error trying to open the url:", reason
			pass
		except urllib2.HTTPError, code:
			print "Got HTTP code", code
			pass
		else:
			break
	return x

dir = os.path.expanduser(dir)

try:
	os.makedirs(dir)
except OSError:
	pass

os.chdir(dir)

while True:
	titlefile = tempfile.NamedTemporaryFile(suffix='.png')
	captionfile = tempfile.NamedTemporaryFile(suffix='.png')
	imagefile = tempfile.NamedTemporaryFile()
	resultfile = tempfile.NamedTemporaryFile(suffix='.png')

	resultheight = 0

	index = urlopen2(url)

	myparser = etree.XMLParser(recover=True)
	index2 = etree.parse(index, myparser)

	title = index2.find('//{http://www.w3.org/1999/xhtml}h1').text
	img = index2.find('//{http://www.w3.org/1999/xhtml}img[@title]')
	imgsrc = img.attrib.get('src')
#	caption = textwrap.fill(img.attrib.get('title'))
	caption = img.attrib.get('title')

	image = urlopen2(imgsrc)

	imagefile.write(image.read())
	imagefile.flush()

	subprocess.check_call(['convert'] + convertargs + [str(screenwidth).strip('\n ') + 'x', '-pointsize', '48', 'caption:' + title, '-gravity', 'north', '-splice', '0x10', titlefile.name])
	subprocess.check_call(['convert'] + convertargs + [str(screenwidth).strip('\n ') + 'x', '-pointsize', '24', 'caption:' + caption, '-gravity', 'south', '-splice', '0x10', captionfile.name])

	subprocess.check_call(['convert', '-background', color, '-alpha', 'on', '-gravity', 'center', '-append', titlefile.name, imagefile.name, captionfile.name, resultfile.name])

	# Clean up now, rather than later
	titlefile.close()
	captionfile.close()
	imagefile.close()
	
	resultheight = int(subprocess.check_output(['identify', '-format', '%h', resultfile.name]))

	if resultheight <= screenheight:
		targetfile = open(dir + file, 'w+')

		targetfile.write(resultfile.read())
		targetfile.flush()
		targetfile.close()

		resultfile.close()

		sleep(60 * freq)
	else:
		resultfile.close()

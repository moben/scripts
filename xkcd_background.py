#!/usr/bin/python2

# Set your screen's width and height in pixels here, until I find a way to 
# get them automatically or turn this into a cli parameter.
# This doesn't scale the result, as that tends to turn out bad
# Instead it just discards all pictures that don't fit onto the target.
screenwidth  = 1600
screenheight = 900 - 50

# Update frequency in minutes
# Don't set this to high, that wouldn't be nice
freq = 30

# Directory to save to
# "~" is automagically expanded
dir  = "~/Bilder/"

# Filename to save to (extension needed!)
file = "xkcd-background.png"

# Font to use (needs to be in a format that ImageMagick can understand)
# Get the default for free (as in beer) from
# http://hvdfonts.com/assets/Document/15/HVD_Comic_Serif_Pro.zip
font = "HVDComicSerifPro"

# The url to fetch from
# Probably shouldn't change
url  = "http://dynamic.xkcd.com/random/comic/"

color = "#ffffff80"
convertargs = [ '-background', color, '-fill', 'black', '-gravity', 'center', '-font', font, '-size' ]


# Don't change!
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
htmlns = r'{http://www.w3.org/1999/xhtml}'

import sys, os, textwrap, subprocess, tempfile
import urllib2
from time import sleep
from xml.dom.minidom import parse


NULL = open("/dev/null")

try:
	subprocess.check_call(['convert', '-version'], stdout=NULL, stderr=NULL)
	subprocess.check_call(['identify', '-version'], stdout=NULL, stderr=NULL)
except OSError:
	exit("This script needs the convert and identify tools from the ImageMagick project")


def my_urlopen(url):
	try:
		x = urllib2.urlopen(url)
	except urllib2.URLError, reason:
		print "Got an error trying to open the url:", reason
		exit(1)
	except urllib2.HTTPError, code:
		print "Got HTTP code", code
		exit(2)
	else:
		return x
	print """Something went very wrong trying to open""", url, """
please report this"""
	exit(200)

dir = os.path.expanduser(dir)

try:
	os.makedirs(dir)
except OSError:
    pass

os.chdir(dir)

# Here the magic starts

titlefile = tempfile.NamedTemporaryFile(suffix='.png')
captionfile = tempfile.NamedTemporaryFile(suffix='.png')
imagefile = tempfile.NamedTemporaryFile()
resultfile = tempfile.NamedTemporaryFile(suffix='.png')

resultheight = 0

index = my_urlopen(url)

index2 = parse(index)
div_tags = index2.getElementsByTagName("div")
img_tags = index2.getElementsByTagName("img")

print img_tags

for tag in img_tags:
	if tag.hasAttribute("title"):
		title   = tag.getAttribute("alt")
		caption = tag.getAttribute("title")
		image   = tag.getAttribute("src")
		break
else:
	print """
Couldn't find a comic, please report this.
Additional information:
Random url:""", index.geturl()
	exit(100)


print "Comic   :", title
print "Caption :", caption
print "Url     :", image


#caption = textwrap.fill(caption)

image = my_urlopen(image)

imagefile.write(image.read())
imagefile.flush()

subprocess.check_call(['convert'] + convertargs + [str(screenwidth).strip('\n ') + 'x', '-alpha', 'on', '-pointsize', '48', 'caption:' + title,   '-gravity', 'north', '-splice', '0x10', titlefile.name])
subprocess.check_call(['convert'] + convertargs + [str(screenwidth).strip('\n ') + 'x', '-alpha', 'on', '-pointsize', '24', 'caption:' + caption, '-gravity', 'south', '-splice', '0x10', captionfile.name])

subprocess.check_call(['convert', '-background', color, '-alpha', 'Remove', '-gravity', 'center', '-append', titlefile.name, imagefile.name, captionfile.name, resultfile.name])


resultheight = int(subprocess.check_output(['identify', '-format', '%h', resultfile.name]))

if resultheight <= screenheight:
	targetfile = open(dir + file, 'w+')

	targetfile.write(resultfile.read())
	targetfile.flush()
	targetfile.close()

# Explicit is better than implicit
titlefile.close()
captionfile.close()
imagefile.close()
resultfile.close()

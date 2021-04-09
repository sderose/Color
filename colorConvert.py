#!/usr/bin/env python
#
# colorConvert.py: Normalize various color specs.
# 2016-04-14: Written. Copyright by Steven J. DeRose.
#
from __future__ import print_function
import sys, os, argparse
import re
import math
import codecs
import colorsys
import webcolors

from alogging import ALogger
from MarkupHelpFormatter import MarkupHelpFormatter

lg = ALogger(1)
palColors = {}

__metadata__ = {
    "title"        : "colorConvert.py",
    "description"  : "Normalize various color specs.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2016-04-14",
    "modified"     : "2021-03-03",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]


descr="""
=head1 Description

Normalize colors to a given form from a variety of other forms.

Forms accepted:
    #RGB
    #RRGGBB
    #RRRGGGBBB
    #RRRRGGGGBBBB
    rgb(r, g, b)
        rgb(r, g, b, h)
    hsv(h, s, v))
    hsva(h, s, v, a)
    yiq(y, i, q)
    HTML and CSS color names

Arguments to the function-style forms may be specified as any of:
    decimal integers from 0 to 255
    hexadecimal numbers prefixed with "0x", from 0x00 to 0xff
    octal numbers with a leading "0"
    decimal non-integers from 0 to 255
    decimal numbers followed by a percent sign ("%")

B<Note>: If some input cannot be parsed,
a I<ValueError> exception is raised.


=head1 Related Commands

Packages: colorsys, webcolors L<https://pypi.python.org/pypi/webcolors/1.3>

Pantone conversion is said to be supported
by L<https://pypi.python.org/pypi/pycolorname>

C<python-colormath> supports many color spaces, but it's I<big>.
See L<https://python-colormath.readthedocs.org/en/latest/>.


=head1 Known bugs and limitations

Although the rgba() and hsva() forms are accepted, the alpha (transparency)
component is discarded.

CMYK, spot color systems, and many other possibilities are not supported.

Conversion I<to> named HTML colors is not provided (yet).

A feature to pick, for each input color, the nearest color from a given
pal*[ae]t*e*, would be helpful.

=head1 References

L<http://www.w3.org/TR/css3-color/#SRGB>

L<https://en.wikipedia.org/wiki/CMYK_color_model#Conversion>

=History=

  2016-04-14: Written. Copyright by Steven J. DeRose.
  2018-04-18: lint.
  2020-03-03: New layout.


=Rights=

Copyright 2016-04-14 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
For further information on this license, see
[https://creativecommons.org/licenses/by-sa/3.0].

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=head1 Options
"""


knownSchemes = [ 'rgb', 'rgba', 'hsv', 'hsva', 'yiq', 'hls' ]
token = r'\s*([\da-fA-F.]+%?)'
try:
    fe = r'(\w+)\(%s,%s,%s(,%s)?\)' % (token,token,token,token)
    print("Expr: /%s/'" % (fe))
    functionExpr = re.compile(fe)
except Exception as e:
    print("Bad regex: '%s'.\n    %s" % (fe, e))
    sys.exit()


###############################################################################
#
def processOptions():
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=MarkupHelpFormatter)

    parser.add_argument(
        "--color",  # Don't default. See below.
        help='Colorize the output.')
    parser.add_argument(
        "--iencoding",        type=str, metavar='E', default="utf-8",
        help='Assume this character set for input files. Default: utf-8.')
    parser.add_argument(
        "--oencoding",        type=str, metavar='E',
        help='Use this character set for output files.')
    parser.add_argument(
        "--out",              type=str, default='rgb6', choices=
        [ 'rgb3', 'rgb6', 'rgb9', 'rgbdec', 'rgb%', 'hsv', 'hsl', 'yiq', 'name' ],
        help='Suppress most messages.')
    parser.add_argument(
        "--pal",              type=str,
        help='File of "known" colors, one per line as #RRGGBB.')
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--unicode",          action='store_const',  dest='iencoding',
        const='utf8', help='Assume utf-8 for input files.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    parser.add_argument(
        'files',             type=str,
        nargs=argparse.REMAINDER,
        help='Path(s) to input file(s)')

    args0 = parser.parse_args()
    if (args0.verbose): lg.setVerbose(args0.verbose)
    if (args0.color == None):
        args0.color = ("USE_COLOR" in os.environ and sys.stderr.isatty())
    lg.setColors(args0.color)
    return(args0)


###############################################################################
#
def doOneFile(fh, path):
    """Read and deal with one individual file.
    """
    recnum = 0
    rec = ""
    while (True):
        try:
            rec = fh.readline()
        except IOError as e:
            lg.error("Error (%s) reading record %d of '%s'." %
                (type(e), recnum, path), stat="readError")
            break
        if (len(rec) == 0): break # EOF
        recnum += 1
        rec = rec.rstrip()
        rgbTriple = cconvert(rec)
        outColor = serialize(rgbTriple, args.out)
        if (args.pal):
            #nearest = findNearestPalColor(serialize(rgbTriple, 'rgb6'))
            #outColor += '\t Nearest: %s' % (nearest)
            lg.eMsg(0, "PAL not yet supported.")
            sys.exit()
        print(outColor)
    fh.close()
    return(recnum)


def cconvert(s):
    # Try HTML and CSS names. 'webcolors' returns as $RRGGBB.
    rgbString = None
    if (s in webcolors.html4_names_to_hex):
        rgbString = webcolors.html4_names_to_hex[s]
        #print("Found '%s' in HTML4 colors. Got: %s." % (s, rgbString))
    elif (s in webcolors.css2_names_to_hex):
        rgbString = webcolors.css2_names_to_hex[s]
        #print("Found '%s' in CSS2 colors. Got: %s." % (s, rgbString))
    elif (s in webcolors.css21_names_to_hex):
        rgbString = webcolors.css21_names_to_hex[s]
        #print("Found '%s' in CSS2.1 colors. Got: %s." % (s, rgbString))
    elif (s in webcolors.css3_names_to_hex):
        rgbString = webcolors.css3_names_to_hex[s]
        #print("Found '%s' in CSS3 colors. Got: %s." % (s, rgbString))
    if (rgbString is not None):
        s = rgbString

    # Try functional notations, like 'rgb(12, 50%, 0xA0)'
    mat = re.match(functionExpr, s)
    if (mat):
        #print("functional")
        func  = mat.group(1)
        a1    = convertNumber(mat.group(2))
        a2    = convertNumber(mat.group(3))
        a3    = convertNumber(mat.group(4))
        if (mat.group(5)): alpha = convertNumber(mat.group(5))
        else: alpha = 0

        if (func == 'rgb' or func == 'rgba'):
            rgbTriple = [ a1, a2, a3 ]
        elif (func == 'hls'):
            rgbTriple = colorsys.hls_to_rgb(a1, a2, a3)
        elif (func == 'hsv'):
            rgbTriple = colorsys.hsv_to_rgb(a1, a2, a3)
        elif (func == 'yiq'):
            rgbTriple = colorsys.yiq_to_rgb(a1, a2, a3)
        else:
            raise ValueError('Unrecognized scheme "%s".' % (func))

    # Try the #RRGGBB types (including re-processing ones from names!)
    elif (s.startswith('#')):
        if (len(s) % 3 != 1):
            raise ValueError('Bad length for #rgb color.')
        per = int(len(s)/3)
        #print("rgb%d" % (per))
        rgbTriple = [ ]
        for i in range(3):
            piece = s[per*i+1:per*i+per+1]
            if (len(piece)==1): piece += piece
            rgbTriple.append(convertNumber('0x' + piece))

    else:
        raise ValueError('Unrecognized syntax: "%s".' % (s))

    return(rgbTriple)


# Take various numeric forms, and return a float in 0..1
def convertNumber(s):
    #print("converting: '%s'." % (s))
    try:
        if (s.endswith('%')):    return(float(s[0:-1])/100)
        if (s.startswith('0x')): return(int(s[2:],16)/255.0)
        if (s.startswith('0')):  return(int(s,8)/255.0)
        if ('.' in s):           return(float(s))
        return(float(int(s)/255.0))
    except ValueError as e:
        print("Cannot parse number from '%s'.\n    %s" % (s, e))
        sys.exit()

# Convert a tuple of floats to the chosen output format
def serialize(rgb, fmt):
    if (args.out == 'rgb3'):
        return('#%01x%01x%01x' %
              (int(rgb[0]*15), int(rgb[1]*15), int(rgb[2]*15)))
    elif (args.out == 'rgb6'):
        return('#%02x%02x%02x' %
              (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))
    elif (args.out == 'rgb9'):
        return('#%03x%03x%03x' %
              (int(rgb[0]*4095), int(rgb[1]*4095), int(rgb[2]*4095)))
    elif (args.out == 'rgdDec'):
        return('rgb(%3d, %3d, %3d)' %
              (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))
    elif (args.out == 'rgb%'):
        return('rgb(%5.1f%%, %5.1f%%, %5.1f%%)' %
              (rgb[0], rgb[1], rgb[2]))

    elif (args.out == 'hsv'):
        return('hsv(%5.3f%%, %5.3f%%, %5.3f%%)' %
              colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2]))
    elif (args.out == 'hls'):
        return('hls(%5.1f%%, %5.1f%%, %5.1f%%)' %
              colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2]))
    elif (args.out == 'yiq'):
        return('yiq(%5.1f%%, %5.1f%%, %5.1f%%)' %
              colorsys.rgb_to_yiq(rgb[0], rgb[1], rgb[2]))
    else:
        raise ValueError('Unknown output format "%s".' % (args.out))


def cdistance(rgb1, rgb2):
    tot = 0.0
    for i in range(len(rgb1)):
        tot += (rgb1[i]-rgb2[i])**2
    return(math.sqrt(tot))

"""
def findNearestPalColor(rgb6):
    minDist = 999
    minRGB = None
    for i in range(len(pal)):
        thisDist = cdistance(rgb5, pal[i])
        if (abs(thisDist) < abs(minDict)):
            minDict = thisDict
            minRGB = pal[i]
    return(minRGB)
"""


###############################################################################
# Main
#
args = processOptions()

if (args.pal):
    try:
        pfh = codecs.open(args.pal, mode='r',  encoding=args.iencoding)
    except IOError as e:
        lg.error("Can't open -pal file '%s'." % (args.pal))
        sys.exit()
    precnum = 0
    while(True):
        rec = pfh.readline()
        if (rec==""): break
        precnum += 1
        rec = rec.trim()
        if (not re.match('#[0-9a-fA-F]{6,6}', rec)):
            lg.error("%s:%d: Bad record: '%s'." % (args.pal, precnum, rec))
            sys.exit()
        else:
            palColors[rec] = 1
    pfh.close()

if (not args.files):
    if (not args.quiet): print("Waiting on STDIN...")
    doOneFile(sys.stdin, 'STDIN')
else:
    for f in (args.files):
        try:
            fh = codecs.open(f, mode='r', encoding=args.iencoding)
        except IOError as e:
            lg.error("Can't open '%s'." % (f), stat="CantOpen")
            sys.exit()
        doOneFile(fh, f)
        fh.close()

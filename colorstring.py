#!/usr/bin/env python
#
# 2018-08-29: Converted by perl2python, by Steven J. DeRose.
# Original Perl version written <2006-10-04, by Steven J. DeRose.
#
from __future__ import print_function
import sys, os, re
import argparse
from subprocess import check_output

import alogging
from ColorManager import ColorManager

lg = alogging.ALogger(1)
cm = ColorManager()
args = None

__metadata__ = {
    'title'        : "colorstring.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2018-08-29",
    'modified'     : "2020-10-02",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Usage=

colorstring [options] colorname [text]

Return the escape sequence to switch an ANSI terminal to a given color,
or turn stdin to that color.

Usage examples:
    PS1=`colorstring -ps Cyan` Hello, `colorstring -ps green`"world ==>"
    colorstring --list

Colors are specified as a named
foreground color, background color, and/or text effect, such as
"red/yellow/bold". For full details on the naming conventions, see
`colorNames.md` or `ColorManager.py`. There is also a Perl version.

Such sequences can be gotten
in various forms as needed for use in bash scripts, bash prompt-strings,
Perl code, etc. (see options).

This script can also:

* display lists of colors (`--list`, `--table`);

* colorize STDIN (`--all`), messages (`-m`), or warnings (`-w`); or

* interact with the *nix `lscolors` command
(`--lscolorset`, `--lsget`, `--lslist`, and `--lsset`). Some of these
require the (usually Linux) command 'dircolors'.

==Color names used==

The color names available are defined in F<bingit/SHELL/colorNames.md>,
which supercedes anything in specific scripts (they `should` match).

==Color with emacs==

To get `emacs` (such as with `M-x shell') to handle color escapes, add
to your F<.emacs> or other init file:

    (add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)


=Options=

* ''--all''

Show all of stdin in the `colorname`.
With `--all`, you can specify multiple colornames to alternate, or
specify the predefined patterns 'usa', 'christmas', 'italy', or 'rainbow'.

* ''--help-ls''

Show the reserved file-type-names that can be used to set file
colors for the *nix `ls` command, based on
file ''types'' (rather than filename-expressions).
These names can be used in the `LS_COLORS` environment variable.
For example, 'ex' can be used to set the color for executable files.

* ''--list''

Show all known combination of colors and effects.
Most terminal programs do not support all effects.
See also `--breakLines`, `--table`, and `--xterm256`.

With `--xterm256` and `--breakLines`, a line will be shown for each color number
0...255, including a word shown in

  the foreground color on the default background,
  the foreground color on a white background,
  the background color with the default foreground,
  the background color with white foreground.

* ''--lscolorset'' `oldcolor` `newcolor`

(that's an el at the beginning, not one or eye)
Replace all the `LS_COLOR` mappings
for a given color, with a new color (see `--lslist` option for a description
of a typical default mapping).

* ''--lsget'' `fileExpr`

Figure out what color `ls` will use to
display a given file's name. If you give an expression such as '*.html' that's
ok, too.

* ''--lslist''

List how `ls` colors are set up, organized by color
(see also the `dircolors` command).
The two-letter codes before some descriptions below, are
the mnemonics `dircolors` uses to refer to various file classes (otherwise,
it assigns color by file extensions).
See `--lsset` for a slightly easier way to modify `dircolors`.

In general, the default settings are (on my system):

** Red:               Archives (tar, jar, zip, etc.)
** Green:             ex: Executables
** Blue:              di: Directories
** Magenta:           so, do: Pictures, video, sockets,...
** Cyan:              (Mac but not Ubuntu?):
Audio files (mp3, midi, flac, wav, etc.)
** Bold Cyan:         ln: Symbolic links
** Black/Red:         ca: Capability files
** Black/Yellow:      sg: SetGID files
** White/Red:         su: SetUID files
** White/Blue:        st: Dir with sticky bit set (+t), hard links
** Black/Green:       tw: Other sticky writable files
** Blue/Green:        ow: Other writable files
** Yellow/Black:      pi: Pipes
** Bold Yellow/black: bd, cd: Block and character device files
** Bold Red/Black:    or: Orphan files (e.g., broken symbolic links)

* ''--lsset'' `fileExpr`

Return a modified `ls` color setup that assigns a
named color to files that match the given `fileExpr` (the color name will
be translated to a numeric code).

The `fileExpr` can be a glob (usually of
the form '*.ext' to distinguish files by their extensions), or a 2-letter
reserved code to distinguish files by some property (see above);
see also `--help-ls`.
If there is already an assignment for exactly
the given `fileExpr`, it will be replaced. For example:

The caller should store this in environment variable `LS_COLORS`), e.g.:

    export LS_COLORS=`colorstring --lsset di red`

=back


=Known bugs and limitations=

Not yet as thoroughly tested as the Perl predecessor.

You can't set more than one effect (such as blink, bold, inverse, hidden,
and underline) at once.

The color-name lookup used with the `--lslist` option can't handle
simultaneous property, foreground, and background settings unless the
environment variable
`LS_COLORS` specifies them in increasing numeric order (which seems typical).
For now, such unmatched entries print the color name as '?'.

`TERM=xterm-256color' is not supported except for `--list` via `--xterm256`.

Does not have avoid low-contrast pairs, particularly
in relation to the default terminal background color (which is hard to
determine in the first place, though see the `xtermcontrol`, `tput`,
and my `getBGColor` command.

Not entirely in sync with related commands.


=Related commands:=

`sjdUtils.pm` -- provides colorized messages, and functions to get the same
kinds of escapes as here
(`sjdUtils.pm` does not use the `colorstring` command).

`sjdUtils.py` -- Python version of `sjdUtils.pm`.

`alogging.py`, `colorstring` (Perl), `hilite` (Perl).

`colorNames.md` -- documentation about color names and usage.


==Related *nix utilities==

Several *nix commands have a `--color=auto' option: `ls`, `grep`, etc.

`dircolors` can be used to set up the colors used by `ls`
(see also `--lslist` and `--lsset`, above).

`grc` and `logtool` can colorize log files.

`info terminfo` has more information about terminal colors.
terminfo fields can be obtained via the `tput` command.
`terminfo2xml` collects it all and displays it, in XML or tabular form.

`tput colors` tells you various terminal control sequences, and the
current values of the corresponding settings. For example, these:
    tput bold | od
    tput setaf 4 | od

give these:
    0000000    1b  5b  31  6d
             033   [   1   m
    0000000    1b  5b  33  34  6d
             033   [   3   4   m

which are:
    ESC [ 1 m
    ESC [ 3 4 m

`locale charmap` tells what character encoding you're set for.

`colortest` displays a terminal color chart (`apt-get`).

`colorama` provides similar output-coloring features (L<pypi>).

To determine an `xterm`'s background color, see
L<http://stackoverflow.com/questions/2507337/>. One way to get it is:

    \\e]11;?\\a

Xterm-compatible terminals should reply with the same sequence, with "?"
replaced by an X11 colorspec, e.g., rgb:0000/0000/0000 for black.


=References=

[http://http://push.cx/2008/256-color-xterms-in-ubuntu]


=History=

* Written <2006-10-04, Steven J. DeRose.
* 2008-02-11 sjd: Add `--perl`, `perl -w`.
* 2008-09-03 sjd: BSD. Improve doc, error-checking, fix bug in `-all`.
* 2010-03-28 sjd: perldoc. Add `\\[\\]` to `-ps`.
* 2010-09-20ff sjd: Cleanup. Add `--color`; `ls` and `dircolors` support.
Simplify numeric handling of codes. Support color combinations. Add `-setenv`.
Change 'fg2_' prefix to 'bold_' and factor out of code.
* 2013-06-11: Add `--xterm256`, but just for `--list`.
* 2013-06-27: Add `--table`. Ditch `fg2_` and `b_` prefixes.
* 2014-07-09: Clean up doc. Add `--python`. Clean up `--perl`. fix `--list`.
* 2015-02-04: Support rest of effects beyond bold.
* 2015-08-25: Start syncing color-refs with `sjdUtils.pm`.
* 2016-01-01: Get rid of extraneous final newline with `-m`.
* 2016-07-21: Merge doc on color names w/ sjdUtils.p[my], etc.
* 2016-10-25: Clean up to integrate w/ ColorManager. Change names.
Debug new (hashless) way of doing colors.
* ''2018-08-29: Port to Python.'' Math alphabet stuff to `mathAlphanumerics.py`.
Switch to depend on ColorManager.py. Reconcile names, no more `fg_` and `bg_`.
* 2018-10-22: Fix minor bugs. Refactor. Add `args.txt`, use `ColorManager` more.
* 2020-10-02: Move effects to end to sync with `colorNames.md`.


=To do=

* Make it just issue the command-line args if present.
* Add alternate setup to tag stuff with HTML instead.
* Consider integrating with mappings from `mathAlphanumerics.py`.
* Offer alternate color sets for `setenv` for light vs. dark backgrounds.
* `lsset` should support replacing all mappings for a given color.
* Use `rgb.txt` with xterm-256color to pick by name?
* Colorize by fields using `TabularFormats` package?

* Expand the test/sample feature (and maybe general support?) to cover
other ANSI esacpes, such as:
** Double-Height Letters
** Single/Double width line
** Privacy message
** Alternate character sets a la ISO 2022.


=Rights=

Copyright 2006-10-04 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
For further information on this license, see
[https://creativecommons.org/licenses/by-sa/3.0].

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].
"""


# Define explanations for the non-file-glob cases used by LS_COLORS.
#
lsSpecials = {
    "bd" : "BLK                    Block device driver",
    "ca" : "CAPABILITY             File with capability",
    "cd" : "CHR                    Character device driver",
    "di" : "DIR                    Directories",
    "do" : "DOOR                   Door (eh?)",
    "ex" : "EXEC                   Executable files",
    "??" : "FILE                   Other file (normally not set)",
    "hl" : "HARDLINK               Hard link",
    "ln" : "LINK                   Symbolic link (can use 'target' color)",
    "or" : "ORPHAN                 Broken symbolic link, etc.",
    "ow" : "OTHER_WRITABLE         Other-writable, non-sticky file",
    "pi" : "FIFO                   Pipe",
    "rs" : "RESET                  Reset to default color",
    "sg" : "SETGID                 SetGID",
    "so" : "SOCK                   Socket?",
    "st" : "STICKY                 Directory with sticky bit set (+t)",
    "su" : "SETUID                 SetUID",
    "tw" : "STICKY_OTHER_WRITABLE  Sticky other writable file",
    }

boldToken = "bold"        # FIX
blinkToken = "blink"
inverseToken = "inverse"
ulToken = "ul"
esc = chr(27)

# Table of basic color names. +30 for foreground, +40 for background
atomicColors = cm.colorNumbers
if (len(atomicColors) != 9):
    raise ValueError("Bad color table from ColorManager!")

effectsOn = cm.effectNumbers

colorTable = {}      # Map from named colors to codes (switch to just use ColorManager)
lsColors = []

def cseq(name):
    return cm.getColorString(name)


###############################################################################
#
def colorizeString(msg, fg, bg=""):
    colorName = fg
    if (bg): colorName += "/" + bg
    return cm.colorize(colorName, msg)

def colorSeq(name):
    if (isinstance(name, list)):
        lg.eMsg(0, "Multi-color not yet supported")
        name = name[0]
    try:
        cs = cm.getColorString(name)
    except TypeError as e:
        lg.eMsg(0, "Error in ColorManager: %s" % (e))
        cs = ""
    return cs


###############################################################################
# Take an n;m... string as used in environment variable LS_COLORS,
# and try to look up what it means.
# Normalizes to increasing (numeric) order.
#
def getColorName(code):   ### OBSOLETE, FIX
    code = re.sub(r'0+(\d)', "\\1", code)  # Strip any leading zeros
    code2 = ';;'.join(sorted(re.split(';', code)))
    lg.vMsg(1, "normalized order: '%s' -> '%s'" % (str(code), str(code2)))

    code = code2
    code = "[" + code + "m"
    for k in (colorTable):
        if (colorSeq(k) == code): return(k)

    lg.vMsg(1, "Couldn't find '" + code + "' in color table.\n")
    return("?")


###############################################################################
#
def setupDircolors():
    """'dircolors' is a Linux /GNU corutils command that helps set bash colors
    for the ls command, via environment variable 'LS_COLORS'.
    It is not typically available on BSD/MacOSX.
    """
    global lsColors
    try:
        lsColors =  re.split(r':', check_output('dircolors'))
    except Exception as e:
        sys.stderr.write(
            "'dircolors' failed. Only available on Linux:\n    %s" % (e))

    lsColors[0] = re.sub(r'LS_COLORS=', '', lsColors[0])
    lsColors.pop()  # "export LS_COLORS"
    lsColors[-1] = re.sub(r';;', '', lsColors[-1])


###############################################################################
#
def processOptions():
    try:
        from BlockFormatter import BlockFormatter
        parser = argparse.ArgumentParser(
            description=descr, formatter_class=BlockFormatter)
    except ImportError:
        parser = argparse.ArgumentParser(description=descr)

    parser.add_argument("--all",            action='store_true',
        help="Show all of stdin in the 'colorname'.")
    parser.add_argument("--breakLines",		action='store_true',
        help="With `--list`, put each example on a separate line.")
    parser.add_argument("--color",			action='store_true',
        help="Use color in our own output.")
    parser.add_argument("--effects",		action='store_true',
        help="Show sample of each effect, to see if your terminal supports it.")
    parser.add_argument("--envPrefix",      type=str, default="COLORSTRING",
        help="Prefix to name env variables for color names with --setenv.")
    parser.add_argument("--helpls", "--help-ls", action='store_true',
        help="Show the file-type-names to set file colors for the 'ls' command")
    parser.add_argument("--list",           action='store_true',
        help="Show all known combination of colors and effects.")
    parser.add_argument("--lscolorset",     type=str,
        help="Replace all `LS_COLOR` mappings for a given color, with a new color")
    parser.add_argument("--lsget",          type=str, default="",
        help="""Find what color `ls` will use to display file names.
Provide a sample filename to specify a category (see 'man ls', or the -h here).
This requires the 'dirColors' command, which may be Linix-only.""")
    parser.add_argument("--lslist",			action='store_true',
        help="List how `ls` colors are set up, organized by color.")
    parser.add_argument("--lsset",          type=str, default="",
        help="Return a modified `ls` color setup (see above).")
    parser.add_argument("--msg", "--message", type=str, default="",
        help="Send this as a message to stdout in the specified color.")
    parser.add_argument("--perl",			action='store_true',
        help="Return Perl code to generate and assign the color string.")
    parser.add_argument("--python",			action='store_true',
        help="Return Python code to generate and assign the color string.")
    parser.add_argument("--printStuff",		action='store_true',
        help="Print out the color string requested.")
    parser.add_argument("--ps", "--bash",	action='store_true',
        help="Return a color command in the form for a Bash prompt string.")
    parser.add_argument(
        "--quiet", "-q",                    action='store_true',
        help='Suppress most messages.')
    parser.add_argument("--sampleText",     type=str, default="Sampler",
        help="Set the text to be displayed with --table. Default: 'Sampler'.")
    parser.add_argument("--setenv", "--envset", action='store_true',
        help="""Returns a (long) string you can
use to set a lot of environment variables, to hold the required escapes to
set given colors. The variable names are 'COLORSTRING_' plus the color names
you can give to this script (but you can change the prefix using `--envPrefix`.""")
    parser.add_argument("--table",			action='store_true',
        help="""Show the main color combinations as a table. This only includes the "plain"
and "bold" effects, but shows all foreground/background combinations, along
with the color names and numbers.
See also `--breakLines`, `--list`, `--sampleText`, `-v`, and `--xterm256`""")
    parser.add_argument(
        "--verbose", "-v",                  action='count', default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')
    parser.add_argument("--warn", "-w",     type=str, default="",
        help="Send this as a message to stderr in the specified color.")
    parser.add_argument("--xterm256",			action='store_true',
        help="Enable the 256-color set supported by TERM=xterm-256color.")

    parser.add_argument(
        'colors', type=str, nargs='?', default=None,
        help='Color name to use. For multiple (alternating), quote the list.')

    parser.add_argument('txt', nargs=argparse.REMAINDER)

    args0 = parser.parse_args()
    if (args0.color is None and ('USE_COLOR' in os.environ)): args0.color = True
    if (args0.colors):
        args0.colors = re.split(r'\s+', args0.colors.strip())
    else:
        args0.colors = 'blue'
    if (args0.verbose): lg.setVerbose(args0.verbose)
    return(args0)


###############################################################################
# For '--xterm56' (unfinished):
#     FG codes: '\e38;5;nm' for `n` from 0 to at least 255.
#     BG codes: '\e48;5;nm'.
#
def showTable():
    rowHeadWidth = 12
    slen = len(args.sampleText)
    for effect in range(0,2):
        if (effect): label = "Bold"
        else: label = "Plain"
        print("\nTable of %s foreground colors on all backgrounds:" % (label))

        # Make table header row
        thead1 = thead2 = " " * (rowHeadWidth + 4)
        for cname, cnum in (atomicColors.items()):
            thead1 += cname.ljust(slen+1)
            thead2 += str(cnum+40).ljust(slen+1)
        print(thead1 + "\n" + thead2)

        # Make a row per (fg) color
        for fgname, fgnum in (atomicColors.items()):
            buf = "%2d: %-12s" % (fgnum, fgname)
            #if (effect and effect!='Plain'): fullName = effect + "/" + fgname
            #else: fullName = fgname
            for bgname in (atomicColors.keys()):
                buf += colorizeString(args.sampleText, fgname, bgname) + " "
            print(buf)
    return

def showList():
    if (args.breakLines): nl = "\n"
    else: nl = " "
    ctable = cm.getColorStrings()
    n = 0
    for ct in (sorted(ctable.keys())):
        print(ctable[ct] + ct + cseq('default'), end=nl)
        n += 1
    print("\nDone, %d combinations." % (n))

# TODO: Use ColorManager.
#
def setupEffects():
    shortMap = {
        "black"	    : "blk",
        "red"	    : "red",
        "green"	    : "grn",
        "yellow"	: "yel",
        "blue"	    : "blu",
        "magenta"	: "mag",
        "cyan"  	: "cyn",
        "white"	    : "wht",
    }
    effects = sorted(effectsOn.keys())
    for e in range(len(effects)):
        print("")
        print("******* Colors with " + (effects[e] or "no") + " effects:")

        if (effects[e] != "plain"):
            eff = effects[e] + "_"
        else:
            eff = ""
        for fg in (atomicColors):
            buf0 = ""
            for bg in (atomicColors):
                sample = ' ' + shortMap[fg] + "/" + shortMap[bg] + ' '
                key = eff + fg
                if (args.breakLines): sep = "\n"
                else: sep = " "
                buf0 += colorizeString(sample, key, bg) + sep
            print(buf0)

        print("")

def helpLSColors():
    print("The LS_COLORS keys are (see also dircolors --print-database):")
    lssp = sorted(lsSpecials.keys())
    for sp in (lssp):
        print("    sp\t" + lsSpecials[sp])
    sys.exit()

def doLsList():
    """Display a list of all the LS_COLORS settings.
    """
    setupDircolors()
    byColor = {}
    for lsc in (lsColors):
        mat = re.search(r'^(.*)=(.*)', lsc)
        #expr = mat.group(1)
        colorCode = mat.group(2)
        if (not None ==  byColor[colorCode]):
            byColor[colorCode] = ""
        byColor[colorCode] += "expr "

    print("Colors for 'ls':")
    coff = cm.getColorString('default')
    for code in (sorted(byColor.keys())):
        name = getColorName(code)
        if (colorSeq(name) is None): con2 = ""
        else: con2 = esc + colorSeq(name)
        print("%s%s (%s):%s %s" % (con2, code, name, coff, byColor[code]))

def doLsGet(what):
    setupDircolors()
    found = 0
    coff = cm.getColorString('default')
    for lsc in (lsColors):
        if (re.match(what, lsc)):
            found += 1
            code = lsc = re.sub(r'^.*=', '', lsc)
            name = getColorName(code)
            if (colorSeq(name) is None): con2 = ""
            else: con2 = esc + colorSeq(name)
            print("%s\t%s (%s%s%s)" % (lsc, code, con2, name, coff))
    if (not (found>0)):
        print("No LS_COLORS mapping found for '%s'." % (what))


def try256():
    end = esc + "[0m"
    print("\n******* Foreground and Background xterm256 colors:")
    for i in range(256):
        e1 = esc + "[38;5;%dm (fg sample) %s\t" % (i, end)
        e2 = esc + "[38;5;%dm %c[47m (fg sample) %s\t" % (i, esc, end)
        e3 = esc + "[48;5;%dm (bg sample) %s\t" % (i, end)
        e4 = esc + "[48;5;%dm %c[37m (bg sample) %s\t" % (i, esc, end)
        nl = ""
        if (args.breakLines): nl = "\n"
        print("i: " + nl + e1 + e2 + e3 + e4)
    print("")

def showEffectSamples():
    for e in (sorted(effectsOn.keys())):
        print("%-30s '%s'" % (e, colorizeString(e, args.sampleText)))

def colorizeStdin():
    reset = colorSeq("default")
    bg_reset = colorSeq("/default")
    clist = []
    for colorName in (args.colors):
        if (colorName == "usa"):
            clist.append(cseq("red/bold"))
            clist.append(cseq("white/bold"))
            clist.append(cseq("blue/bold"))

        elif (colorName == "christmas"):
            clist.append(cseq("red/bold"))
            clist.append(cseq("green/bold"))

        elif (colorName == "italy"):
            clist.append(cseq("red/bold"))
            clist.append(cseq("green/bold"))
            clist.append(cseq("white/bold"))

        elif (colorName == "rainbow"):
            clist.append(cseq("red/bold"))
            clist.append(cseq("red"))
            clist.append(cseq("yellow/bold"))
            clist.append(cseq("green/bold"))
            clist.append(cseq("blue/bold"))
            clist.append(cseq("magenta/bold"))
            clist.append(cseq("magenta"))

        else:
            seq0 = colorSeq(colorName)
            if (not seq0):
                print("colorstring: Unknown color '%s'." % (colorName))
                print("Known: %s" % (" ".join(cm.colorStrings.keys())))
                sys.exit(0)
            clist.append(seq0)

    #warn "Color sequence: " + (" ".join(clist)) + "\n"

    n = 0
    for rec in sys.stdin.readlines():
        rec = rec.strip()
        print(esc + clist[n] + rec
            + esc + reset
            + esc + bg_reset + "\n")
        n += 1
        if (n >= len(clist)):
            n = 0
    return

def outConvert(s):
    """Convert to the desired output syntax.
    """
    if (args.lsset != ""):
        if (args.verbose):
            sys.stderr.write("Attempting --lsset for expr '%s'." % (args.lsset))
        orig = os.environ["LS_COLORS"]
        new = orig = re.sub(r'lsset=.*?(:|$)', '', orig)
        new = re.sub(r':+$', '', new)
        s = re.sub(r'^\[', '', s)
        s = re.sub(r'm$', '', s)
        s = "new:lsset=" + s

    elif (args.lscolorset):
        if (args.verbose):
            sys.stderr.write("Attempting --lscolorset for color '" +
                args.lscolorset + "'.\n")
        s = re.sub(r'^\[', '', s)
        s = re.sub(r'm$', '', s)
        orig = os.environ["LS_COLORS"]
        new = orig
        new = re.sub(r'=lscolorset(:|$)', '='+s, new)
        if (not (args.quiet)):
            sys.stderr.write("Changing n LS_COLOR mappings to new color.\n")
        new = re.sub(r':+$', '', new)
        s = new

    elif (args.ps):
        s = "\\[\\e" + s + "\\]\n"

    elif (args.perl):
        s = "   \\colors[\"colorName\"] = \"\\e" + s + "\n"

    elif (args.python):
        s = "   colors[colorName] = u\"\\x1B\"" + s + "\n"

    elif (args.printStuff):
        s = "   ESC " + s + "\n"

    elif (args.txt or args.warn):
        s1 = esc + s
        s3 = esc + cseq("default") + "\n"
        s = s1 + args.msg + s3
        if (args.warn):
            sys.stderr.write(s1 + args.warn + s3 + "\n")
        if (not args.msg):
            sys.exit()

    else:
        s = esc + s
    return s


###############################################################################
# Main
#
args = processOptions()
color0 = args.colors[0]

#setupEffects()

if (args.xterm256 and os.environ['TERM'] != "xterm256color"):
    print("You set --xterm256, but TERM is '%s'." % (os.environ['TERM']))

if (args.table):
    showTable()
elif (args.list):
    showList()
elif (args.helpls):
    helpLSColors()
elif (args.xterm256):
    try256()
elif (args.effects):
    showEffectSamples()
elif (args.lslist):
    doLsList()
elif (args.lsget != ""):
    doLsGet(args.lsget)
elif (args.setenv):
    # You can't easily set the relevant environment from Perl, since it's
    # owned by the parent process. So return a big string the caller can use....
    lsbuf = ""
    for cc in (colorTable):
        seq = re.sub(r'\[', '', colorSeq(cc))
        seq = re.sub(r'm$', '', seq)
        lsbuf += args.envPrefix + "_c='" + seq + "'"
    print(lsbuf)
elif (not args.colors):
    # Remaining commands require that a color be specified.
    sys.stderr.write("No color(s) specified.\n")
elif (args.all):
    # For '--all', copy stdin coloring each line.
    # Support a list of colors to alternate among.
    print("all: %s." % (all))
    colorizeStdin()
elif (args.warn):
    sys.stderr.write(cm.colorize(color0, args.warn + "\n"))
elif (args.msg):
    print(cm.colorize(color0, args.msg))
elif (args.txt):
    print(cm.colorize(color0, " ".join(args.txt)))
else:
    lg.vMsg(1, "No special options, so expecting a color name.")
    cName =  args.colors
    escString = colorSeq(cName)
    if (not escString):
        print("colorstring: Unknown color key '%s'. Use -h for help." % (cName))
        sys.exit(0)
    escString = outConvert(escString)
    print(escString, end="")

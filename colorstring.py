#!/usr/bin/env python
#
# 2018-08-29: Converted by perl2python, by Steven J. DeRose.
#
# Usage examples:
#    PS1=`colorstring -ps Cyan` Hello, `colorstring -ps green`"world ==>"
#    colorstring --list
#
# Written <2006-10-04, Steven J. DeRose.
# 2008-02-11 sjd: Add --perl, perl -w.
# 2008-09-03 sjd: BSD. Improve doc, error-checking, fix bug in -all.
# 2010-03-28 sjd: perldoc. Add \[\] to -ps.
# 2010-09-20ff sjd: Cleanup. Add --color; ls and dircolors support. Simplify
#     numeric handling of codes. Support color combinations. Add -setenv.
#     Change 'fg2_' prefix to 'bold_' and factor out of code.
# 2013-06-11: Add --xterm256, but just for --list.
# 2013-06-27: Add --table. Ditch "fg2_" and "b_" prefixes.
# 2014-07-09: Clean up doc. Add --python. Clean up --perl. fix --list.
# 2015-02-04: Support rest of effects beyond bold.
# 2015-08-25: Start syncing color-refs with sjdUtils.pm.
# 2016-01-01: Get rid of extraneous final newline with -m.
# 2016-07-21: Merge doc on color names w/ sjdUtils.p[my], etc.
# 2016-10-25: Clean up to integrate w/ ColorManager. Change names.
#     Debug new (hashless) way of doing colors.
# ####### 2018-08-29: Port to Python. Math alphabet stuff to mathUnicode.py.
#     Switch to depend on ColorManager.py. Reconcile names, no more fg_ and bg_.
# 2018-10-22: Fix minor bugs. Refactor. Add args.txt, use ColorManager more.
#
# To do:
#     Make it just issue the commandline args if present.
#     Add alternate setup to tag stuff with HTML instead.
#     Use the ColorManager class from sjdUtils.pl!
#     Consider mappings to special Unicode alphabets (cf SimplifyUnicode)
#         51:framed; 52:encircled; (enclosed alphanumerics U+2460-U+24FF)
#             (a) U+249C; circled A U+24B6; circled a U+24D0
#         53:overlined (combining overline = U+0305)
#         combining underline U+0332
#     Offer alternate color sets for setenv, for light vs. dark backgrounds.
#     lsset should support replacing all mappings for a given color.
#     Use rgb.txt with xterm-256color to pick by name?
#     Colorize by fields using TabularFormats package?
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

__version__ = "2018-10-22"

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
###############################################################################
#
def colorizeString(msg, fg, bg=""):
    colorName = fg
    if (bg): colorName += "/" + bg
    return cm.colorize(colorName, msg)

def colorSeq(name):
    if (isinstance(name, list)):
        lg.eMsg("Multi-color not yet supported")
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
    global lsColors
    lsColors =  re.split(r':', check_output('dircolors'))
    lsColors[0] = re.sub(r'LS_COLORS=', '', lsColors[0])
    lsColors.pop()  # "export LS_COLORS"
    lsColors[-1] = re.sub(r';;', '', lsColors[-1])


###############################################################################
#
def processOptions():
    descr = """
=pod

=head1 Usage

colorstring [options] colorname [text]

Returns the escape sequence needed to switch an ANSI terminal to a given
foreground color, background color, and/or text effect, given a color name
as supported by C<ColorManager.py>.

Such sequences can be gotten
in various forms as needed for use in bash scripts, bash prompt-strings,
Perl code, etc. (see options).

This script can also:

=over

=item * display lists of colors (I<--list>, I<--table>);

=item * colorize STDIN (I<--all>), messages (I<-m>), or warnings (I<-w>); or

=item * interact with the *nix C<lscolors> command
(I<--lscolorset>, I<--lsget>, I<--lslist>, and I<--lsset>).

=back

=head2 Color with emacs

To get C<emacs> (such as with I<M-x shell>) to handle color escapes, add
to your F<.emacs> or other init file:

    (add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)

=head2 Color names used

The color names available are defined in F<bingit/SHELL/colorNames.pod>,
which supercedes anything in specific scripts (they I<should> match).


=head1 Option details

=over

=item * B<--all>

Show all of stdin in the I<colorname>.
With I<--all>, you can specify multiple colornames to alternate, or
specify the predefined patterns 'usa', 'christmas', 'italy', or 'rainbow'.

=item * B<--help-ls>

Show the reserved file-type-names that can be used to set file
colors for the *nix C<ls> command, based on
file B<types> (rather than filename-expressions).
These names can be used in the C<LS_COLORS> environment variable.
For example, 'ex' can be used to set the color for executable files.

=item * B<--list>

Show all known combination of colors and effects.
Most terminal programs do not support all effects.
See also I<--breakLines>, I<--table>, and I<--xterm256>.

With I<--xterm256> and I<--breakLines>, a line will be shown for each color number
0...255, including a word shown in

  the foreground color on the default background,
  the foreground color on a white background,
  the background color with the default foreground,
  the background color with white foreground.

=item * B<--lscolorset> I<oldcolor> I<newcolor>

(that's an el at the beginning, not one or eye)
Replace all the C<LS_COLOR> mappings
for a given color, with a new color (see I<--lslist> option for a description
of a typical default mapping).

=item * B<--lsget> I<fileExpr>

Figure out what color C<ls> will use to
display a given file's name. If you give an expression such as '*.html' that's
ok, too.

=item * B<--lslist>

List how C<ls> colors are set up, organized by color
(see also the C<dircolors> command).
The two-letter codes before some descriptions below, are
the mnemonics C<dircolors> uses to refer to various file classes (otherwise,
it assigns color by file extensions).
See I<--lsset> for a slightly easier way to modify I<dircolors>.

In general, the default settings are (on my system):

=over

=item * Red:               Archives (tar, jar, zip, etc.)

=item * Green:             ex: Executables

=item * Blue:              di: Directories

=item * Magenta:           so, do: Pictures, video, sockets,...

=item * Cyan:              (Mac but not Ubuntu?):
Audio files (mp3, midi, flac, wav, etc.)

=item * Bold Cyan:         ln: Symbolic links

=item * Black/Red:         ca: Capability files

=item * Black/Yellow:      sg: SetGID files

=item * White/Red:         su: SetUID files

=item * White/Blue:        st: Dir with sticky bit set (+t), hard links

=item * Black/Green:       tw: Other sticky writable files

=item * Blue/Green:        ow: Other writable files

=item * Yellow/Black:      pi: Pipes

=item * Bold Yellow/black: bd, cd: Block and character device files

=item * Bold Red/Black:    or: Orphan files (e.g., broken symbolic links)

=back


=item * B<--lsset> I<fileExpr>

Return a modified C<ls> color setup that assigns a
named color to files that match the given I<fileExpr> (the color name will
be translated to a numeric code).

The I<fileExpr> can be a glob (usually of
the form '*.ext' to distinguish files by their extensions), or a 2-letter
reserved code to distinguish files by some property (see above);
see also I<--help-ls>.
If there is already an assignment for exactly
the given I<fileExpr>, it will be replaced. For example:

The caller should store this in environment variable C<LS_COLORS>), e.g.:

    export LS_COLORS=`colorstring --lsset di red`

=back


=head1 Known bugs and limitations

Not as thoroughly tested yet, as the Perl predecessor.

You can't set more than one of blink, bold, inverse, hidden, and ul at once.

The color-name lookup used with the I<--lslist> option can't handle
simultaneous property, foreground, and background settings unless the
environment variable
C<LS_COLORS> specifies them in increasing numeric order (which seems typical).
For now, such unmatched entries print the color name as '?'.

I<TERM=xterm-256color> is not supported except for I<--list> via I<--xterm256>.

Does not have a way to avoid low-contrast pairs, particularly
in relation to the default terminal background color (which is hard to
determine in the first place, though see the C<xtermcontrol>, C<tput>,
and my C<getBGColor> command.

Is not entirely in sync with related commands.


=head1 Related commands:

C<sjdUtils.pm> -- provides colorized messages, and functions to get the same
kinds of escapes as here
(C<sjdUtils.pm> does not use the C<colorstring> command).

C<sjdUtils.py> -- Python version of C<sjdUtils.pm>.

C<alogging.py>, C<colorstring> (Perl), C<hilite> (Perl).

C<colorNames.pod> -- documentation about color names and usage.


=head2 Related *nix utilities

Several *nix commands have a I<--color=auto> option: C<ls>, C<grep>, etc.

C<dircolors> can be used to set up the colors used by C<ls>
(see also I<--lslist> and I<--lsset>, above).

C<grc> and C<logtool> can colorize log files.

C<info terminfo> has more information about terminal colors.
terminfo fields can be obtained via the C<tput> command.
C<terminfo2xml> collects it all and displays it, in XML or tabular form.

C<tput colors> tells you various terminal control sequences, and the
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

C<locale charmap> tells what character encoding you're set for.

C<colortest> displays a terminal color chart (C<apt-get>).

C<colorama> provides similar output-coloring features (L<pypi>).

To determine an C<xterm>'s background color, see
L<http://stackoverflow.com/questions/2507337/>. One way to get it is:

    \\e]11;?\a

Xterm-compatible terminals should reply with the same sequence, with "?"
replaced by an X11 colorspec, e.g., rgb:0000/0000/0000 for black.


=head1 References

L<http://http://push.cx/2008/256-color-xterms-in-ubuntu>


=head1 Ownership

This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see L<http://creativecommons.org/licenses/by-sa/3.0/>.

For the most recent version, see L<http://www.derose.net/steve/utilities/>.
"""

    try:
        from MarkupHelpFormatter import MarkupHelpFormatter
        formatter = MarkupHelpFormatter
    except ImportError:
        formatter = None
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=formatter)

    parser.add_argument("--all",            action='store_true',
        help="Show all of stdin in the 'colorname'.")
    parser.add_argument("--breakLines",		action='store_true',
        help="With I<--list>, put each example on a separate line.")
    parser.add_argument("--color",			action='store_true',
        help="Use color in our own output.")
    parser.add_argument("--effects",		action='store_true',
        help="Show a sample of each effect, to see if your terminal supports it.")
    parser.add_argument("--envPrefix",      type=str, default="COLORSTRING",
        help="Prefix for color names, to make env variable names  with --setenv.")
    parser.add_argument("--helpls", "--help-ls", action='store_true',
        help="Show the file-type-names to set file colors for the 'ls' command")
    parser.add_argument("--list",           action='store_true',
        help="Show all known combination of colors and effects.")
    parser.add_argument("--lscolorset",     type=str,
        help="Replace all the C<LS_COLOR> mappings for a given color, with a new color")
    parser.add_argument("--lsget",          type=str, default="",
        help="Figure out what color C<ls> will use to display a given file's name.")
    parser.add_argument("--lslist",			action='store_true',
        help="List how C<ls> colors are set up, organized by color.")
    parser.add_argument("--lsset",          type=str, default="",
        help="Return a modified C<ls> color setup (see above).")
    parser.add_argument("--msg", "--message", type=str, default="",
        help="Send this as a message to stdout in the specified color.")
    parser.add_argument("--perl",			action='store_true',
        help="Return Perl code to generate and assign the color string.")
    parser.add_argument("--python",			action='store_true',
        help="Return Python code to generate and assign the color string.")
    parser.add_argument("--printStuff",		action='store_true',
        help="Print out the color string requested.")
    parser.add_argument("--ps", "--bash",	action='store_true',
        help="Return a color command with '\\e' (ESC) to put in a Bash prompt string.")
    parser.add_argument(
        "--quiet", "-q",                    action='store_true',
        help='Suppress most messages.')
    parser.add_argument("--sampleText",     type=str, default="Sampler",
        help="Set the text to be displayed with --table. Default: 'Sampler'.")
    parser.add_argument("--setenv", "--envset", action='store_true',
        help="""Returns a (long) string you can
use to set a lot of environment variables, to hold the required escapes to
set given colors. The variable names are 'COLORSTRING_' plus the color names
you can give to this script (but you can change the prefix using I<--envPrefix>.""")
    parser.add_argument("--table",			action='store_true',
        help="""Show the main color combinations as a table. This only includes the "plain"
and "bold" effects, but shows all foreground/background combinations, along
with the color names and numbers.
See also I<--breakLines>, I<--list>, I<--sampleText>, I<-v>, and I<--xterm256>""")
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
###############################################################################
# For '--xterm56':
#     FG codes: '\e38;5;nm' for I<n> from 0 to at least 255.
#     BG codes: '\e48;5;nm'.
#
def showTable(bold=False):
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
            if (effect and effect!='Plain'): fullName = effect + "/" + fgname
            else: fullName = fgname
            for bgname, bgnum in (atomicColors.items()):
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

# Can this be gotten more easily from ColorManager?
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

def doLsGet():
    setupDircolors()
    found = 0
    coff = cm.getColorString('default')
    for lsc in (lsColors):
        lsc = ~ lsget
        if (lsc):
            found += 1
            code = lsc = re.sub(r'^.*=', '', lsc)
            name = getColorName(code)
            if (colorSeq(name) is None): con2 = ""
            else: con2 = esc + colorSeq(name)
            print("%s\t%s (%s%s%s)" % (lsc, code, con2, name, coff))
    if (not (found>0)):
        print("No LS_COLORS mapping found for '%s'." % (lsget))


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
            clist.append(cseq("bold/red"))
            clist.append(cseq("bold/default"))
            clist.append(cseq("bold/blue"))

        elif (colorName == "christmas"):
            clist.append(cseq("bold/red"))
            clist.append(cseq("bold/green"))

        elif (colorName == "italy"):
            clist.append(cseq("bold/red"))
            clist.append(cseq("bold/green"))
            clist.append(cseq("bold/default"))

        elif (colorName == "rainbow"):
            clist.append(cseq("bold/red"))
            clist.append(cseq("red"))
            clist.append(cseq("bold/yellow"))
            clist.append(cseq("bold/green"))
            clist.append(cseq("bold/blue"))
            clist.append(cseq("bold/magenta"))
            clist.append(cseq("magenta"))

        else:
            seq = colorSeq(colorName)
            if (not seq):
                print("colorstring: Unknown color '%s'." % (colorName))
                print("Known: %s" % (" ".join(cm.colorStrings.keys())))
                sys.exit(0)
            clist.append(seq)

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


def outConvert(escString):
    """Convert to the desired output syntax.
    """
    if (args.lsset != ""):
        if (args.verbose):
            sys.stderr.write("Attempting --lsset for expr '%s'." % (args.lsset))
        orig = os.environ["LS_COLORS"]
        new = orig = re.sub(r'lsset=.*?(:|$)', '', orig)
        new = re.sub(r':+$', '', new)
        escString = re.sub(r'^\[', '', escString)
        escString = re.sub(r'm$', '', escString)
        escString = "new:lsset=" + escString

    elif (args.lscolorset):
        if (args.verbose):
            sys.stderr.write("Attempting --lscolorset for color '" + args.lscolorset + "'.\n")
        escString = re.sub(r'^\[', '', escString)
        escString = re.sub(r'm$', '', escString)
        orig = os.environ["LS_COLORS"]
        new = orig
        n = new = re.sub(r'=lscolorset(:|$)', '='+escString, new)
        if (not (args.quiet)):
            sys.stderr.write("Changing n LS_COLOR mappings to new color.\n")
        new = re.sub(r':+$', '', new)
        escString = new

    elif (args.ps):
        escString = "\\[\\e" + escString + "\\]\n"

    elif (args.perl):
        escString = "   \\colors[\"colorName\"] = \"\\e" + escString + "\n"

    elif (args.python):
        escString = "   colors[colorName] = u\"\\x1B\"" + escString + "\n"

    elif (args.printStuff):
        escString = "   ESC " + escString + "\n"

    elif (args.txt or args.warn):
        s1 = esc + escString
        s3 = esc + cseq("default") + "\n"
        escString = s1 + args.msg + s3
        if (args.warn):
            sys.stderr.write(s1 + args.warn + s3 + "\n")
        if (not args.msg):
            sys.exit()

    else:
        escString = esc + escString
    return escString


###############################################################################
###############################################################################
# MAIN
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
    doLsGet()
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
    lg.vMsg(1, "In final else")
    cName =  args.colors
    escString = colorSeq(cName)
    if (not escString):
        print("colorstring: Unknown color key '%s'. Use -h for help." % (cName))
        sys.exit(0)
    escString = outConvert(escString)
    print(escString, end="")

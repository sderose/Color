#!/usr/bin/env less

=The ColorManager package color names=

The ColorManager package supplies ANSI terminal color services
to other code. This file describe the naming conventions it uses.

It is used by many of my utilities in both Perl and Python.
For example: sjdUtils.pm, sjdUtils.py, alogging.py, colorstring, hilite,
colorizeExpr, uncolorize, etc.).


==Color naming conventions==

The color names available are defined here.
This supercedes anything in specific scripts (they I<should> match).

The basic form of a "color name" is:

    foreground/background/effect1/effect2...

A name can stop after any number of the /-separated parts. For example,
'red' and 'blue/yellow' are fine. At present, my ColorManager packages
only support a single effect at a time.


===Basic colors===

The known basic color names are the usual ANSI terminal colors:

    "black"   : 0
    "red"     : 1
    "green"   : 2
    "yellow"  : 3
    "blue"    : 4
    "magenta" : 5
    "cyan"    : 6
    "white"   : 7
    "default" : 9


===Basic effects===

The known effect names are:

    "bold"       : 1   aka 'bright'
    "faint"      : 2
    "italic"     : 3   (rare)
    "underline"  : 4   aka 'ul'
    "blink"      : 5
    "fblink"     : 6?  aka 'fastblink' (rare)
    "reverse"    : 7   aka 'inverse'
    "concealed"  : 8   aka 'invisible' or 'hidden'
    "strike"     : 9   aka 'strikethru' or 'strikethrough'
    "plain"      : 0   (can be used to express "no special effect")

"blink" and "fblink" are suppressed if the environment variable B<NOBLINK>
is set.

Ideally, each effect could be turned on and off separately (so that any
combination would be possible), but for the moment only one effect is
supported at a time. To turn an effect on, use the name as listed;
to turn it off, use the name prefixed by "!", for example "!bold" to turn
off bold.
"bold" usually appears as a much brighter version of the color,
so is often used as if it provides additional colors.

Not all terminal programs support all effects (see section below).
You can check your terminal program color support with:

    colorstring --effects


===Non-basic colors===

A complete color name consists of:
    a foreground color F,
    a background color B, and
    an effect(s) E (possibly with leading "!" to negate it)

These are separated by "/". If leading components are omitted, their
following slash must still be present (so one can tell the difference
between foreground and background colors, which have the same names).

For example:
    red/blue
    yellow/black/italic
    /green/bold

Setting the foreground
and background colors the same is available, though unreadable.

Multiple simultaneous effects are not yet available; but if/when they are,
the additional effects will be expressed by subsequent "/"-separated tokens.

See my C<colorstring> command for some additional information; you can also
check the behavior of your terminal or terminal program with:

    colorstring --list

You can tell C<ColorManager> to include I<only> certain effects, by passing a
list of the desired effect name in the I<effects> parameter to the constructor.


==Effect support in some common terminal programs:==

* B<Terminal> (Mac OS X):  blink, bold, faint, inverse, invisible, ul
(not fblink, italic, or strike).

* B<xterm>: blink (but only when the window is focused),
bold, inverse, invisible, italic, strike, ul
(not faint, fblink).

* B<putty>: bold, inverse, ul
(not blink, faint, fblink, invisible, italic, or strike).

* B<gnone-terminal>: bold, faint, inverse, invisible, italic, strike, ul
(not blink or fblink).
Profiles have an "Allow bold text" setting.

* B<iterm2>:
bold (set to true bold or to bright),
italic (preference setting, but does not work for me,
blink (preference setting),
faint,
ul.

You can use C<colorstring> with the I<--effects> or I<--list> options
to check support by displaying samples.

I<--xterm256> is not yet supported. That, and/or color names from
the X F<rgb.txt> file, may be supported in the future.
See https://unix.stackexchange.com/questions/124407/ for details.


==The ANSI terminal escapes==

The basic commands are coded in the form:
    ESC [ n1;n2...m

where B<n1>, B<n2>, etc. are number:

Basic foreground color numbers:
    30 black  31 red      32 green  33 yellow
    34 blue   35 magenta  36 cyan   37 white

Basic background color numbers:
    40 black  41 red      42 green  43 yellow
    44 blue   45 magenta  46 cyan   47 white

Effects numbers:
    0 "plain"     reset all
    1 "bold"      bold
    2 "faint"     faint (rarely supported)
    3 "italic"    italic or inverse (rarely supported)
    4 "ul"        underline
    5 "blink"     blink
    6 "fblink"    fast blink (rarely supported)
    7 "inverse"   inverse
    8 "invisible" hidden (rarely supported)
    9 "strike"    strikethru (rarely supported)
   10...19        select font n (rarely supported)

Xterm adds controls to turn off some of these effects (I have not verified that
the list below is correct or how widely supported this is):
   22             bold off
   27             inverse off
   24             ul off
   25             blink off

Extended foreground (xterm256)
   38;5;n   (for color number 0..255)

Extended background (xterm256)
   48;5;n   (for color number 0..255)

Example: for bold red on cyan background:
    \e[1;31;46m


==Expressing escape strings==

It may be difficult or impossible to type such escape sequences by hand,
or to put a literal ESC character inside a string. C<colorstring> can provide
the escape sequence in various forms. For example, to get a color escape sequence
that you can paste directly into a C<bash> prompt string, use:

    colorstring --bash red

which will print C<\[\e[31m\]>.

==Rights==

This naming scheme is by Steven J. DeRose. I hereby dedicate it to the
public domain.


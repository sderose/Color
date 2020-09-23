#Color repo#

Utilities for dealing with ANSI color features on terminals.
These mainly just handle the basic set (8 colors), not xterm-256.

Many of my scripts support a --color option, which usually default to ON
if environment variable USE_COLOR is set, otherwise to OFF.

See: [http://github.com/sderose/Color].
See also: ../PYTHONLIBS/ColorManager.py

* `colorConvert.py` --

* `colorNames.md` -- Documentation of my conventional color names.
See colorNames.md or -h for individual commands for the details.
Briefly, you can specify up to
3 slash-separated tokens: an effect, a foreground color, a background color.
For example:

     yellow/black/bold

You can prefix an effect name with "!" to negate it (in case it was already on).
To specify background without specifying foreground, put a slash before it.

* `colorizeExpr` -- Takes a parenthesized/bracketed expression, and makes the various
scopes visible, by colorizing characters by how deeply they are nested, and by
displaying multiple lines underneath to show the layers of scope.

* `colorstring` -- Just forwards to colorstring.pm

* `colorstring.pm` -- Perl version of command-line colorizing facility. This includes
several options to help set up colors for *nix "ls" to use to identify
filetypes. Built atop ../PERLLIBS/ColorManager.pm.

* `colorstring.py` -- Not quite finished Python port of colorstring.pm.
Built atop ../PYTHONLIBS/ColorManager.py

* `findColorName` -- Searches rgb.txt (see also "xcolors" below) for the color
closest to a given RGB value (my Manhatten or Euclidean distance). Suggestions
for better but still simple distance measures are welcome.

* `getBGColor` -- Attempt to figure out what the current terminal program thinks
its background color is. This is supposedly supported via an xterm escape sequence,
but it does not seem to work on all terminals that claim to be "xterm"s.
See also http://stackoverflow.com/questions/2507337.

* `makeXColorChart` (Perl) -- Generates an HTML file that shows all the colors defined for X11
in the file (default /usr/X11/lib/X11/rgb.txt). Writes to stdout. See also "xcolors",
which attempts to find the file.

* `show256colors` (Python) -- Shows the effect of xterm-256 color requests from

* `uncolorize` (Python) -- A filter to remove ANSO color escapes from text, such as cleaning
up a saved console log that uses color you no longer want. This is also available
as a function in ColorManager.pm and ColorManager.py.

* `xcolors` (Perl) -- Try to locate the X Consortium color-list file "rgb.txt" on
your system and display it.


#SEE ALSO#

(these will be moving to here):

* [https://github.com/sderose/PERLLIBS/ColorManager.pm]
* [https://github.com/sderose/PYTHONLIBS/ColorManager.py]


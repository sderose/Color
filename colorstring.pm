#!/usr/bin/perl -w
#
# colorstring.pm: Support for ANSI terminal colors and effects.
# 2006-10: Written by Steven J. DeRose.
#
use strict;
use Getopt::Long;
use sjdUtils;
use alogging;
use ColorManager;

our %metadata = (
    'title'        => "colorstring.pm",
    'description'  => "Support for ANSI terminal colors and effects.",
    'rightsHolder' => "Steven J. DeRose",
    'creator'      => "http://viaf.org/viaf/50334488",
    'type'         => "http://purl.org/dc/dcmitype/Software",
    'language'     => "Perl 5.18",
    'created'      => "2006-10",
    'modified'     => "2020-11-20",
    'publisher'    => "http://github.com/sderose",
    'license'      => "https://creativecommons.org/licenses/by-sa/3.0/"
);
our $VERSION_DATE = $metadata{'modified'};


=pod

=head1 Usage

colorstring [options] colorname

Returns the escape string needed to switch an ANSI terminal to a given
foreground color, background color, and/or text effect, or displays something
in a given color.

The escape-strings can be gotten
in various forms as needed for use in bash scripts, bash prompt-strings,
Perl code, etc. (see options). For example:

    PS1=`colorstring -ps Cyan` "Hello"

This encloses the string (in this case "Hello") with the necessary stuff to
display it in Cyan (on the default background color).
I<-ps> instructs the script to format as needed to embed in
a bash prompt string (that affects how the escape character is expressed).

    colorstring -m green "Happy birthday"

You can also get color information, for example:

    colorstring --list

shows a table of available foreground and background colors and effects.
The naming conventions this package uses, are described in F<colorNames.md>.

# Usage examples:
#
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

The color names available are defined in F<bingit/SHELL/colorNames.md>,
which supercedes anything in specific scripts (they I<should> match).


=head1 Options

=over

=item * B<--all>

Show all of stdin in the I<colorname>.
With I<--all>, you can specify multiple colornames to alternate, or
specify the predefined patterns 'usa', 'christmas', 'italy', or 'rainbow'.

=item * B<--break>

With I<--list>, put each example on a separate line.

=item * B<--color>

Use color in our own output.

=item * B<--effects>

Just show a sample of each effect, to see if your terminal supports it.

=item * B<--envPrefix> I<s>

Specify what to prefix to color names to
make the environment variable names generated by I<--setenv> (q.v.).

=item * B<--help-keys>

Show the reserved file-type-names that can be used to set file
colors for the *nix C<ls> command, based on
file B<types> (rather than filename-expressions).
These names can be used in the C<LS_COLORS> environment variable.
For example, 'ex' can be used to set the color for executable files.

=item * B<--list>

Show all known combination of colors and effects.
Most terminal programs do not support all effects.
See also I<--break>, I<--table>, and I<--xterm256>.

With I<--xterm256> and I<--break>, a line will be shown for each color number
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
see also I<--help-keys>.
If there is already an assignment for exactly
the given I<fileExpr>, it will be replaced. For example:

The caller should store this in environment variable C<LS_COLORS>), e.g.:

    export LS_COLORS=`colorstring --lsset di red`

=item * B<-m> I<msg> OR B<--msg> OR C<--message>

Send I<msg> to stdout in the specified color.

=item * B<-w> I<msg> OR B<--warn>

Send I<msg> to stderr in the specified color.

=item * B<--perl>

Return Perl code to generate and assign the color string.

=item * B<--python>

Return Python code to generate and assign the color string.

=item * B<--print>

Print out the color string requested.

=item * B<--ps> OR B<--bash>

Return a color command with '\e' (ESC) to put in a Bash prompt string.

=item * B<-q> OR B<--quiet>

Suppress most messages.

=item * B<--sampleText> <string>

Set the text to be displayed with I<--table>. Default: "Sampler".

=item * B<--setenv>

Returns a (long) string you can
use to set a lot of environment variables, to hold the required escapes to
set given colors. The variable names are 'COLORSTRING_' plus the color names
you can give to this script (but you can change the prefix using I<--envPrefix>.

=item * B<--table>

Show the main color combinations as a table. This only includes the "plain"
and "bold" effects, but shows all foreground/background combinations, along
with the color names and numbers.
See also I<--break>, I<--list>, I<--sampleText>, I<-v>, and I<--xterm256>.

=item * B<-v> OR B<--verbose>

Add more messages. In particular, show a list of all color names (including
names for combinations of foreground, background, and/or effect), and the
control sequences they map to.

=item * B<--version>

Display version information and exit.

=item * B<--xterm256>

Enable the 256-color set supported by TERM=I<xterm-256color>.
At present, this is only useful with I<--list>.

=back


=head1 Known bugs and limitations

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

Is not entirely in sync with my related commands.


=head1 Related commands and files:

C<colorNames.md> -- documentation about color names and usage.

C<ColorManager.pm> -- provides the functionality used here.

C<ColorManager.py> -- same functionality as ColorManager.pm, but in Python.

C<sjdUtils.pm> -- provides colorized messages, and functions to get the same
kinds of escapes as here
(C<sjdUtils.pm> does not use the C<colorstring> command).

C<sjdUtils.py> -- Python version of C<sjdUtils.pm>.

C<alogging.py>, C<colorstring> (Perl), C<hilite> (Perl).

C<mathAlphanumerics.py> -- Unicode has many alternate forms of the Latin and Greek alphabets. See bin/data/unicodeLatinAlphabets.py for more information,
and PYTHONLIBS/mathAlphanumerics.py for support for transliterating into them.


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

    \e]11;?\a

Xterm-compatible terminals should reply with the same sequence, with "?"
replaced by an X11 colorspec, e.g., rgb:0000/0000/0000 for black.


=head1 References

L<http://http://push.cx/2008/256-color-xterms-in-ubuntu>


=head1 History

  Written <2006-10-04, Steven J. DeRose.
  2008-02-11 sjd: Add --perl, perl -w.
  2008-09-03 sjd: BSD. Improve doc, error-checking, fix bug in -all.
  2010-03-28 sjd: perldoc. Add \[\] to -ps.
  2010-09-20ff sjd: Cleanup. Add --color; ls and dircolors support. Simplify
numeric handling of codes. Support color combinations. Add -setenv.
Change 'fg2_' prefix to 'bold_' and factor out of code.
  2013-06-11: Add --xterm256, but just for --list.
  2013-06-27: Add --table. Ditch "fg2_" and "b_" prefixes.
  2014-07-09: Clean up doc. Add --python. Clean up --perl. fix --list.
  2015-02-04: Support rest of effects beyond bold.
  2015-08-25: Start syncing color-refs with sjdUtils.pm.
  2016-01-01: Get rid of extraneous final newline with -m.
  2016-07-21: Merge doc on color names w/ sjdUtils.p[my], etc.
  2016-10-25: Clean up to integrate w/ ColorManager. Change names.
Debug new (hashless) way of doing colors.
  2018-08-29: Ported to Python. *******
  2020-11-20: New layout.


=head1 To do

  Use the ColorManager.pm class!
    Update internals to use right naming conventions (a la colorNames.md), and
to not make a big unnecessary hash of all the possibilities.
  Add alternate setup to tag stuff with HTML instead.
  Offer alternate color sets for setenv, for light vs. dark backgrounds.
  lsset should support replacing all mappings for a given color.


=head1 Rights

Copyright 2006-10-04, 2018-08-29 by Steven J. DeRose.
This work is licensed under a
Creative Commons Attribution-Share Alike 3.0 Unported License.
For further information on this license, see
L<https://creativecommons.org/licenses/by-sa/3.0>.

For the most recent version, see L<http://www.derose.net/steve/utilities> or
L<https://github.com/sderose>.


=cut


###############################################################################
# Data
#
# Define explanations for the non-file-glob cases used by LS_COLORS.
#
my %lsSpecials = (
    "bd" => "BLK                    Block device driver",
    "ca" => "CAPABILITY             File with capability",
    "cd" => "CHR                    Character device driver",
    "di" => "DIR                    Directories",
    "do" => "DOOR                   Door (eh?)",
    "ex" => "EXEC                   Executable files",
    "??" => "FILE                   Other file (normally not set)",
    "hl" => "HARDLINK               Hard link",
    "ln" => "LINK                   Symbolic link (can use 'target' color)",
    "or" => "ORPHAN                 Broken symbolic link, etc.",
    "ow" => "OTHER_WRITABLE         Other-writable, non-sticky file",
    "pi" => "FIFO                   Pipe",
    "rs" => "RESET                  Reset to default color",
    "sg" => "SETGID                 SetGID",
    "so" => "SOCK                   Socket?",
    "st" => "STICKY                 Directory with sticky bit set (+t)",
    "su" => "SETUID                 SetUID",
    "tw" => "STICKY_OTHER_WRITABLE  Sticky other writable file",
    );

my @atomicColors = ();   # Table of basic color names.
my %effectsOn = ();      # Table of special effects (bold, etc)
my %colorTable = ();     # Map from named colors to codes.


###############################################################################
# Options
#
my $all        = 0;
my $break      = 0;
my $color      = $ENV{USE_COLOR} ? 1:0;
my $effects    = 0;
my $envPrefix  = "COLORSTRING";
my $list       = 0;
my $lsget      = "";
my $lslist     = 0;
my $lsset      = "";
my $lscolorset = "";
my $message    = "";
my $perl       = 0;
my $print      = 0;
my $python     = 0;
my $ps         = 0;
my $quiet      = 0;
my $sampleText = "Sampler";
my $setenv     = 0;
my $table      = 0;
my $verbose    = 0;
my $warnmsg    = "";
my $xterm256   = 0;

my $boldToken    = "bold";       # FIX
my $blinkToken   = "blink";
my $inverseToken = "inverse";
my $ulToken      = "ul";
my $esc = chr(27);


my %getoptHash = (
    "all"               => \$all,
    "break!"            => \$break,
    "color!"            => \$color,
    "effects!"          => \$effects,
    "h|help|?"          => sub { system "perldoc $0"; exit; },
    "help-keys"         => sub {
        print "The LS_COLORS keys are (see also dircolors --print-database):\n";
        for my $sp (sort keys %lsSpecials) {
            print "    $sp\t" . $lsSpecials{$sp} . "\n";
        }
    },
    "list"              => \$list,
    "lscolorset=s"      => \$lscolorset,
    "lsget=s"           => \$lsget,
    "lslist!"           => \$lslist,
    "lsset=s"           => \$lsset,
    "m|message|msg=s"   => \$message,
    "perl!"             => \$perl,
    "python!"           => \$python,
    "print"             => \$print,
    "ps|bash"           => \$ps,
    "q|quiet!"          => \$quiet,
    "sampleText=s"      => \$sampleText,
    "setenv|envset!"    => \$setenv,
    "table!"            => \$table,
    "v|verbose+"        => \$verbose,
    "version"           => sub {
        die "Version of $VERSION_DATE, by Steven J. DeRose.\n";
    },
    "w|warn=s"          => \$warnmsg,
    "xterm256!"         => \$xterm256,
    );
Getopt::Long::Configure ("ignore_case");
my $result = GetOptions(%getoptHash) || die "Bad options.\n";

warn "Remaining args after getopt: " . join(", ", @ARGV) . ".\n";

my $con = my $coff = "";
if ($color) {
    $con = $esc . "[1;34m"; # blue
    $coff = $esc . "[0;39m";
    #$coff = $esc . "[0;";
}

my @lsColors = ();
my $nSupported = `tput colors`;
chomp $nSupported;
if ($verbose) { warn "tput reports support for " . $nSupported . " colors.\n"; }

if ($xterm256 && $ENV{TERM} ne "xterm256color") {
    warn "You set --xterm256, but \$TERM is '$ENV{TERM}'\n";
}

if ($verbose) { warn "Calling setupColors...\n"; }
setupColors();


###############################################################################
# Check for and do various one-off options first.
# For '--list', show all the colors
# For '--xterm56':
#     FG codes: '\e38;5;nm' for I<n> from 0 to at least 255.
#     BG codes: '\e48;5;nm'.
#
if ($table) {
    my $labelWidth = 12;
    my $slen = length($sampleText);
    for my $bold (0,1) {
        print "\nTable of " . ($bold?"Bold":"Plain") . " foreground colors:\n";

        my $buf = " " x ($labelWidth + 4);
        my $nums = " " x ($labelWidth + 4);
        for my $head (@atomicColors) {
            $buf  .= " " . substr($head . (" " x 80), 0, $slen);
            (my $cnum = $colorTable{$head}) =~ s/\D//g;
            $cnum += 10;
            $nums .= " " . sjdUtils::rpad($cnum, $slen);
        }
        print "$buf\n$nums\n";

        for my $fg (@atomicColors) {
            (my $cnum = $colorTable{$fg}) =~ s/\D//g;
            my $fgg = ($bold) ? "bold_$fg" : "$fg";
            my $buf = colorizeString("$fgg", $fgg) .
                (" " x ($labelWidth - length($fgg)));
            for my $bg (@atomicColors) {
                $buf .= " " . colorizeString($sampleText, $fgg, $bg);
            }
            printf("%2d: $buf\n", $cnum);
        }
    }
    exit;
}

# For --list, show a compact table of effect_fg/bg combinations.
#
if ($list) {
    my %map = (
        "black"     => "blk",
        "red"       => "red",
        "green"     => "grn",
        "yellow"    => "yel",
        "blue"      => "blu",
        "magenta"   => "mag",
        "cyan"      => "cyn",
        "white"     => "wht",
    );
    my @effects = sort keys %effectsOn;
    for (my $e=0; $e<scalar(@effects); $e++) {
        print "\n";
        print "******* Colors with " . ($effects[$e] || "no") .
            " effects:\n";
        my $eff = ($effects[$e] ne "plain") ? ($effects[$e] . "_") : "";
        for my $fg (@atomicColors) {
            my $buf = "";
            for my $bg (@atomicColors) {
                my $sample = ' ' . $map{$fg} . "/" . $map{$bg} . ' ';
                my $key = $eff . $fg;
                $buf .= colorizeString($sample, $key, $bg) . ($break ? "\n":" ");
            }
            print "$buf\n";
        }
        print "\n";
    }
    exit unless ($xterm256);

    my $end = "\e[0m";
    print "\n******* Foreground and Background xterm256 colors:\n";
    for (my $i=0; $i<256; $i++) {
        print "$i: " .
            $esc . "[38;5;$i" . "m (fg sample) "        . $end . "\t" .
            $esc . "[38;5;$i" . "m \e[47m (fg sample) " . $end . "\t" .
            $esc . "[48;5;$i" . "m (bg sample) "        . $end . "\t" .
            $esc . "[48;5;$i" . "m \e[37m (bg sample) " . $end .
             ($break ? "\n":", ");
    }
    print "\n";
    exit;
}

if ($effects) {
    for my $e (sort keys %effectsOn) {
        printf("%-30s '%s'.\n", $e, colorizeString($e, $e));
    }
    exit;
}

if ($lslist) {
    setupDircolors();
    my %byColor = ();
    for my $lsc (@lsColors) {
        $lsc =~ m/^(.*)=(.*)/;
        my $expr = $1; my $colorCode = $2;
        if (!defined $byColor{$colorCode}) { $byColor{$colorCode} = ""; }
        $byColor{$colorCode} .= "$expr ";
    }
    print "Colors for 'ls':\n";
    for my $code (sort keys %byColor) {
        my $name = getColorName($code);
        my $con2 = (defined $colorTable{$name}) ?
            ($esc . $colorTable{$name}) : "";
        print "$con2$code ($name):$coff $byColor{$code}\n";
    }
    exit;
}

if ($lsget ne "") {
    setupDircolors();
    my $found = 0;
    for my $lsc (@lsColors) {
        if ($lsc =~ $lsget) {
            $found++;
            (my $code = $lsc) =~ s/^.*=//;
            my $name = getColorName($code);
            my $con2 = (defined $colorTable{$name}) ?
                ($esc . $colorTable{$name}) : "";
            print "$lsc\t$code ($con2$name$coff)\n";
        }
    }
    ($found>0) || print "No LS_COLORS mapping found for '$lsget'.\n";
    exit;
}

# You can't easily set the relevant environment from Perl, since it's
# owned by the parent process. So return a big string the caller can use....
#
if ($setenv) {
    my $buf = "";
    for my $c (keys %colorTable) {
        (my $seq = $colorTable{$c}) =~ s/\[//;
        $seq =~ s/m$//;
        $buf .= $envPrefix . "_$c='$seq';";
    }
    print $buf;
    exit;
}


###############################################################################
# Remaining commands require that a color be specified.
#
(scalar @ARGV) || die "No color specified.\n";

# For '-all', copy stdin coloring each line.
# Support a list of colors to alternate among.
#
if ($all) {
    my $reset = $colorTable{"fg_default"};
    my $bg_reset = $colorTable{"/default"};
    my @clist = ();
    while ($ARGV[0]) {
        my $colorName = shift;
        if ($colorName eq "usa")  {
            push(@clist, $colorTable{"_red" . $boldToken});
            push(@clist, $colorTable{"_default" . $boldToken});
            push(@clist, $colorTable{"_blue"    . $boldToken});
        }
        elsif ($colorName eq "christmas")  {
            push(@clist, $colorTable{"_red" . $boldToken});
            push(@clist, $colorTable{"_green"   . $boldToken});
        }
        elsif ($colorName eq "italy")  {
            push(@clist, $colorTable{"_red" . $boldToken});
            push(@clist, $colorTable{"_green"   . $boldToken});
            push(@clist, $colorTable{"_default" . $boldToken});
        }
        elsif ($colorName eq "rainbow")  {
            push(@clist, $colorTable{"_red" . $boldToken});
            push(@clist, $colorTable{"fg_red"});
            push(@clist, $colorTable{"_yellow"  . $boldToken});
            push(@clist, $colorTable{"_green"   . $boldToken});
            push(@clist, $colorTable{"_blue"    . $boldToken});
            push(@clist, $colorTable{"_magenta" . $boldToken});
            push(@clist, $colorTable{"fg_magenta"});
        }
        else {
            my $seq = $colorTable{$colorName};
            if (!$seq) { $seq = $colorTable{"_$colorName"   . $boldToken}; }
            if (!$seq) {
                die "colorstring: Unknown color '$colorName'.\n";
            }
            push(@clist, $seq);
        }
    }
    #warn "Color sequence: " . join(" ",@clist) . "\n";

    my $n = 0;
    while (my $rec = <>) {
        chomp($rec);
        print $esc . $clist[$n] . $rec
            . $esc . $reset
            . $esc . $bg_reset . "\n";
        $n++;
        if ($n >= scalar @clist) { $n = 0; }
    }
    exit;
}


###############################################################################
# Look up the color name(s) they requested.
#
my $colorName = lc(shift);
my $escString = $colorTable{$colorName};
if (!$escString) {
    $escString = $colorTable{"_$colorName"  . $boldToken};
}
($escString) ||
    die "colorstring: Unknown color key '$colorName'. Use -h for help.\n";


###############################################################################
# Convert to the desired output syntax
#
if ($lsset ne "") {
    ($verbose) && warn "Attempting -lsset for expr '$lsset'.\n";
    my $orig = $ENV{LS_COLORS};
    (my $new = $orig) =~ s/$lsset=.*?(:|$)//;
    $new =~ s/:+$//;
    $escString =~ s/^\[//;
    $escString =~ s/m$//;
    $escString = "$new:$lsset=$escString";
}
elsif ($lscolorset ne "") {
    ($verbose) && warn "Attempting -lscolorset for color '$lscolorset'.\n";
    $escString =~ s/^\[//;
    $escString =~ s/m$//;
    my $orig = $ENV{LS_COLORS};
    my $new = $orig;
    my $n = ($new =~ s/=$lscolorset(:|$)/=$escString/g);
    ($quiet) || warn "Changing $n LS_COLOR mappings to new color.\n";
    $new =~ s/:+$//;
    $escString = $new;
}
elsif ($ps) {
    $escString = "\\[\\e" . $escString . "\\]\n";
}
elsif ($perl) {
    $escString = "   \$colors{\"$colorName\"} = \"\\e" . $escString . "\";\n";
}
elsif ($python) {
    $escString = "   colors[$colorName] = u\"\\x1B" . $escString . "\"\n";
}
elsif ($print) {
    $escString = "   ESC " . $escString . "\n";
}
elsif ($message || $warnmsg) {
    my $s1 = $esc . $escString;
    my $s3 = $esc . $colorTable{"cancel"} . "\n";
    $escString = $s1 . $message . $s3;
    if ($warnmsg) {
        print STDERR "$s1$warnmsg$s3";
    }
    if (!$message) { exit; }
}
else {
    $escString = $esc . $escString;
}

# Issue it and we're done (no newline).
#
print $escString;

exit;


###############################################################################
#
sub colorizeString {
    my ($msg, $fg, $bg) = @_;
    my $key = ($bg && ($fg ne $bg)) ? "$fg/$bg" : "$fg";
    my $c = $colorTable{$key};
    if (!$c) {
        eMsg(1, "Can't find entry for '$key'.");
        return("?" x length($msg));
    }
    my $buf =  "\e" . $c . $msg . $coff;
    return($buf);
}


###############################################################################
# Create lists of color names and meanings. When setting up the codes,
# don't include the initial escape character,
# because it has to be expressed differently depending on context.
#
# OBSOLETE: Now parsing names as needed instead of precalculating them all.
#
sub setupColors {
    # These basic color names are re-used for foreground, bold foreground,
    # and background (with different offsets).
    #
    $atomicColors[0] = "black";
    $atomicColors[1] = "red";
    $atomicColors[2] = "green";
    $atomicColors[3] = "yellow";
    $atomicColors[4] = "blue";
    $atomicColors[5] = "magenta";
    $atomicColors[6] = "cyan";
    $atomicColors[7] = "white";
    (scalar @atomicColors == 8) || die "Bad color table!\n";

    # Other properties
    #
    %effectsOn = (
        "plain"       => "0",
        "bold"        => "1",
        "faint"       => "2",
        "italic"      => "3",
        "ul"          => "4",
        #"blink"       => "5", # See below
        #"fblink"      => "6", # See below
        "inverse"     => "7",
        "invisible"   => "8",
        "strike"      => "9",
    );
    # Be nice to people with blink sensitivities.
    if (!defined $ENV{'NOBLINK'}) {
        $effectsOn{'blink'} = 5;
        $effectsOn{'fblink'} = 6;
    }

    my %effectsOff = (
        "bold_off"    => "22",  # mainly xterm?
        "inverse_off" => "27",
        "ul_off"      => "24",
        "blink_off"   => "25",
        # invisible off?
    );

    for my $e (keys %effectsOn) {
        $colorTable{$e} = "[" . $effectsOn{$e} . "m";
    }
    $colorTable{"cancel"}      = "[m";
    $colorTable{"off"}         = "[m";
    $colorTable{"fg_default"}  = "[39m";
    $colorTable{"/default"}  = "[49m";
    $colorTable{"_default"} = "[39m"    . $boldToken;

    # Make up the full tables of all known color names, combos, whatever.
    # NOTE: The leading escape is not included here.
    ### FIX: Sync with sjdUtils color support.
    ### FIX: Support "!" for negating effects per %effectsOff.
    #
    $colorTable{"default"} =
        ($colorTable{"fg_default"}); # . $colorTable{"/default"});

    my @eff = keys %effectsOn;
    for (my $en=0; $en<scalar(@eff); $en++) {
        my $e = $eff[$en];
        my $ekey = ($e eq "plain") ? "" : ($e."_");
        my $eval = ($e eq "plain") ? "" : ($effectsOn{$e}.';');
        for (my $i=0; $i<scalar(@atomicColors); $i++) {
            $colorTable{$ekey.$atomicColors[$i]}       = '['.$eval.(30+$i)."m";
            $colorTable{$ekey."/".$atomicColors[$i]} = '['.$eval.(40+$i)."m";
            # Foreground/background combos
            for (my $j=0; $j<scalar(@atomicColors); $j++) {
                # ($i==$j) && next;
                my $pairKey =  $atomicColors[$i]."/".$atomicColors[$j];
                $colorTable{$ekey.$pairKey} =
                    '['.$eval.(30+$i).";".(40+$j)."m";
            } # for j
        } # for i
    } # for e

    if ($verbose) {
        print("Available color names:\n");
        for my $k (sort(keys(%colorTable))) {
            printf("%-30s %s\n",
                $k, "ESC " . sjdUtils::showInvisibles($colorTable{$k}));
        }
    }
} # setupColors


###############################################################################
# Take an n;m... string as used in environment variable LS_COLORS,
# and try to look up what it means.
# Normalizes to increasing (numeric) order.
#
sub getColorName {
    my ($code) = @_;
    $code =~ s/0+(\d)/$1/g; # Strip any leading zeros
    my $code2 = join(';', sort(split(/;/,$code)));
    ($verbose) && warn
        "normalized order: '$code' -> '$code2'\n";
    $code = $code2;
    $code = "[$code" . "m";
    for my $k (keys %colorTable) {
        if ($colorTable{$k} eq $code) { return($k); }
    }
    ($verbose) && warn "Couldn't find '$code' in color table.\n";
    return("?");
}


###############################################################################
#
sub setupDircolors {
    @lsColors = split(/:/,`dircolors`);
    $lsColors[0] =~ s/LS_COLORS='//;
    pop @lsColors; # "export LS_COLORS"
    $lsColors[-1] =~ s/';//;
}


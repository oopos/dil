#!/bin/bash

PHOBOS_SRC=$1
# Find source files, ignore phobos.d, cast.d, invariant.d, switch.d, unittest.d and the folder internal/.
FILES=`find $PHOBOS_SRC \( \! \( -name "phobos.d" -o -name "cast.d" -o -name "invariant.d" -o -name "switch.d" -o -name "unittest.d" \) -a \( -iname '*.d' -o -iname '*.di' \) \) -type f -print | sed -e "s@^$PHOBOS_SRC/*internal.\+@@"`
D_VERSION="1.0" # TODO: Needs to be determined dynamically.

# Modify std.ddoc and write it out to data/phobos.ddoc.
python -c '
# import the module for regular expressions.
import re
# Open ddoc file to be modified.
ddoc = open("'$PHOBOS_SRC'/std.ddoc").read()
# Add a website icon.
ddoc = re.sub(r"</head>", "<link rel=\"icon\" type=\"image/gif\" href=\"./holy.gif\" />\n</head>", ddoc)
# Make "../" to "./".
ddoc = re.sub(r"\.\./(style.css|dmlogo.gif)", r"./\1", ddoc)
# Make some relative paths to absolute ones.
ddoc = ddoc.replace("../", "http://www.digitalmars.com/d/'$D_VERSION'/")
# Replace with a DDoc macro.
ddoc = re.sub("Page generated by.+", "$(GENERATED_BY)", ddoc)
# Replace phobos.html#xyz.
# ddoc = re.sub("href=\"phobos.html#(std_[^\"]+)\"", "href=\"\\1.html\"", ddoc)
# Make e.g. "std_string.html" to "std.string.html".
ddoc = re.sub("href=\"std_.+?\"", lambda m: m.group(0).replace("_", "."), ddoc)
# Linkify the title.
ddoc = re.sub("<h1>\$\(TITLE\)</h1>", "<h1><a href=\"$(SRCFILE)\">$(TITLE)</a></h1>", ddoc)
# Write new ddoc file.
open("data/phobos.ddoc", "w").write(ddoc)'

# Destination of all documentation files.
DOC="phobosdoc"
# Create the destination folders.
mkdir -p $DOC/htmlsrc

# Returns the fully qualified module name of a d source file.
function getModuleFQN
{
  echo $1 | sed -e "s@^$PHOBOS_SRC/*@@" -e 's@/@.@g' -e 's@\.d$@@';
}

# Create an index file.
echo "Ddoc
<ul>
$(for DFILE in $FILES; do
  MODULE_FQN=$(getModuleFQN $DFILE)
  echo '<li><a' href="$MODULE_FQN.html"'>'$MODULE_FQN.html'</a></li>'
  done)
</ul>
Macros:
  TITLE = Index" > data/index.d

# Some files needed from dmd's doc folder.
PHOBOS_HTML=$PHOBOS_SRC/../../html/d/phobos
cp $PHOBOS_HTML/erfc.gif $PHOBOS_HTML/erf.gif $PHOBOS_HTML/../style.css $PHOBOS_HTML/../holy.gif $PHOBOS_HTML/../dmlogo.gif $DOC/
# Syntax highlighted files need html.css.
cp data/html.css $DOC/htmlsrc

# Generate documenation files.
dil ddoc $DOC/ -i -v data/phobos.ddoc data/phobos_overrides.ddoc -version=DDoc $FILES $PHOBOS_SRC/phobos.d data/index.d

# Modify $DOC/phobos.html.
python -c '
# import the module for regular expressions.
import re
# Open file to be modified.
ddoc = open("'$DOC'/phobos.html").read()
ddoc = ddoc.replace("../", "http://www.digitalmars.com/d/'$D_VERSION'/")
# Make e.g. "std_string.html" to "std.string.html".
ddoc = re.sub("href=\"std_[^\"]+\"", lambda m: m.group(0).replace("_", "."), ddoc)
# De-linkify the title.
ddoc = re.sub("<h1><a[^>]+>(.+?)</a></h1>", "<h1>\\1</h1>", ddoc)
# Write modified file.
open("'$DOC'/phobos.html", "w").write(ddoc)'

# Generate syntax highlighted files.
HTMLSRC="$DOC/htmlsrc"
for DFILE in $FILES; do
  # Use sed to remove part of the path, convert '/' to '.' and remove the extension.
  HTMLFILE=$(getModuleFQN $DFILE).html
  echo "dil hl $DFILE > $HTMLSRC/$HTMLFILE";
  dil hl --lines --syntax --html $DFILE > "$HTMLSRC/$HTMLFILE";
done
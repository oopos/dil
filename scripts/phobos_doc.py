#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Aziz Köksal
import os, re
from path import Path
from common import *
from html2pdf import PDFGenerator

def modify_std_ddoc(std_ddoc, phobos_ddoc, version):
  """ Modify std.ddoc and write it out to phobos.ddoc. """
  ddoc = open(std_ddoc).read() # Read the whole file.
  # Add a website icon.
  ddoc = re.sub(r"</head>", '<link rel="icon" type="image/gif" href="./holy.gif">\r\n</head>', ddoc)
  # Make "../" to "./".
  ddoc = re.sub(r"\.\./(style.css|dmlogo.gif)", r"./\1", ddoc)
  # Make some relative paths to absolute ones.
  ddoc = ddoc.replace("../", "http://www.digitalmars.com/d/%s/" % version)
  # Replace with a DDoc macro.
  ddoc = re.sub("Page generated by.+", "$(GENERATED_BY)", ddoc)
  # Replace phobos.html#xyz.
  # ddoc = re.sub("href=\"phobos.html#(std_[^\"]+)\"", "href=\"\\1.html\"", ddoc)
  # Make e.g. "std_string.html" to "std.string.html".
  ddoc = re.sub('href="std_.+?"', lambda m: m.group(0).replace("_", "."), ddoc)
  # Linkify the title.
  ddoc = re.sub("<h1>\$\(TITLE\)</h1>", '<h1><a href="$(SRCFILE)">$(TITLE)</a></h1>', ddoc)
  # Add a link to the index in the navigation sidebar.
  ddoc = re.sub('(NAVIGATION_PHOBOS=\r\n<div class="navblock">)', '\\1\r\n$(UL\r\n$(LI<a href="index.html" title="Index of all HTML files">Index</a>)\r\n)', ddoc)
  # Write new ddoc file.
  open(phobos_ddoc, "w").write(ddoc)

# Create an index file.
def create_index_file(index_d, prefix_path, FILES):
  text = ""
  for filepath in FILES:
    fqn = get_module_fqn(prefix_path, filepath)
    text += '  <li><a href="%(fqn)s.html">%(fqn)s.html</a></li>\n' % {'fqn':fqn}
  text = "Ddoc\n<ul>\n%s\n</ul>\nMacros:\nTITLE = Index" % text
  open(index_d, 'w').write(text)

def copy_files(DIL, PHOBOS, DEST):
  """ Copies required files to the destination folder. """
  for f in ["erfc.gif", "erf.gif"] + \
            Path("..")//("style.css", "holy.gif", "dmlogo.gif"):
    (PHOBOS.HTML/f).copy(DEST)
  # Syntax highlighted files need html.css.
  (DIL.DATA/"html.css").copy(DEST.HTMLSRC)

def copy_files2(DIL, PHOBOS, DEST):
  """ Copies required files to the destination folder. """
  for f in ("erfc.gif", "erf.gif"):
    (PHOBOS.HTML/f).copy(DEST)
  for FILE, DIR in (
      (DIL.DATA/"html.css", DEST.HTMLSRC),
      (DIL.KANDIL.style,    DEST.CSS)):
    FILE.copy(DIR)
  for FILE in DIL.KANDIL.jsfiles:
    FILE.copy(DEST.JS)
  for img in DIL.KANDIL.images:
    img.copy(DEST.IMG)

def modify_phobos_html(phobos_html, version):
  """ Modifys DEST/phobos.html. """
  ddoc = open(phobos_html).read() # Read the whole file.
  # Make relative links to absolute links.
  ddoc = ddoc.replace("../", "http://www.digitalmars.com/d/%s/" % version)
  # Make e.g. "std_string.html" to "std.string.html".
  ddoc = re.sub("href=\"std_[^\"]+\"", lambda m: m.group(0).replace("_", "."), ddoc)
  # De-linkify the title.
  ddoc = re.sub("<h1><a[^>]+>(.+?)</a></h1>", "<h1>\\1</h1>", ddoc)
  # Write the contents back to the file.
  open(phobos_html, "w").write(ddoc)

def write_missing_macros(path):
  """ These macros are missing in std.ddoc. """
  open(path, "w").write("""WIKI =
COMMENT = <!-- -->
DOLLAR = $
_PI = &pi;
POW = $1<sup>$2</sup>
TABLE_DOMRG = $(TABLE_SV $0)
std_boilerplate = <!-- undefined macro in std/outbuffer.d -->
DOMAIN = <!-- undefined macro in std/math.d -->
RANGE = <!-- undefined macro in std/math.d -->"""
  )

def write_overrides_ddoc(path):
  """ For kandil. """
  open(path, "w").write("""
GENERATED_BY = Page generated by $(LINK2 http://code.google.com/p/dil, dil) on $(DATETIME)
SRCFILE = ./htmlsrc/$(DIL_MODFQN).html
DIL_SYMBOL = <a href="$(SRCFILE)#L$4" class="sym$3" name="$2" title="At line $4.">$1</a>
"""
  )

def write_overrides_ddoc2(path):
  """ For kandil. """
  open(path, "w").write("""
COPYRIGHT = Copyright © 1999-2009 by Digital Mars ®, All Rights Reserved.
"""
  )

def write_PDF(DIL, SRC, VERSION, TMP):
  pdf_gen = PDFGenerator()
  pdf_gen.fetch_files(DIL, TMP)

  for gif in SRC//("erf.gif", "erfc.gif"): gif.copy(TMP)
  html_files = SRC.glob("*.html")
  ignore_list = ("phobos.html", "std.c.windows.windows.html")
  html_files = [f for f in html_files
                    if not any(map(f.endswith, iter(ignore_list)))]
  symbol_link = "http://dil.googlecode.com/svn/doc/Phobos_%s" % VERSION
  params = {"pdf_title": "Phobos %s API" % VERSION,
    "cover_title": "Phobos %s<br/><b>API</b>" % VERSION,
    "author": "Walter Bright",
    "subject": "Programming API",
    "keywords": "Phobos D Standard Library",
    "nested_toc": True,
    "symlink": symbol_link}
  pdf_gen.run(html_files, SRC/("Phobos.%s.API.pdf"%VERSION), TMP, params)

def main():
  from optparse import OptionParser

  usage = "Usage: scripts/phobos_doc.py VERSION PHOBOS_DIR [DESTINATION_DIR]"
  parser = OptionParser(usage=usage)
  #parser.add_option("--rev", dest="revision", metavar="REVISION", default=None,
    #type="int", help="set the repository REVISION to use in symbol links")
  parser.add_option("--zip", dest="zip", default=False, action="store_true",
    help="create a 7z archive")
  parser.add_option("--pdf", dest="pdf", default=False, action="store_true",
    help="create a PDF document")
  parser.add_option("--kandil", dest="use_kandil", action="store_true",
    default=False, help="use kandil as the documentation front-end")

  (options, args) = parser.parse_args()

  if len(args) < 2:
    return parser.print_help()

  change_cwd(__file__)

  # Validate the version argument.
  m = re.match(r"((\d)\.(\d\d\d))", args[0])
  if not m:
    parser.error("invalid VERSION; format: /\d.\d\d\d/ E.g.: 1.123")
  matched = m.groups()
  # Extract the version strings.
  VERSION, V_MAJOR = matched[:2]
  V_MINOR = matched[2]
  D_VERSION  = V_MAJOR + ".0" # E.g.: 1.0 or 2.0

  # Path to dil's root folder.
  DIL       = dil_path()
  # The source code folder of Phobos.
  PHOBOS_SRC = Path(args[1])
  # Path to the html folder of Phobos.
  PHOBOS_SRC.HTML = PHOBOS_SRC/".."/".."/"html"/"d"/"phobos"
  # Destination of doc files.
  DEST       = doc_path(firstof(str, getitem(args, 2), 'phobosdoc'))
  # Temporary directory, deleted in the end.
  TMP        = DEST/"tmp"
  # The list of module files (with info) that have been processed.
  MODLIST    = TMP/"modules.txt"
  # List of files to ignore.
  IGNORE_LIST = ("phobos.d", "cast.d", "invariant.d", "switch.d", "unittest.d")
  IGNORE_LIST = [Path.sep+i for i in IGNORE_LIST] # Prepend with path separator.
  # The files to generate documentation for.
  FILES       = []

  if not PHOBOS_SRC.exists:
    print "The path '%s' doesn't exist." % PHOBOS_SRC
    return

  build_dil_if_inexistant(DIL.EXE)

  # Create the destination folders.
  DEST.makedirs()
  map(Path.mkdir, (DEST.HTMLSRC, TMP))
  if options.use_kandil:
    map(Path.mkdir, (DEST.JS, DEST.CSS, DEST.IMG))

  # Begin processing.
  find_source_files(PHOBOS_SRC, FILES)
  # Filter out files in the internal/ folder and in the ignore list.
  FILES = [f for f in FILES if not any(map(f.endswith, IGNORE_LIST)) and \
                               not f.startswith(PHOBOS_SRC/"internal")]
  FILES.sort() # Sort for index.

  modify_std_ddoc(PHOBOS_SRC/"std.ddoc", TMP/"phobos.ddoc", D_VERSION)
  write_missing_macros(TMP/"missing.ddoc")
  if options.use_kandil:
    write_overrides_ddoc2(TMP/"overrides.ddoc")
    DOC_FILES = [TMP/"phobos.ddoc", DIL.KANDIL.ddoc] + \
                 TMP//("missing.ddoc", "overrides.ddoc") + \
                [PHOBOS_SRC/"phobos.d"] + FILES
    versions = ["DDoc"]
    generate_docs(DIL.EXE, DEST, MODLIST, DOC_FILES,
                  versions, options='-v -i -hl --kandil'.split(' '))
    modify_phobos_html(DEST/"phobos.html", D_VERSION)
    copy_files2(DIL, PHOBOS_SRC, DEST)
    if options.pdf:
      write_PDF(DIL, DEST, VERSION, TMP)
  else:
    write_overrides_ddoc(TMP/"overrides.ddoc")
    create_index_file(TMP/"index.d", PHOBOS_SRC, FILES)
    DOC_FILES = FILES + [PHOBOS_SRC/"phobos.d"] + \
      TMP//("index.d", "phobos.ddoc", "missing.ddoc", "overrides.ddoc")
    versions = ["DDoc"]
    generate_docs(DIL.EXE, DEST, MODLIST, DOC_FILES,
                  versions, options=['-v', '-i', '-hl'])
    modify_phobos_html(DEST/"phobos.html", D_VERSION)
    copy_files(DIL, PHOBOS_SRC, DEST)
    if options.pdf:
      print "Warning: can only create a PDF document from kandil HTML files."

  TMP.rmtree()

  if options.zip:
    name, src = "Phobos.%s_doc" % VERSION, DEST
    cmd = "7zr a %(name)s.7z %(src)s" % locals()
    print cmd
    os.system(cmd)

if __name__ == "__main__":
  main()

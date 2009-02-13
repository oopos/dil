#! /usr/bin/python
# -*- coding: utf-8 -*-
# Author: Aziz Köksal
import os, re
from path import Path
from common import *
from sys import platform
from build import DMDCommand
from html2pdf import PDFGenerator

def copy_files(DIL):
  """ Copies required files to the destination folder. """
  for FILE, DIR in (
      (DIL.DATA/"dilconf.d", DIL.BIN),
      (DIL.DATA/"html.css",  DIL.DOC.HTMLSRC),
      (DIL.KANDIL.style,     DIL.DOC.CSS)):
    FILE.copy(DIR)
  for FILE in DIL.KANDIL.jsfiles:
    FILE.copy(DIL.DOC.JS)
  for img in DIL.KANDIL.images:
    img.copy(DIL.DOC.IMG)

def writeMakefile():
  """ Writes a Makefile for building dil to the disk. """
  # TODO: implement.
  pass

def build_dil(dmd_exe, *args, **kwargs):
  kwargs.update(dmd_exe=dmd_exe)
  cmd = DMDCommand(*args, **kwargs)
  cmd.use_wine = dmd_exe.use_wine
  print cmd
  cmd.call()

def update_version(path, major, minor, suffix):
  """ Updates the version info in the compiler's source code. """
  major, minor = int(major), int(minor)
  code = open(path).read()
  code = re.sub(r"(VERSION_MAJOR\s*=\s*)[\w\d]+;", r"\g<1>%s;" % major, code)
  code = re.sub(r"(VERSION_MINOR\s*=\s*)\d+;", r"\g<1>%s;" % minor, code)
  code = re.sub(r'(VERSION_SUFFIX\s*=\s*)"";', r'\g<1>"%s";' % suffix, code)
  open(path, "w").write(code)

def write_PDF(DIL, SRC, VERSION, TMP):
  # TODO: some links should be rewritten:
  # E.g.: .) "dil.lexer.Funcs.html#CProperty.Whitespace" ->
  #          "m-dil.lexer.Funcs:CProperty.Whitespace"
  #       .) "dil.lexer.Identifier" -> "m-dil.lexer.Identifier"
  pdf_gen = PDFGenerator()
  pdf_gen.fetch_files(DIL, TMP)
  html_files = SRC.glob("*.html")
  symlink = "http://dil.googlecode.com/svn/doc/dil_%s" % VERSION
  params = {"pdf_title": "dil %s API" % VERSION,
    "cover_title": "dil %s<br/><b>API</b>" % VERSION,
    "author": u"Aziz Köksal",
    "subject": "Compiler API",
    "keywords": "dil D compiler API documentation",
    "x_html": "XHTML",
    "nested_toc": True,
    "symlink": symlink}
  pdf_gen.run(html_files, SRC/("dil.%s.API.pdf"%VERSION), TMP, params)

def main():
  from functools import partial as func_partial
  from optparse import OptionParser

  usage = "Usage: scripts/release.py VERSION [Options]"
  parser = OptionParser(usage=usage)
  add_option = func_partial(parser.add_option, action="store_true",
                            default=False)
  add_option("-s", "--dsymbols", dest="debug_symbols",
    help="generate debug symbols for debug builds")
  add_option("-d", "--docs", dest="docs", help="generate documentation")
  add_option("-n", "--no-bin", dest="no_binaries", help="don't compile code")
  add_option("--7z", dest="_7z", help="create a 7z archive")
  add_option("--gz", dest="tar_gz", help="create a tar.gz archive")
  add_option("--bz2", dest="tar_bz2", help="create a tar.bz2 archive")
  add_option("--zip", dest="zip", help="create a zip archive")
  add_option("--pdf", dest="pdf", help="create a PDF document")
  add_option("-m", dest="copy_modified",
    help="copy modified files from the (git) working directory")
  parser.add_option("--src", dest="src", metavar="SRC", default=None,
    help="use SRC folder instead of checking out code with git")
  parser.add_option("--dmd-exe", dest="dmd_exe", metavar="EXE_PATH",
    default="dmd", help="specify EXE_PATH if dmd is not in your PATH")
  parser.add_option("--builddir", dest="builddir", metavar="DIR", default=None,
    help="where to build the release and archives (default is build/)")
  parser.add_option("--winpath", dest="winpath", metavar="P", default=None,
    help="permanently append P to PATH in the Windows (or wine's) registry. "
         "Exits the script.")

  (options, args) = parser.parse_args()

  if options.winpath != None:
    from env_path import append2PATH
    append2PATH(options.winpath, Path(""))
    return

  if len(args) < 1:
    return parser.print_help()
  if len(args) > 1:
    print "Warning! Arguments ignored: " + " ".join(args[1:])

  change_cwd(__file__)

  # Validate the version argument.
  m = re.match(r"((\d)\.(\d\d\d)(-\w+)?)", args[0])
  if not m:
    parser.error("invalid VERSION; format: /\d.\d\d\d(-\w+)?/ E.g.: 1.123")
  matched = m.groups()

  if not Path(options.dmd_exe).exists and not locate_command(options.dmd_exe):
    parser.error("The executable '%s' couldn't be located or does not exist." %
      options.dmd_exe)

  # Path to dil's root folder.
  DIL       = dil_path()
  # Name or path to the executable of dmd.
  DMD_EXE   = Path(options.dmd_exe)
  # The version of dil to be built.
  VERSION, V_MAJOR = matched[:2]
  V_MINOR, V_SUFFIX = (matched[2], firstof(str, matched[3], ''))

  # Build folder.
  BUILD_DIR = Path(firstof(str, options.builddir, "build"))
  # Destination of distributable files.
  DEST      = dil_path(BUILD_DIR/("dil."+VERSION))
  BIN       = DEST.BIN # Shortcut to the bin/ folder.
  DEST.DOC  = doc_path(DEST.DOC)

  # Temporary directory, deleted in the end.
  TMP       = DEST/"tmp"
  # The list of module files (with info) that have been processed.
  MODLIST   = TMP/"modules.txt"
  # The files to generate documentation for.
  FILES     = []

  # Create the build directory.
  BUILD_DIR.makedirs()
  # Check out a new working copy.
  DEST.rmtree() # First remove the tree.
  if options.src != None:
    # Use the source folder specified by the user.
    src = Path(options.src)
    if not src.exists:
      parser.error("the given SRC path (%s) doesn't exist" % src)
    #if src.ext in ('.zip', '.gz', 'bz2'):
      # TODO:
    src.copytree(DEST)
  elif locate_command('git'):
    # Use git to checkout a clean copy.
    os.system("git clone ./ '%s'" % DEST)
    (DEST/".git").rmtree() # Remove the .git folder.
    if options.copy_modified:
      modified_files = os.popen("git ls-files -m").read()[:-1]
      if modified_files != "":
        for f in modified_files.split("\n"):
          Path(f).copy(DEST/f)
  else:
    parser.error("git is not in your PATH; specify --src instead")
  # Create other directories not available in a clean checkout.
  DOC = DEST.DOC
  map(Path.mkdir, (DEST.BIN, DOC, DOC.HTMLSRC,
                   DOC.CSS, DOC.IMG, DOC.JS, TMP))

  # Find the source code files.
  FILES = find_dil_source_files(DEST.SRC)

  # Update the version info.
  VERSION_FILE = DEST.SRC/"dil"/"Version.d"
  update_version(VERSION_FILE, V_MAJOR, V_MINOR, V_SUFFIX)

  if options.docs:
    build_dil_if_inexistant(DIL.EXE)

    DOC_FILES = [DEST.KANDIL.ddoc] + \
                 DEST.DATA//("macros_dil.ddoc", "dilconf.d") + FILES
    print "***** Generating documentation *****"
    versions = ["DDoc"]
    generate_docs(DIL.EXE, DEST.DOC, MODLIST, DOC_FILES,
                  versions, options=['-v', '-i', '-hl', '--kandil'])
    if options.pdf:
      write_PDF(DEST, DEST.DOC, VERSION, TMP)

  DMD_EXE.use_wine = False
  use_wine = False
  if platform is 'win32':
    build_linux_binaries = False
    build_windows_binaries = True
  else:
    build_linux_binaries = True
    build_windows_binaries = locate_command("wine") != None
    class BINPath(Path):
      def __div__(self, name):
        """ Converts a Unix path to a Windows path. """
        name = Path.__div__(self, name)
        return name if name.ext != '.exe' else name.replace("/", r"\\")
    BIN = BINPath(BIN)
    use_wine = True # Use wine on Linux to build Windows binaries.
    if not build_windows_binaries:
      print "Error: can't build windows binaries: "\
            "wine is not installed or not in PATH."

  if options.no_binaries:
    build_linux_binaries = build_windows_binaries = False

  # Create partial functions with common parameters.
  # Note: the -inline switch makes the binaries significantly larger on Linux.
  build_dil_rls = func_partial(build_dil, DMD_EXE, FILES,
                               release=True, optimize=True, inline=True)
  build_dil_dbg = func_partial(build_dil, DMD_EXE, FILES,
                               debug_info=options.debug_symbols)
  if build_linux_binaries:
    print "***** Building Linux binaries *****"
    # Linux Debug Binaries
    build_dil_dbg(BIN/"dil_d")
    build_dil_dbg(BIN/"dil2_d", versions=["D2"])
    # Linux Release Binaries
    build_dil_rls(BIN/"dil")
    build_dil_rls(BIN/"dil2", versions=["D2"])

  if build_windows_binaries:
    print "***** Building Windows binaries *****"
    DMD_EXE.use_wine = use_wine
    # Windows Debug Binaries
    build_dil_dbg(BIN/"dil_d.exe")
    build_dil_dbg(BIN/"dil2_d.exe", versions=["D2"])
    # Windows Release Binaries
    build_dil_rls(BIN/"dil.exe")
    build_dil_rls(BIN/"dil2.exe", versions=["D2"])

  print "***** Copying files *****"
  copy_files(DEST)

  options.docs or DEST.DOC.rmtree()
  TMP.rmtree()

  # Build archives.
  assert DEST[-1] != Path.sep
  opt = options
  for exec_cmd, cmd in zip((opt.tar_gz, opt.tar_bz2, opt.zip, opt._7z),
    ("tar --owner root --group root -czf %(name)s.tar.gz %(src)s",
     "tar --owner root --group root --bzip2 -cf %(name)s.tar.bz2 %(src)s",
     "zip -q -9 -r %(name)s.zip %(src)s",
     "7zr a %(name)s.7z %(src)s")):
    if not exec_cmd: continue
    if locate_command(cmd):
      print "Error: the utility '%s' is not in your PATH." % cmd
      continue
    cmd = cmd % dict(locals(), name=DEST, src=DEST)
    print cmd
    os.system(cmd)

if __name__ == '__main__':
  main()

/**
 * Author: Jari-Matti Mäkelä
 * License: GPL3
 */
module docgen.document.plaintextwriter;

import docgen.document.writer;
import docgen.misc.textutils;
import tango.io.FileConduit : FileConduit;
import tango.io.Print: Print;
import tango.text.convert.Layout : Layout;

//TODO: this is mostly broken now

/**
 * Writes a plain text document skeleton.
 */
class PlainTextWriter : AbstractDocumentWriter!(1, "plaintext") {
  this(DocumentWriterFactory factory, OutputStream[] outputs) {
    super(factory, outputs);
  }

  void generateTOC(Module[] modules) {
    // TODO
    auto print = new Print!(char)(new Layout!(char), outputs[0]);
  
    print.format(templates["toc"]);
  }

  void generateModuleSection() {
    // TODO
    auto print = new Print!(char)(new Layout!(char), outputs[0]);
  
    print.format(templates["modules"]);
  }

  void generateListingSection() {
    // TODO
    auto print = new Print!(char)(new Layout!(char), outputs[0]);
  
    print.format(templates["listings"]);
  }

  void generateDepGraphSection() {
    // TODO
    auto print = new Print!(char)(new Layout!(char), outputs[0]);
  
    print.format(templates["dependencies"]);
  }

  void generateIndexSection() { }

  void generateLastPage() { }

  void generateFirstPage() {
    auto output = new Print!(char)(new Layout!(char), outputs[0]);
    
    output(
      plainTextHeading(factory.options.templates.title ~ " Reference Manual") ~
      factory.options.templates.versionString ~ \n ~
      "Generated by " ~ docgen_version ~ \n ~
      timeNow() ~ \n \n \n ~
      plainTextHorizLine() ~ \n \n ~
      plainTextHeading("Table of Contents") ~ \n ~
      plainTextHeading("Module documentation") ~ \n ~
      plainTextHeading("File listings") ~ \n ~
      plainTextHeading("Dependency diagram") ~ \n
    );
  }
}

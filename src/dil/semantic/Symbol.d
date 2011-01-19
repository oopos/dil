/// Author: Aziz Köksal
/// License: GPL3
/// $(Maturity average)
module dil.semantic.Symbol;

import dil.ast.Node;
import dil.lexer.Identifier;
import dil.lexer.IdTable;
import common;

/// Enumeration of Symbol IDs.
enum SYM
{
  Module,
  Package,
  Class,
  Interface,
  Struct,
  Union,
  Enum,
  EnumMember,
  Template,
  Variable,
  Function,
  Alias,
  Typedef,
  OverloadSet,
  Scope,
  Parameter,
  Parameters,
//   Type,
}

/// A symbol represents an object with semantic code information.
class Symbol
{ /// Enumeration of symbol statuses.
  enum Status : ushort
  {
    Declared,   /// The symbol has been declared.
    Completing, /// The symbol is being processed.
    Complete    /// The symbol is complete.
  }

  SYM sid; /// The ID of this symbol.
  Status status; /// The semantic status of this symbol.
  Symbol parent; /// The parent this symbol belongs to.
  /// The name of this symbol.
  /// If the symbol is nameless Ident.Empty is assigned to it.
  Identifier* name;
  /// The syntax tree node that produced this symbol.
  /// Useful for source code location info and retrieval of doc comments.
  Node node;

  /// Constructs a Symbol object.
  /// Params:
  ///   sid = the symbol's ID.
  ///   name = the symbol's name.
  ///   node = the symbol's node.
  this(SYM sid, Identifier* name, Node node)
  {
    this.sid = sid;
    this.name = name ? name : Ident.Empty;
    this.node = node;
  }

  /// Change the status to Status.Completing.
  void setCompleting()
  { status = Status.Completing; }

  /// Change the status to Status.Complete.
  void setComplete()
  { status = Status.Complete; }

  /// Returns true if the symbol is being completed.
  bool isCompleting()
  { return status == Status.Completing; }

  /// Returns true if the symbols is complete.
  bool isComplete()
  { return status == Status.Complete; }

  /// A template for building isXYZ() methods.
  private static string is_()(string kind)
  {
    return `bool is`~kind~`(){ return sid == SYM.`~kind~`; }`;
  }

  mixin(is_("Module"));
  mixin(is_("Package"));
  mixin(is_("Class"));
  mixin(is_("Interface"));
  mixin(is_("Struct"));
  mixin(is_("Union"));
  mixin(is_("Enum"));
  mixin(is_("EnumMember"));
  mixin(is_("Template"));
  mixin(is_("Variable"));
  mixin(is_("Function"));
  mixin(is_("Alias"));
  mixin(is_("Typedef"));
  mixin(is_("OverloadSet"));
  mixin(is_("Scope"));
  mixin(is_("Parameter"));
  mixin(is_("Parameters"));
//   mixin(is_("Type"));

  /// Casts the symbol to Class.
  Class to(Class)()
  {
    assert(mixin(`this.sid == mixin("SYM." ~
      { const N = Class.stringof; // Slice off "Symbol" from the name.
        return N[$-6..$] == "Symbol" ? N[0..$-6] : N; }())`));
    return cast(Class)cast(void*)this;
  }

  /// Returns: the fully qualified name of this symbol.
  /// E.g.: dil.semantic.Symbol.Symbol.getFQN
  string getFQN()
  {
    char[] fqn = name.str.dup;
    if (parent) // Iter upwards until the root package is reached.
      for (auto s = parent; s.parent; s = s.parent)
        fqn = s.name.str ~ '.' ~ fqn;
    return fqn;
  }

  /// Returns the type of this symbol or null if inexistent.
  /// The return type is Object to avoid circular imports.
  Object getType()
  {
    return null;
  }

  /// Returns the mangled name of this symbol.
  char[] toMangle()
  {
    // TODO:
    return name.str.dup;
  }

  /// Returns the string representation of this symbol.
  char[] toString()
  {
    return name.str.dup;
  }
}

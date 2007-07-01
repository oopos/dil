/++
  Author: Aziz Köksal
  License: GPL2
+/
module Messages;

/// Index into table of error messages.
enum MID
{
  InvalidUnicodeCharacter,
  InvalidUTF8Sequence,
  // ''
  UnterminatedCharacterLiteral,
  EmptyCharacterLiteral,
  // #line
  ExpectedIdentifierSTLine,
  ExpectedNormalStringLiteral,
  ExpectedNumberAfterSTLine,
  NewlineInSpecialToken,
  UnterminatedSpecialToken,
  // ""
  UnterminatedString,
  // x""
  NonHexCharInHexString,
  OddNumberOfDigitsInHexString,
  UnterminatedHexString,
  // /* */ /+ +/
  UnterminatedBlockComment,
  UnterminatedNestedComment,
  // `` r""
  UnterminatedRawString,
  UnterminatedBackQuoteString,
  // \x \u \U
  UndefinedEscapeSequence,
  InsufficientHexDigits,
  // \&[a-zA-Z][a-zA-Z0-9]+;
  UnterminatedHTMLEntity,
  InvalidBeginHTMLEntity,
  // integer overflows
  OverflowDecimalSign,
  OverflowDecimalNumber,
  OverflowHexNumber,
  OverflowBinaryNumber,
  OverflowOctalNumber,
  OverflowFloatNumber,
  OctalNumberHasDecimals,
  NoDigitsInHexNumber,
  NoDigitsInBinNumber,
  HexFloatExponentRequired,
  HexFloatMissingExpDigits,
  FloatExponentDigitExpected,
}

string[] messages = [
  "invalid Unicode character.",
  "invalid UTF-8 sequence.",
  // ''
  "unterminated character literal.",
  "empty character literal.",
  // #line
  "expected 'line' after '#'.",
  `the filespec must be defined in a double quote string literal (e.g. "filespec".)`,
  "positive integer expected after #line",
  "newline not allowed inside special token.",
  "expected a terminating newline after special token.",
  // ""
  "unterminated string literal.",
  // x""
  "non-hex character '{1}' found in hex string.",
  "odd number of hex digits in hex string.",
  "unterminated hex string.",
  // /* */ /+ +/
  "unterminated block comment (/* */).",
  "unterminated nested comment (/+ +/).",
  // `` r""
  "unterminated raw string.",
  "unterminated back quote string.",
  // \x \u \U
  "found undefined escape sequence.",
  "insufficient number of hex digits in escape sequence.",
  // \&[a-zA-Z][a-zA-Z0-9]+;
  "unterminated html entity.",
  "html entities must begin with a letter.",
  // integer overflows
  "decimal number overflows sign bit.",
  "overflow in decimal number.",
  "overflow in hexadecimal number.",
  "overflow in binary number.",
  "overflow in octal number.",
  "overflow in float number.",
  "decimal digits are not allowed in octal numbers.",
  "invalid hex number; at least one hex digit expected.",
  "invalid binary number; at least one binary digit expected.",
  "the exponent of a hexadecimal float number is required.",
  "missing decimal digits in hexadecimal float exponent.",
  "exponents have to start with a digit.",
];
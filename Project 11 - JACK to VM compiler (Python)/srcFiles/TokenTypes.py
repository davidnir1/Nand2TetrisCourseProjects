from enum import Enum


class Type(Enum):
	KEYWORD = 1
	SYMBOL = 2
	IDENTIFIER = 3
	INT_CONST = 4
	STRING_CONST = 5


class Keyword(Enum):
	CLASS = 6
	METHOD = 7
	FUNCTION = 8
	CONSTRUCTOR = 9
	INT = 10
	BOOLEAN = 11
	CHAR = 12
	VOID = 13
	VAR = 14
	STATIC = 15
	FIELD = 16
	LET = 17
	DO = 18
	IF = 19
	ELSE = 20
	WHILE = 21
	RETURN = 22
	TRUE = 23
	FALSE = 24
	NULL = 25
	THIS = 26


keyword_dict = {"class": Keyword.CLASS, "method": Keyword.METHOD, "function": Keyword.FUNCTION,
				"constructor": Keyword.CONSTRUCTOR, "int": Keyword.INT, "boolean": Keyword.BOOLEAN,
				"char": Keyword.CHAR, "void": Keyword.VOID, "var": Keyword.VAR,
				"static": Keyword.STATIC, "field": Keyword.FIELD, "let": Keyword.LET,
				"do": Keyword.DO, "if": Keyword.IF, "else": Keyword.ELSE, "while": Keyword.WHILE,
				"return": Keyword.RETURN, "true": Keyword.TRUE, "false": Keyword.FALSE,
				"null": Keyword.NULL, "this": Keyword.THIS}


class Symbol(Enum):
	LEFT_BRACE = 27  # {
	RIGHT_BRACE = 28  # }
	LEFT_PAR = 29  # (
	RIGHT_PAR = 30  # )
	LEFT_BRACKET = 31  # [
	RIGHT_BRACKET = 32  # ]
	DOT = 33  # .
	COMMA = 34  # ,
	SEMICOLON = 35  # ;
	PLUS = 36
	MINUS = 37
	STAR = 38  # *
	FORWARD_SLASH = 39  # /
	AMPERSAND = 40  # &
	PIKE = 41  # |
	LESS_THAN = 42  # <
	GREATER_THAN = 43  # >
	EQUALS = 44  # =
	TILDE = 45  # ~


symbols_dict = {"{": Symbol.LEFT_BRACE, "}": Symbol.RIGHT_BRACE, "(": Symbol.LEFT_PAR,
				")": Symbol.RIGHT_PAR, "[": Symbol.LEFT_BRACKET, "]": Symbol.RIGHT_BRACKET,
				".": Symbol.DOT, ",": Symbol.COMMA, ";": Symbol.SEMICOLON, "+": Symbol.PLUS,
				"-": Symbol.MINUS, "*": Symbol.STAR, "/": Symbol.FORWARD_SLASH,
				"&": Symbol.AMPERSAND, "|": Symbol.PIKE, "<": Symbol.LESS_THAN,
				">": Symbol.GREATER_THAN, "=": Symbol.EQUALS, "~": Symbol.TILDE}

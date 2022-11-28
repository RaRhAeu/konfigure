from pydantic import constr

StrDict = dict[str, str]
UnicodeStr = constr(min_length=1, max_length=255, strip_whitespace=True)

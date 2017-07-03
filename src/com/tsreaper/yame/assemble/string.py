from com.tsreaper.yame.assemble.assemble_exception import AssembleException

# ------------------------------------------------------------------------------
# Find the value of a string
# ------------------------------------------------------------------------------
def value_of(s):
    res = eval(s)
    if not isinstance(res, str):
        raise AssembleException('Invalid string "%s".' % (s))
    return res

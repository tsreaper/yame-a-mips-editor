from com.tsreaper.yame.assemble.assemble_exception import AssembleException
from com.tsreaper.yame.constant.register_list import *

# ------------------------------------------------------------------------------
# Find the id of a register
# ------------------------------------------------------------------------------
def value_of(reg):
    reg = reg.lower()
    
    if reg in REGISTER_LIST:
        return REGISTER_LIST.index(reg)
    if reg in REGISTER_NUM_LIST:
        return REGISTER_NUM_LIST.index(reg)
    raise AssembleException('Invalid register "%s".' % (reg))

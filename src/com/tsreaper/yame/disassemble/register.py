from com.tsreaper.yame.disassemble.disassemble_exception import DisassembleException
from com.tsreaper.yame.constant.register_list import *

# ------------------------------------------------------------------------------
# Get name of a register
# ------------------------------------------------------------------------------
def name_of(idx):
    if idx < 0 or idx >= len(REGISTER_LIST):
        raise DisassembleException('Invalid register index.')
    
    return REGISTER_LIST[idx]

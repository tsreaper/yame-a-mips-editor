import re
import com.tsreaper.yame.assemble.register as register
import com.tsreaper.yame.assemble.immediate as immediate
from com.tsreaper.yame.assemble.assemble_exception import AssembleException
from com.tsreaper.yame.constant.token_regex import *

# ------------------------------------------------------------------------------
# Find the value of an immediate(register)
# ------------------------------------------------------------------------------
def value_of(imm_rs, b):
    try:
        imm, rs = re.search(IMMEDIATE_REGISTER_REGEX, imm_rs).groups()
    except:
        raise AssembleException('Invalid immediate(rs) "%s".' % (imm_rs))
    
    return (immediate.value_of(imm, b), register.value_of(rs))

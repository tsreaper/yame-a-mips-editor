import re
import com.tsreaper.yame.assemble.label as label
from com.tsreaper.yame.assemble.assemble_exception import AssembleException

# ------------------------------------------------------------------------------
# Find the value of an immediate
# ------------------------------------------------------------------------------
def value_of(imm, b = 32):
    if isinstance(imm, str):
        # Deal with character
        while True:
            regex_res = re.search('\'(.+?)\'', imm)
            if regex_res == None:
                break
            
            c = eval('"' + regex_res.group(1) + '"')
            imm = re.sub('\'(.+?)\'', str(ord(c)), imm, 1)
        
        # Deal with label
        while True:
            regex_res = re.search('@(.+?)@', imm)
            if regex_res == None:
                break
            
            addr = label.value_of(regex_res.group(1))
            imm = re.sub('@(.+?)@', hex(addr), imm, 1)
        
        try:
            res = eval(imm.replace('/', '//'))
        except:
            raise AssembleException('Invalid immediate "%s".' % (imm))
    else:
        res = imm
    
    if not isinstance(res, int):
        raise AssembleException('Invalid immediate "%s".' % (imm))
    
    return res & (2**b - 1)

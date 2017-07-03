import com.tsreaper.yame.assemble.immediate as immediate
import com.tsreaper.yame.assemble.string as string
from com.tsreaper.yame.assemble.assemble_exception import AssembleException
from com.tsreaper.yame.constant.instruction_template import *
import com.tsreaper.yame.constant.config as config

def get_binary(operation, operand):
    bin_code = bytearray()
    
    if DATA_INSTRUCTIONS[operation][0] == 'imm':
        # Data about immediates
        b = DATA_INSTRUCTIONS[operation][1]
        
        for o in operand:
            if operation != '.space':
                imm = immediate.value_of(o, b*8)
                for i in range(0, b):
                    bin_code.append((imm>>((b-1-i)*8)) & 0xFF)
            else:
                imm = immediate.value_of(o)
                if imm > config.MEM_SIZE:
                    raise AssembleException('.space consumes too much space.')
                for i in range(0, imm):
                    bin_code.append(0)
    else:
        # Data about strings
        for o in operand:
            s = string.value_of(o)
            for c in s:
                bin_code.append(ord(c))
            if operation == '.asciiz':
                bin_code.append(0)
    
    return bin_code

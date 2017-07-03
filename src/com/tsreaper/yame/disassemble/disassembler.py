import com.tsreaper.yame.disassemble.instruction as instruction
import com.tsreaper.yame.disassemble.data as data
from com.tsreaper.yame.disassemble.disassemble_exception import DisassembleException
import com.tsreaper.yame.constant.config as config

# ------------------------------------------------------------------------------
# Disassemble binary machine code to MIPS code
# ------------------------------------------------------------------------------
def disassemble(mem):
    res = ''
    
    zero = True
    for i in range(config.TEXT_ADDR_LOWER, config.TEXT_ADDR_UPPER+1, 4):
        try:
            code = (int(mem[i])<<24) | (int(mem[i+1])<<16) | (int(mem[i+2])<<8) | int(mem[i+3])
        except:
            raise DisassembleException('Invalid binary file.')
        
        if code != 0:
            if zero:
                res += '.text 0x%08x\n' % (i)
            res += instruction.disassemble_instruction(code, i//4) + '\n'
            zero = False
        else:
            zero = True
    
    zero = True
    for i in range(config.DATA_ADDR_LOWER, config.DATA_ADDR_UPPER+1, 4):
        try:
            code = (int(mem[i])<<24) | (int(mem[i+1])<<16) | (int(mem[i+2])<<8) | int(mem[i+3])
        except:
            raise DisassembleException('Invalid binary file.')
        
        if code != 0:
            if zero:
                res += '.data 0x%08x\n' % (i)
            res += data.disassemble_data(code, i//4) + '\n'
            zero = False
        else:
            zero = True
    
    return res

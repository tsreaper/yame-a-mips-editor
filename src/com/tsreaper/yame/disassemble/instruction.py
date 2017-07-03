import com.tsreaper.yame.disassemble.register as register
from com.tsreaper.yame.disassemble.disassemble_exception import DisassembleException
from com.tsreaper.yame.constant.instruction_template import *

# ------------------------------------------------------------------------------
# Get a signed integer
# ------------------------------------------------------------------------------
def get_signed(x, b = 16):
    if (x>>(b-1)) == 1:
        return x - (2**b)
    else:
        return x

# ------------------------------------------------------------------------------
# Disassemble an R-type instruction
# ------------------------------------------------------------------------------
def disassemble_r_instruction(code):
    rs = (code>>21) & (2**5-1)
    rt = (code>>16) & (2**5-1)
    rd = (code>>11) & (2**5-1)
    sa = (code>>6) & (2**5-1)
    func = code & (2**6-1)
    
    if func not in R_FUNCCODES.keys():
        raise DisassembleException('Invalid function code of R-type instruction.')
    
    # Get operation name and operand
    operation = R_FUNCCODES[func]
    operand = R_INSTRUCTIONS[operation][0]
    res = operation
    
    # Get operand values
    for i in range(0, len(operand)):
        if i > 0:
            res += ','
        if operand[i] == 'rd':
            res += ' ' + register.name_of(rd)
        elif operand[i] == 'rs':
            res += ' ' + register.name_of(rs)
        elif operand[i] == 'rt':
            res += ' ' + register.name_of(rt)
        elif operand[i] == 'sa':
            res += ' %d' % (sa)
    
    return res

# ------------------------------------------------------------------------------
# Disassemble an I-type instruction
# ------------------------------------------------------------------------------
def disassemble_i_instruction(code, stm_num):
    op = (code>>26)
    rs = (code>>21) & (2**5-1)
    rt = (code>>16) & (2**5-1)
    imm = code & (2**16-1)
    
    # Get operation name and operand
    if op == 0b00001:
        if rt == 1:
            operation = 'bgez'
        elif rt == 17:
            operation = 'bgezal'
        elif rt == 0:
            operation = 'bltz'
        elif rt == 16:
            operation = 'bltzal'
    else:
        operation = I_OPCODES[op]
    
    operand = I_INSTRUCTIONS[operation][0]
    res = operation
    
    # Get operand values
    for i in range(0, len(operand)):
        if i > 0:
            res += ','
        if operand[i] == 'rs':
            res += ' ' + register.name_of(rs)
        elif operand[i] == 'rt':
            res += ' ' + register.name_of(rt)
        elif operand[i] == 'imm':
            res += ' 0x%04x' % (imm)
        elif operand[i] == 'imm(rs)':
            res += ' %d(%s)' % (get_signed(imm), register.name_of(rs))
        elif operand[i] == 'label':
            res += ' L%08X' % (get_signed(imm) + stm_num + 1)
    
    return res

# ------------------------------------------------------------------------------
# Disassemble a J-type instruction
# ------------------------------------------------------------------------------
def disassemble_j_instruction(code):
    op = (code>>26)
    imm = code & (2**26-1)
    
    # Get operation name and operand
    operation = J_OPCODES[op]
    operand = J_INSTRUCTIONS[operation][0]
    res = operation
    
    # Get operand values
    for i in range(0, len(operand)):
        if i > 0:
            res += ','
        if operand[i] == 'label':
            res += ' L%08X' % (imm)
    
    return res

# ------------------------------------------------------------------------------
# Disassemble an instruction
# ------------------------------------------------------------------------------
def disassemble_instruction(code, stm_num):
    op = (code>>26)
    if op == 0b000000:
        # R-type instruction
        res = disassemble_r_instruction(code)
    elif op in I_OPCODES.keys():
        # I-type instruction
        res = disassemble_i_instruction(code, stm_num)
    elif op in J_OPCODES.keys():
        # J-type instruction
        res = disassemble_j_instruction(code)
    else:
        raise DisassembleException('Invalid operation code.')
    
    return ('L%08X: ' % (stm_num)) + res

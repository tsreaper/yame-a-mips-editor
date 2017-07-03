import com.tsreaper.yame.assemble.register as register
import com.tsreaper.yame.assemble.immediate as immediate
import com.tsreaper.yame.assemble.immediate_register as immediate_register
import com.tsreaper.yame.assemble.label as label
from com.tsreaper.yame.assemble.assemble_exception import AssembleException
from com.tsreaper.yame.constant.instruction_template import *

# ------------------------------------------------------------------------------
# Get binary machine code of an R-type instruction
# ------------------------------------------------------------------------------
def get_r_binary(operation, operand):
    t = R_INSTRUCTIONS[operation]
    
    if len(operand) != len(t[0]):
        # Unexpected number of operand
        raise AssembleException('Unexpected number of operand.')
    
    # Read values from operand
    rs, rt, rd, sa, func = (0, 0, 0, 0, t[1])
    for i in range(0, len(t[0])):
        if t[0][i] == 'rd':
            rd = register.value_of(operand[i])
        elif t[0][i] == 'rs':
            rs = register.value_of(operand[i])
        elif t[0][i] == 'rt':
            rt = register.value_of(operand[i])
        elif t[0][i] == 'sa':
            sa = immediate.value_of(operand[i], 5)
    
    return (rs<<21) | (rt<<16) | (rd<<11) | (sa<<6) | func

# ------------------------------------------------------------------------------
# Get binary machine code of an I-type instruction
# ------------------------------------------------------------------------------
def get_i_binary(operation, operand, addr):
    t = I_INSTRUCTIONS[operation]
    
    if len(operand) != len(t[0]):
        # Unexpected number of operand
        raise AssembleException('Unexpected number of operand.')
    
    # Read values from operand
    op, rs, rt, imm = (t[1], 0, 0, 0)
    
    if operation == 'bgez':
        rt = 1
    elif operation == 'bgezal':
        rt = 17
    elif operation == 'bltz':
        rt = 0
    elif operation == 'bltzal':
        rt = 16
    
    for i in range(0, len(t[0])):
        if t[0][i] == 'rs':
            rs = register.value_of(operand[i])
        elif t[0][i] == 'rt':
            rt = register.value_of(operand[i])
        elif t[0][i] == 'imm':
            imm = immediate.value_of(operand[i], 16)
        elif t[0][i] == 'imm(rs)':
            imm, rs = immediate_register.value_of(operand[i], 16)
        elif t[0][i] == 'label':
            lbl_addr = label.value_of(operand[i])
            try:
                imm = immediate.value_of((lbl_addr - addr)//4 - 1, 16)
            except:
                # Label too far
                raise AssembleException('Can\'t reach label "%s".' % (operand[i]))
    
    return (op<<26) | (rs<<21) | (rt<<16) | imm

# ------------------------------------------------------------------------------
# Get binary machine code of an J-type instruction
# ------------------------------------------------------------------------------
def get_j_binary(operation, operand):
    t = J_INSTRUCTIONS[operation]
    
    if len(operand) != len(t[0]):
        # Unexpected number of operand
        raise AssembleException('Unexpected number of operand.')
    
    # Read values from operand
    op, imm = (t[1], 0)
    for i in range(0, len(t[0])):
        if t[0][i] == 'label':
            lbl_addr = label.value_of(operand[i])
            try:
                imm = immediate.value_of(lbl_addr//4, 26)
            except:
                # Label too far
                raise AssembleException('Can\'t reach label "%s".' % (operand[i]))
    
    return (op<<26) | imm

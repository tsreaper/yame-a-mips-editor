import re
import com.tsreaper.yame.assemble.instruction as instruction
import com.tsreaper.yame.assemble.pseudo as pseudo
import com.tsreaper.yame.assemble.data as data
import com.tsreaper.yame.assemble.label as label
import com.tsreaper.yame.assemble.immediate as immediate
from com.tsreaper.yame.assemble.assemble_exception import AssembleException
import com.tsreaper.yame.constant.config as config
from com.tsreaper.yame.constant.instruction_template import *
from com.tsreaper.yame.constant.token_regex import *

# Memory
mem = None

# Text segment address
text_addr = None

# Data segment address
data_addr = None

# If current statement is text
is_text = None

# ------------------------------------------------------------------------------
# Split one instruction into tokens
# ------------------------------------------------------------------------------
def split_tokens(text):
    lbl = None
    operation = None
    operand = None
    
    tokens = text.split()
    
    if len(tokens) > 0:
        if tokens[0][-1] == ':':
            # Label
            lbl = tokens[0][:-1]
            tokens.pop(0)
            text = text.replace(lbl+':', '', 1)
        
        if len(tokens) > 0:
            # Operation and operand
            operation = tokens[0]
            text = text.replace(operation, '', 1)
            operand = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', text) if len(tokens) > 1 else []
            
            lst = []
            for o in operand:
                o = o.strip()
                if o != '' and o != ',':
                    lst.append(o)
            operand = lst
    
    return (lbl, operation, operand)

# ------------------------------------------------------------------------------
# Split whole assembly code into lines of tokens
# ------------------------------------------------------------------------------
def split_lines(text):
    # Remove comments
    text = re.sub(COMMENT_REGEX, '', text)
    
    # Get valid lines
    splited = re.split('\n|\r|\n\r', text)
    lines = []
    line_num = 0
    
    # Deal with each statement
    for line in splited:
        line_num += 1
        lines.append([])
        
        for stm in line.split(';'):
            # Get tokens and parse pseudo instructions
            lbl, operation, operand = split_tokens(stm)
            
            try:
                parsed = pseudo.parse_pseudo(lbl, operation, operand, stm)
            except AssembleException as e:
                raise AssembleException('Line %d: ' % (line_num) + str(e))
            
            for real in parsed.split(';'):
                # Parse real instructions
                lines[-1].append(split_tokens(real))
    
    return lines

# ------------------------------------------------------------------------------
# Check text address validity
# ------------------------------------------------------------------------------
def check_text_addr(addr, line_num):
    if addr % 4 != 0:
        raise AssembleException('Line %d: Text segment address 0x%08x is not aligned to 4 bytes.' % (line_num, addr))
    if addr < config.TEXT_ADDR_LOWER or addr > config.TEXT_ADDR_UPPER + 1:
        raise AssembleException('Line %d: Text segment address 0x%08x out of range.' % (line_num, addr))

# ------------------------------------------------------------------------------
# Check data address validity
# ------------------------------------------------------------------------------
def check_data_addr(addr, line_num):
    if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER + 1:
        raise AssembleException('Line %d: Data segment address 0x%08x out of range.' % (line_num, addr))

# ------------------------------------------------------------------------------
# Parse data to binary machine code and record labels
# ------------------------------------------------------------------------------
def process_label_and_data(lbl, operation, operand, line_num):
    global mem, text_addr, data_addr, is_text
    
    addr = text_addr if is_text else data_addr
    processed = True
    
    if operation != None:
        # Process operation
        if operation == '.text':
            # Text segment indicator
            if lbl != None:
                raise AssembleException('Line %d: Unexpected label.' % (line_num))
            
            if len(operand) > 1:
                raise AssembleException('Line %d: Unexpected number of operand.' % (line_num))
            elif len(operand) == 1:
                try:
                    imm = immediate.value_of(operand[0])
                except AssembleException as e:
                    raise AssembleException('Line %d: %s' % (line_num, str(e)))
                text_addr = imm
            
            is_text = True
            check_text_addr(text_addr, line_num)
            
            return (text_addr, True)
        
        elif operation == '.data':
            # Data segment indicator
            if lbl != None:
                raise AssembleException('Line %d: Unexpected label.' % (line_num))
            
            if len(operand) > 1:
                raise AssembleException('Line %d: Unexpected number of operand.' % (line_num))
            elif len(operand) == 1:
                try:
                    imm = immediate.value_of(operand[0])
                except AssembleException as e:
                    raise AssembleException('Line %d: %s' % (line_num, str(e)))
                data_addr = imm
            
            is_text = False
            check_data_addr(data_addr, line_num)
            
            return (data_addr, True)
        
        elif is_text:
            # Text statement
            check_text_addr(text_addr + 4, line_num)
            text_addr += 4
            processed = False
            
        else:
            # Data statement
            try:
                if operation.lower() not in DATA_INSTRUCTIONS.keys():
                    raise AssembleException('Unknown operation "%s" in data segment.' % (operation))
                data_arr = data.get_binary(operation, operand)
            except AssembleException as e:
                raise AssembleException('Line %d: %s' % (line_num, str(e)))
            
            check_data_addr(data_addr + len(data_arr), line_num)
            for i in range(0, len(data_arr)):
                mem[data_addr + i] = data_arr[i]
            data_addr += len(data_arr)
    
    if lbl != None:
        # Process label
        try:
            label.insert(lbl, addr)
        except AssembleException as e:
            raise AssembleException('Line %d: %s' % (line_num, str(e)))
    
    return (addr, processed)

# ------------------------------------------------------------------------------
# Parse text to binary machine code
# ------------------------------------------------------------------------------
def process_text(operation, operand, addr, line_num):
    try:
        if operation in R_INSTRUCTIONS.keys():
            bin_code = instruction.get_r_binary(operation, operand)
        elif operation in I_INSTRUCTIONS.keys():
            bin_code = instruction.get_i_binary(operation, operand, addr)
        elif operation in J_INSTRUCTIONS.keys():
            bin_code = instruction.get_j_binary(operation, operand)
        else:
            raise AssembleException('Unknown operation "%s" in text segment.' % (operation))
    except AssembleException as e:
        raise AssembleException('Line %d: %s' % (line_num, str(e)))
    
    mem[addr] = bin_code >> 24
    mem[addr+1] = (bin_code >> 16) & 0xFF
    mem[addr+2] = (bin_code >> 8) & 0xFF
    mem[addr+3] = bin_code & 0XFF

# ------------------------------------------------------------------------------
# Assemble MIPS code to binary machine code
# ------------------------------------------------------------------------------
def assemble(text):
    global mem, text_addr, data_addr, is_text
    
    # Init
    mem = bytearray(config.MEM_SIZE)
    text_addr = config.TEXT_ADDR_LOWER
    data_addr = config.DATA_ADDR_LOWER
    is_text = True
    label.clear()
    
    # Get lines
    lines = split_lines(text)
    
    # Process labels and data
    texts = []
    for i in range(0, len(lines)):
        for s in lines[i]:
            addr, processed = process_label_and_data(*s, i+1)
            if not processed:
                texts.append((*s[1:], addr, i+1))
    
    # Process texts
    for s in texts:
        process_text(*s)
    
    try:
        return mem, label.value_of('main')
    except:
        return mem, -1

import re
import configparser

from com.tsreaper.yame.assemble.assemble_exception import AssembleException

# Dictionary. Stores pseudo instructions
pseudo_dict = {}

# ------------------------------------------------------------------------------
# Load pseudo instructions from config file
# ------------------------------------------------------------------------------
def load_pseudo(filename):
    conf = configparser.ConfigParser()
    conf.read(filename)
    
    for sec in conf.sections():
        if sec == '`':
            # Skip assembler config
            continue
        
        pseudo_dict[sec] = (conf.getint(sec, 'operand'), conf.get(sec, 'real'))

# ------------------------------------------------------------------------------
# Save pseudo instructions to config file
# ------------------------------------------------------------------------------
def save_pseudo(filename):
    conf = configparser.ConfigParser()
    conf.read(filename)
    conf.clear()
    
    for op in pseudo_dict.keys():
        conf.add_section(op)
        conf.set(op, 'operand', str(pseudo_dict[op][0]))
        conf.set(op, 'real', pseudo_dict[op][1])
    
    conf.write(open(filename, 'w'))

# ------------------------------------------------------------------------------
# Parse pseudo instructions to real instructions
# ------------------------------------------------------------------------------
def parse_pseudo(lbl, operation, operand, stm):
    if operation not in pseudo_dict.keys():
        return stm
    
    num = pseudo_dict[operation][0]
    if num != len(operand):
        raise AssembleException('Unexpected number of operand.')
    
    # Replacing
    statement = pseudo_dict[operation][1]
    for i in range(0, num):
        statement = statement.replace('[%d]' % (i+1), operand[i])
    
    if lbl != None:
        statement = lbl + ': ' + statement
    
    return statement

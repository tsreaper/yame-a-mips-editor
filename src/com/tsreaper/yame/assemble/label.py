import re
from com.tsreaper.yame.assemble.assemble_exception import AssembleException
from com.tsreaper.yame.constant.token_regex import *

# Dictionary. Stores labels and their address
label_dict = {}

# ------------------------------------------------------------------------------
# Insert a new label
# ------------------------------------------------------------------------------
def insert(label, addr):
    if re.search(LABEL_REGEX, label) == None:
        # Invalid format
        raise AssembleException('Invalid label "%s"' % (label))
    if label in label_dict.keys():
        # Duplicate label
        raise AssembleException('Duplicate "%s"' % (label))
    
    label_dict[label] = addr

# ------------------------------------------------------------------------------
# Find the address of a label
# ------------------------------------------------------------------------------
def value_of(label):
    if re.search(LABEL_REGEX, label) == None:
        # Invalid format
        raise AssembleException('Invalid label "%s"' % (label))
    if label not in label_dict.keys():
        # Label not found
        raise AssembleException('Can\'t find label "%s"' % (label))
    
    return label_dict[label]

# ------------------------------------------------------------------------------
# Clear all the stored labels
# ------------------------------------------------------------------------------
def clear():
    label_dict.clear()

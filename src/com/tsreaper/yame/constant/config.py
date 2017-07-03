import configparser

# Config file name
CONFIG_FILE = 'config.cfg'

# Memory size
MEM_SIZE = 256
MAX_MEM_SIZE = 1048576

# Text segment address range
TEXT_ADDR_LOWER = 0x00
TEXT_ADDR_UPPER = 0x7F

# Data segment address range
DATA_ADDR_LOWER = 0x80
DATA_ADDR_UPPER = 0XFF

# ------------------------------------------------------------------------------
# Load config from file
# ------------------------------------------------------------------------------
def load_config(filename):
    global MEM_SIZE, TEXT_ADDR_LOWER, TEXT_ADDR_UPPER, DATA_ADDR_LOWER, DATA_ADDR_UPPER
    
    conf = configparser.ConfigParser()
    conf.read(filename)
    
    MEM_SIZE = conf.getint('`', 'mem_size')
    TEXT_ADDR_LOWER = conf.getint('`', 'text_addr_lower')
    TEXT_ADDR_UPPER = conf.getint('`', 'text_addr_upper')
    DATA_ADDR_LOWER = conf.getint('`', 'data_addr_lower')
    DATA_ADDR_UPPER = conf.getint('`', 'data_addr_upper')

# ------------------------------------------------------------------------------
# Save config to file
# ------------------------------------------------------------------------------
def save_config(filename):
    global MEM_SIZE, TEXT_ADDR_LOWER, TEXT_ADDR_UPPER, DATA_ADDR_LOWER, DATA_ADDR_UPPER
    
    conf = configparser.ConfigParser()
    conf.read(filename)
    
    conf.add_section('`')
    conf.set('`', 'mem_size', str(MEM_SIZE))
    conf.set('`', 'text_addr_lower', str(TEXT_ADDR_LOWER))
    conf.set('`', 'text_addr_upper', str(TEXT_ADDR_UPPER))
    conf.set('`', 'data_addr_lower', str(DATA_ADDR_LOWER))
    conf.set('`', 'data_addr_upper', str(DATA_ADDR_UPPER))
    
    conf.write(open(filename, 'w'))

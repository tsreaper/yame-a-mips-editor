import re
from com.tsreaper.yame.io.file_exception import FileException
import com.tsreaper.yame.constant.config as config

# ------------------------------------------------------------------------------
# Read COE file
# ------------------------------------------------------------------------------
def read(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    
    # Read radix
    radix_res = re.search(r'memory_initialization_radix\s*=\s*(\d+?);', content)
    if radix_res == None:
        raise FileException('Could not read radix info.')
    radix = int(radix_res.group(1))
    if radix != 2 and radix != 10 and radix != 16:
        raise FileException('Invalid radix %d.' % (radix))
    
    # Read data
    data_res = re.search(r'memory_initialization_vector=([\s\S]*?);', content)
    if data_res == None:
        raise FileException('Could not read data.')
    data = data_res.group(1).split(',')
    
    # Parse data
    mem = bytearray(config.MEM_SIZE)
    addr = 0
    
    for v in data:
        v = v.split()[0]
        if radix == 2:
            v = '0b' + v
        elif radix == 16:
            v = '0x' + v
        v = eval(v)
        
        try:
            mem[addr] = (v>>24) & 0xFF
            mem[addr+1] = (v>>16) & 0xFF
            mem[addr+2] = (v>>8) & 0xFF
            mem[addr+3] = v & 0xFF
            addr += 4
        except Exception as e:
            raise FileException('COE file too large.')
    
    return mem

# ------------------------------------------------------------------------------
# Write coe file
# ------------------------------------------------------------------------------
def write(filename, mem):
    file = open(filename, 'w')
    
    content = 'memory_initialization_radix=16;\n'
    content += 'memory_initialization_vector='
    for i in range(0, len(mem), 4):
        v = (int(mem[i])<<24) | (int(mem[i+1])<<16) | (int(mem[i+2])<<8) | int(mem[i+3])
        if i > 0:
            content += ', '
        content += '%08X' % (v)
    content += ';'
    
    file.write(content)
    file.close()

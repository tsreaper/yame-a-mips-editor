import random
import time
from com.tsreaper.yame.simulate.simulation_exception import SimulationException
from com.tsreaper.yame.simulate.simulation_info_exception import SimulationInfoException
from com.tsreaper.yame.constant.register_list import *
import com.tsreaper.yame.constant.config as config

# Maximum number of instruction executed
STEP_LIMIT = 1000000

pc = 0                            # Program counter
init_pc = 0                       # Initial address

mem = bytearray()                 # Memory
init_mem = bytearray()            # Initial memory

reg = [0] * len(REGISTER_LIST)    # Registers
hi, lo = (0, 0)                   # Two special registers

input_data = []                   # Input data for syscall
output_data = ''                  # Output data for syscall

program_end = False               # If simulation is finished

# ------------------------------------------------------------------------------
# Get a signed integer
# ------------------------------------------------------------------------------
def get_signed(x, b = 32):
    if (x>>(b-1)) == 1:
        return x - (2**b)
    else:
        return x

# ------------------------------------------------------------------------------
# Read a null ended string from memory
# ------------------------------------------------------------------------------
def read_string(addr):
    global pc
    
    if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
        raise SimulationException('PC = %d: Trying to read string out of data segment.' % (pc))
    
    ret = ''
    while mem[addr] != 0:
        ret += chr(mem[addr])
        addr += 1
        if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
            raise SimulationException('PC = %d: Trying to read string out of data segment.' % (pc))
    
    return ret

# ------------------------------------------------------------------------------
# Write a null ended string to memory
# ------------------------------------------------------------------------------
def write_string(s, addr, sz):
    global pc
    
    sz = min(sz-1, len(s))
    for i in range(0, sz):
        if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
            raise SimulationException('PC = %d: Trying to write string out of data segment.' % (pc))
        mem[addr] = ord(s[i])
        addr += 1
    
    if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
        raise SimulationException('PC = %d: Trying to write string out of data segment.' % (pc))
    mem[addr] = 0

# ------------------------------------------------------------------------------
# Reset the simulator
# ------------------------------------------------------------------------------
def reset():
    global pc, init_pc, mem, init_mem, reg, hi, lo, input_data, output_data, program_end
    
    # Reset PC
    pc = init_pc
    
    # Reset memory
    mem = bytearray(init_mem)
    
    # Reset registers
    for i in range(0, len(REGISTER_LIST)):
        reg[i] = 0
    reg[29] = config.DATA_ADDR_UPPER + 1
    hi, lo = (0, 0)
    
    input_data = []
    output_data = ''
    
    program_end = False

# ------------------------------------------------------------------------------
# Load machine code for simulation
# ------------------------------------------------------------------------------
def load(_mem, _addr):
    global init_mem, init_pc
    
    init_mem = bytearray(_mem)
    init_pc = _addr
    reset()

# ------------------------------------------------------------------------------
# Run one step of the program
# ------------------------------------------------------------------------------
def step():
    global pc, mem, reg, hi, lo, input_data, output_data, program_end
    
    # Get each part of instruction
    ins = (int(mem[pc])<<24) | (int(mem[pc+1])<<16) | (int(mem[pc+2])<<8) | int(mem[pc+3])
    op = ins>>26
    r1 = (ins>>21) & 0x1F
    r2 = (ins>>16) & 0x1F
    r3 = (ins>>11) & 0x1F
    sa = (ins>>6) & 0x1F
    func = ins & 0x3F
    imm = ins & 0xFFFF
    lbl = ins & 0x3FFFFFF
    
    if pc < config.TEXT_ADDR_LOWER or pc > config.TEXT_ADDR_UPPER:
        program_end = True
        raise SimulationException('PC = %d: Program counter moved out of text segment.' % (pc))
    
    if op == 0x00:
        # R-type instruction
        if func == 0x20:
            # Add
            reg[r3] = (reg[r1] + reg[r2]) & 0xFFFFFFFF
            if (reg[r1]>>31) == (reg[r2]>>31) and (reg[r1]>>31) != (reg[r3]>>31):
                program_end = True
                raise SimulationException('PC = %d: An overflow occurs when performing the add operation.' % (pc))
        
        elif func == 0x21:
            # Addu
            reg[r3] = (reg[r1] + reg[r2]) & 0xFFFFFFFF
        
        elif func == 0x24:
            # And
            reg[r3] = reg[r1] & reg[r2]
        
        elif func == 0x1A:
            # Div
            a = get_signed(reg[r1])
            b = get_signed(reg[r2])
            if b == 0:
                raise SimulationException('PC = %d: Divided by zero when performing the div operation.' % (pc))
            lo = (a // b) & 0xFFFFFFFF
            hi = (a % b) & 0xFFFFFFFF
        
        elif func == 0x1B:
            # Divu
            lo = (reg[r1] // reg[r2]) & 0xFFFFFFFF
            hi = (reg[r1] % reg[r2]) & 0xFFFFFFFF
        
        elif func == 0x09:
            # Jalr
            tmp = reg[r1]
            reg[r3] = pc + 4
            pc = tmp
            return
        
        elif func == 0x08:
            # Jr
            pc = reg[r1]
            return
        
        elif func == 0x10:
            # Mfhi
            reg[r3] = hi
        
        elif func == 0x12:
            # Mflo
            reg[r3] = lo
        
        elif func == 0x11:
            # Mthi
            hi = reg[r1]
        
        elif func == 0x13:
            # Mtlo
            lo = reg[r1]
        
        elif func == 0x18:
            # Mult
            a = get_signed(reg[r1])
            b = get_signed(reg[r2])
            hi = ((a*b)>>32) & 0xFFFFFFFF
            lo = (a*b) & 0xFFFFFFFF
        
        elif func == 0x19:
            # Multu
            hi = ((reg[r1]*reg[r2])>>32) & 0xFFFFFFFF
            lo = (reg[r1]*reg[r2]) & 0xFFFFFFFF
        
        elif func == 0x27:
            # Nor
            reg[r3] = ~(reg[r1] | reg[r2]) & 0xFFFFFFFF
        
        elif func == 0x25:
            # Or
            reg[r3] = reg[r1] | reg[r2]
        
        elif func == 0x00:
            # Sll
            reg[r3] = (reg[r2] << sa) & 0xFFFFFFFF
        
        elif func == 0x04:
            # Sllv
            reg[r3] = (reg[r2] << min(reg[r1], 32)) & 0xFFFFFFFF
        
        elif func == 0x2A:
            # Slt
            if get_signed(reg[r1]) < get_signed(reg[r2]):
                reg[r3] = 1
            else:
                reg[r3] = 0
        
        elif func == 0x2B:
            # Sltu
            if reg[r1] < reg[r2]:
                reg[r3] = 1
            else:
                reg[r3] = 0
        
        elif func == 0x03:
            # Sra
            s = reg[r2] >> 31
            reg[r3] = reg[r2] >> sa
            if s == 1:
                reg[r3] |= ((1<<sa)-1) << (32-sa)
        
        elif func == 0x07:
            # Srav
            s = reg[r2] >> 31
            t = min(reg[r1], 32)
            reg[r3] = reg[r2] >> t
            if s == 1:
                reg[r3] |= ((1<<t)-1) << (32-t)
        
        elif func == 0x02:
            # Srl
            reg[r3] = reg[r2] >> sa
        
        elif func == 0x06:
            # Srlv
            reg[r3] = reg[r2] >> min(reg[r1], 32)
        
        elif func == 0x22:
            # Sub
            reg[r3] = (reg[r1] - reg[r2]) & 0xFFFFFFFF
            if (reg[r1]>>31) == (reg[r2]>>31) and (reg[r1]>>31) != (reg[r3]>>31):
                program_end = True
                raise SimulationException('PC = %d: An overflow occurs when performing the sub operation.' % (pc))
        
        elif func == 0x23:
            # Subu
            reg[r3] = (reg[r1] - reg[r2]) & 0xFFFFFFFF
        
        elif func == 0x0C:
            # Syscall
            if reg[2] == 1:
                # Print integer
                output_data += str(get_signed(reg[4]))
            
            elif reg[2] == 4:
                # Print string
                output_data += read_string(reg[4])
            
            elif reg[2] == 5:
                # Read integer
                if len(input_data) > 0:
                    try:
                        reg[2] = int(input_data[0]) & 0xFFFFFFFF
                        input_data = input_data[1:]
                    except:
                        pass
                else:
                    raise SimulationInfoException('PC = %d: Waiting for integer input. Simulation paused.' % (pc))
            
            elif reg[2] == 8:
                # Read string
                if len(input_data) > 0:
                    write_string(input_data[0], reg[4], reg[5])
                    input_data = input_data[1:]
                else:
                    raise SimulationInfoException('PC = %d: Waiting for string input. Simulation paused.' % (pc))
            
            elif reg[2] == 10:
                # Exit
                program_end = True
                return
            
            elif reg[2] == 11:
                # Print char
                output_data += chr(reg[4] & 0xFF)
            
            elif reg[2] == 12:
                # Read char
                if len(input_data) > 0:
                    reg[4] = ord(input_data[0][0])
                    input_data = input_data[1:]
                else:
                    raise SimulationInfoException('PC = %d: Waiting for char input. Simulation paused.' % (pc))
            
            elif reg[2] == 30:
                # System time
                millis = int(round(time.time() * 1000))
                reg[4] = millis & 0xFFFFFFFF
                reg[5] = (millis>>32) & 0xFFFFFFFF
            
            elif reg[2] == 41:
                # Random int
                reg[4] = random.randint(0, 0xFFFFFFFF)
            
            elif reg[2] == 42:
                # Random int with range
                reg[4] = random.randint(0, reg[5]-1)
            
            else:
                raise SimulationException('PC = %d: Unsupported syscall operation %d.' % (pc, reg[2]))
        
        elif func == 0x26:
            # Xor
            reg[r3] = reg[r1] ^ reg[r2]
    
    elif op == 0x08:
        # Addi
        t = get_signed(imm, 16) & 0xFFFFFFFF
        reg[r2] = (reg[r1] + t) & 0xFFFFFFFF
        if (reg[r1]>>31) == (t>>31) and (reg[r1]>>31) != (reg[r2]>>31):
            program_end = True
            raise SimulationException('PC = %d: An overflow occurs when performing the addi operation.' % (pc))
    
    elif op == 0x09:
        # Addiu
        reg[r2] = (reg[r1] + get_signed(imm, 16)) & 0xFFFFFFFF
    
    elif op == 0x0C:
        # Andi
        reg[r2] = reg[r1] & imm
    
    elif op == 0x04:
        # Beq
        if reg[r1] == reg[r2]:
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x01 and r2 == 1:
        # Bgez
        if get_signed(reg[r1]) >= 0:
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x01 and r2 == 17:
        # Bgezal
        if get_signed(reg[r1]) >= 0:
            reg[31] = pc+4
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x07 and r2 == 0:
        # Bgtz
        if get_signed(reg[r1]) > 0:
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x06 and r2 == 0:
        # Blez
        if get_signed(reg[r1]) <= 0:
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x01 and r2 == 0:
        # Bltz
        if get_signed(reg[r1]) < 0:
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x01 and r2 == 16:
        # Bltzal
        if get_signed(reg[r1]) < 0:
            reg[31] = pc+4
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x05:
        # Bne
        if reg[r1] != reg[r2]:
            pc += get_signed(imm, 16) << 2
    
    elif op == 0x02:
        # J
        pc = (pc&0xF0000000) | (lbl<<2)
        return
    
    elif op == 0x03:
        # Jal
        reg[31] = pc+4
        pc = (pc&0xF0000000) | (lbl<<2)
        return
    
    elif op == 0x20:
        # Lb
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to load signed byte out of data segment.' % (pc))
        reg[r2] = int(mem[addr])
        
        if (reg[r2]>>7) == 1:
            reg[r2] |= 0xFFFFFF00
    
    elif op == 0x24:
        # Lbu
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to load unsigned byte out of data segment.' % (pc))
        reg[r2] = int(mem[addr])
    
    elif op == 0x21:
        # Lh
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr+1 > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to load signed half word out of data segment.' % (pc))
        reg[r2] = (int(mem[addr])<<8) | int(mem[addr+1])
        
        if (reg[r2]>>15) == 1:
            reg[r2] |= 0xFFFF0000
    
    elif op == 0x25:
        # Lhu
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr+1 > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to load unsigned half word out of data segment.' % (pc))
        reg[r2] = (int(mem[addr])<<8) | int(mem[addr+1])
    
    elif op == 0x0F:
        # Lui
        reg[r2] = imm << 16
    
    elif op == 0x23:
        # Lw
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr+3 > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to load word out of data segment.' % (pc))
        reg[r2] = (int(mem[addr])<<24) | (int(mem[addr+1])<<16) | (int(mem[addr+2])<<8) | int(mem[addr+3])
    
    elif op == 0x0D:
        # Ori
        reg[r2] = reg[r1] | imm
    
    elif op == 0x28:
        # Sb
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to store byte out of data segment.' % (pc))
        mem[addr] = reg[r2] & 0xFF
    
    elif op == 0x0A:
        # Slti
        if get_signed(reg[r1]) < get_signed(imm, 16):
            reg[r2] = 1
        else:
            reg[r2] = 0
    
    elif op == 0x0B:
        # Sltiu
        if reg[r1] < imm:
            reg[r2] = 1
        else:
            reg[r2] = 0
    
    elif op == 0x29:
        # Sh
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr+1 > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to store half word out of data segment.' % (pc))
        mem[addr] = (reg[r2]>>8) & 0xFF
        mem[addr+1] = reg[r2] & 0xFF
    
    elif op == 0x2B:
        # Sw
        addr = reg[r1] + get_signed(imm, 16)
        if addr < config.DATA_ADDR_LOWER or addr+3 > config.DATA_ADDR_UPPER:
            program_end = True
            raise SimulationException('PC = %d: Trying to store word out of data segment.' % (pc))
        mem[addr] = reg[r2]>>24
        mem[addr+1] = (reg[r2]>>16) & 0xFF
        mem[addr+2] = (reg[r2]>>8) & 0xFF
        mem[addr+3] = reg[r2] & 0xFF
    
    elif op == 0x0E:
        # Xori
        reg[r2] = reg[r1] ^ imm
    
    else:
        SimulationException('PC = %d: Unsupported instruction.' % (pc))
    
    pc += 4

# ------------------------------------------------------------------------------
# Run all the program
# ------------------------------------------------------------------------------
def run():
    global program_end
    
    for i in range(0, STEP_LIMIT):
        if program_end:
            return
        step()
    
    program_end = True
    raise SimulationException('PC = %d: Too many instructions executed.' % (pc))

# ------------------------------------------------------------------------------
# Get output data of the simulator
# ------------------------------------------------------------------------------
def get_output():
    global output_data
    
    for c in output_data:
        if ord(c) >= 33 and ord(c) <= 126:
            ret = output_data
            output_data = ''
            return ret
    return ''

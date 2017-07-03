R_INSTRUCTIONS = {
    'add': [['rd', 'rs', 'rt'], 0b100000],
    'addu': [['rd', 'rs', 'rt'], 0b100001],
    'and': [['rd', 'rs', 'rt'], 0b100100],
    'break': [[], 0b001101],
    'div': [['rs', 'rt'], 0b011010],
    'divu': [['rs', 'rt'], 0b011011],
    'jalr': [['rd', 'rs'], 0b001001],
    'jr': [['rs'], 0b001000],
    'mfhi': [['rd'], 0b010000],
    'mflo': [['rd'], 0b010010],
    'mthi': [['rs'], 0b010001],
    'mtlo': [['rs'], 0b010011],
    'mult': [['rs', 'rt'], 0b011000],
    'multu': [['rs', 'rt'], 0b011001],
    'nor': [['rd', 'rs', 'rt'], 0b100111],
    'or': [['rd', 'rs', 'rt'], 0b100101],
    'sll': [['rd', 'rt', 'sa'], 0b000000],
    'sllv': [['rd', 'rt', 'rs'], 0b000100],
    'slt': [['rd', 'rs', 'rt'], 0b101010],
    'sltu': [['rd', 'rs', 'rt'], 0b101011],
    'sra': [['rd', 'rt', 'sa'], 0b000011],
    'srav': [['rd', 'rt', 'rs'], 0b000111],
    'srl': [['rd', 'rt', 'sa'], 0b000010],
    'srlv': [['rd', 'rt', 'rs'], 0b000110],
    'sub': [['rd', 'rs', 'rt'], 0b100010],
    'subu': [['rd', 'rs', 'rt'], 0b100011],
    'syscall': [[], 0b001100],
    'xor': [['rd', 'rs', 'rt'], 0b100110],
}

I_INSTRUCTIONS = {
    'addi': [['rt', 'rs', 'imm'], 0b001000],
    'addiu': [['rt', 'rs', 'imm'], 0b001001],
    'andi': [['rt', 'rs', 'imm'], 0b001100],
    'beq': [['rs', 'rt', 'label'], 0b000100],
    'bgez': [['rs', 'label'], 0b000001],
    'bgezal': [['rs', 'label'], 0b000001],
    'bgtz': [['rs', 'label'], 0b000111],
    'blez': [['rs', 'label'], 0b000110],
    'bltz': [['rs', 'label'], 0b000001],
    'bltzal': [['rs', 'label'], 0b000001],
    'bne': [['rs', 'rt', 'label'], 0b000101],
    'lb': [['rt', 'imm(rs)'], 0b100000],
    'lbu': [['rt', 'imm(rs)'], 0b100100],
    'lh': [['rt', 'imm(rs)'], 0b100001],
    'lhu': [['rt', 'imm(rs)'], 0b100101],
    'lui': [['rt', 'imm'], 0b001111],
    'lw': [['rt', 'imm(rs)'], 0b100011],
    'lwc1': [['rt', 'imm(rs)'], 0b110001],
    'ori': [['rt', 'rs', 'imm'], 0b001101],
    'sb': [['rt', 'imm(rs)'], 0b101000],
    'slti': [['rt', 'rs', 'imm'], 0b001010],
    'sltiu': [['rt', 'rs', 'imm'], 0b001011],
    'sh': [['rt', 'imm(rs)'], 0b101001],
    'sw': [['rt', 'imm(rs)'], 0b101011],
    'swc1': [['rt', 'imm(rs)'], 0b111001],
    'xori': [['rt', 'rs', 'imm'], 0b001110],
}

J_INSTRUCTIONS = {
    'j': [['label'], 0b000010],
    'jal': [['label'], 0b000011],
}

DATA_INSTRUCTIONS = {
    '.2byte': ['imm', 2],
    '.4byte': ['imm', 4],
    '.8byte': ['imm', 8],
    '.ascii': ['str', 1],
    '.asciiz': ['str', 1],
    '.byte': ['imm', 1],
    '.dword': ['imm', 8],
    '.half': ['imm', 2],
    '.space': ['imm', 1],
    '.word': ['imm', 4],
}

# Construct "func/op code - operation name" dictionary
R_FUNCCODES = {}
for o in R_INSTRUCTIONS.keys():
    R_FUNCCODES[R_INSTRUCTIONS[o][1]] = o

I_OPCODES = {}
for o in I_INSTRUCTIONS.keys():
    I_OPCODES[I_INSTRUCTIONS[o][1]] = o

J_OPCODES = {}
for o in J_INSTRUCTIONS.keys():
    J_OPCODES[J_INSTRUCTIONS[o][1]] = o

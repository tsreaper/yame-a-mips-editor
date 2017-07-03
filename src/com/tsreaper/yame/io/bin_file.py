from com.tsreaper.yame.io.file_exception import FileException
import com.tsreaper.yame.constant.config as config

# ------------------------------------------------------------------------------
# Read BIN file
# ------------------------------------------------------------------------------
def read(filename):
    file = open(filename, 'rb')
    mem = bytearray(file.read())
    file.close()
    if len(mem) > config.MEM_SIZE:
        raise FileException('BIN file too large.')
    return mem

# ------------------------------------------------------------------------------
# Write BIN file
# ------------------------------------------------------------------------------
def write(filename, mem):
    file = open(filename, 'wb')
    file.write(mem)
    file.close()

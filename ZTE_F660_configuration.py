import sys
import binascii
import struct
import zlib
import os


# also can use header
def validate_header(file_header):
    if(file_header[0x0:0x4] != b'\x04\x03\x02\x01'):
        print('Invalid magic at begining')
        sys.exit()
    if(file_header[0x10:0x14] != b'\x01\x02\x03\x04'):
        print('Invalid magic')
        sys.exit()
    hcrc_calc = binascii.crc32(file_header[0x10:0x28]) & 0xffffffff
    hcrc_stored = struct.unpack('!L', file_header[0x28:0x2c])[
        0]  # unpack as long integer
    print(
        f'hcrc_calculated = {hex(hcrc_calc)} , stored_val = {hex(hcrc_stored)}')

    if(hcrc_calc != hcrc_stored):
        print('header CRC invalid')
        sys.exit()


def disassemble():
    file_header = file.read(0x4c)

    validate_header(file_header)

    # calculating crc on header

    block_buffer_size = struct.unpack('!L', file_header[0x20:0x24])[0]
    cumulate_crc_stored = struct.unpack('!L', file_header[0x24:0x28])[0]
    # relpos_final_block_stored = struct.unpack('!L', file_header[0x1c:0x20])[0]
    print(f'block buffer size = {hex(block_buffer_size)}')

    fout = open(
        f"{filepath}{(filename.split('.'))[0]}_outs/{filepath}{(filename.split('.'))[0]}_disassembled.xml", 'wb')
    cumulate_crc = 0
    while(True):
        block_header = file.read(0x0c)
        if(len(block_header) == 0):
            break
        block_size = struct.unpack('!L', block_header[0x04:0x08])[0]
        print(f'block size = {hex(block_size)}')
        block = file.read(block_size)
        cumulate_crc = binascii.crc32(block, cumulate_crc) & 0xffffffff
        block_decomp = zlib.decompress(block)
        fout.write(block_decomp)

    print(
        f'cumulate_crc_stored = {cumulate_crc_stored}, calculated = {cumulate_crc}')
    if(cumulate_crc_stored != cumulate_crc):
        print("invalid cumulate_crc")
        sys.exit()
    fout.close()


def assemble():

    # ---------------------------------- compressing and storing xml as zlib ----------------------------------------------
    file_data = file.read()

    data_block = zlib.compress(file_data, 9)
    with open(f"{filepath}{(filename.split('.'))[0]}_outs/{((filename.split('.'))[0])}_compressed.zlib", 'wb') as zfile:
        zfile.write(data_block)
        zfile.close()
    print(
        f"zlib file saved {filepath}{(filename.split('.'))[0]}_outs/{((filename.split('.'))[0])}_compressed.zlib\n")

# ----------------------------------block size and xml config file size
    xml_size = struct.pack('!L', (os.path.getsize(filename)))
    block_size = struct.pack('!L', (os.path.getsize(
        f"{filepath}{(filename.split('.'))[0]}_outs/{((filename.split('.'))[0])}_compressed.zlib")))

# --------------------------------- block assembling header----------------------------------------
    # calculating block crc --> hex
    block_crc = struct.pack('!L', (binascii.crc32(data_block) & 0xffffffff))
    # relative position to final block from 0x1c; We are wirtting just one file
    block_relpos = b'\x00\x00\x00\x3c'
    block_buffer = b'\x00\x01\x00\x00'  # temp memory buffer
    next_block_relpos = b'\x00' * 4
    block_info = b'\x00' * 4 + xml_size + block_relpos + block_buffer + block_crc
    block_info_crc = struct.pack('!L', (binascii.crc32(
        b'\x01\x02\x03\x04' + block_info) & 0xffffffff))  # crc val of 0x10:0x28
    block_header = xml_size + block_size + next_block_relpos
    # -----------------printing part-------------------------------------------------------------------
    print(f"xml size = {hex((struct.unpack('!L',xml_size))[0])}\nblock size = {hex((struct.unpack('!L',block_size))[0])}\nblock crc = {hex((struct.unpack('!L',block_crc))[0])}\nblock relpos from 0x1c = {hex((struct.unpack('!L',block_relpos))[0])}\nmemory buffer = {hex((struct.unpack('!L',block_buffer))[0])}\nblock info crc = {hex((struct.unpack('!L',block_info_crc))[0])}\n")

# --------------------------------------writting output----------------------------------------------------------
    build_file = open(
        f"{filepath}{(filename.split('.'))[0]}_outs/{((filename.split('.'))[0])}_assembled.bin", 'wb')
    build_file.write(header + block_info + block_info_crc)
    build_file.write(b'\x00' * 32)
    build_file.write(block_header)
    build_file.write(data_block)
    build_file.close()
    print(
        f"bin file saved {filepath}{(filename.split('.'))[0]}_outs/{((filename.split('.'))[0])}_assembled.bin")


if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("Usage : createF660config.py <-c | -d> <inputfile (xml or bin)> \nexample:createF660config.py -c /config_out/config.xml")
        sys.exit()

    # Complete F660 Header (End-Of-Transmission F660)
    header = b'\x04\x03\x02\x01\x00\x00\x00\x00\x00\x00\x00\x04\x46\x36\x36\x30\x01\x02\x03\x04'
    args = (sys.argv[2]).split('/')
    filename = args[-1]
    filepath = ""
    if(len(args) > 1):
        for i in (args[:len(args) - 1]):
            filepath += i + "/"

    file = open(filepath + filename, 'rb')
    print("Creating a project folder")
    os.system(f"mkdir {filepath}{(filename.split('.'))[0]}_outs")

    if(sys.argv[1] == "-c"):
        assemble()

    elif(sys.argv[1] == "-d"):
        disassemble()
    else:
        print("invalid arguments \nUsage : createF660config.py <-c | -d> <inputfile (xml or bin)>\nexample:createF660config.py -c /config_out/config.xml")

    file.close()

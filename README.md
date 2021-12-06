# ZXHN-F660_Configuration
disassemble and modify configuration bin 

Usages:  createF660config.py <-c | -d> <inputfile (xml or bin)>
          d - disassemble the bin file and extract contains to single xml file.
          c - assemble the xml file to a bin file 

inspired by @SebastienDuval and @ebux

Original post: https://reverseengineering.stackexchange.com/questions/13391/zte-reverse-engineering-config-bin-file-problem?newreg=6df764837fdb4f7ca46f617e63562832

#--------------------------------------------------------------------------------------------------------------------------------------#

(0x00 to 0x4c) in the configuration bin file is the file header. 
(0x00 to 0x14) - F660 header (Literally End of transmission(EOT) F660) in ASCII
(0x18 to 0x1c) - the full xml file size in bytes
(0x1c to 0x20) - contains the offset to final block from the address 0x1c
(0x20 to 0x24) - the memory buffer for the block
(0x24 to 0x28) - CRC32 value for all the block
(0x28 to 0x2c) - CRC32 value of Address 0x10 to 0x28 (file info header)

(0x4c to 0x58) is the header for individual data block (size of 0x0c)
(0x0c to 0x50) - block xml file size in bytes
(0x50 to 0x54) - block size
(0x54 to 0x58) - offset to next block from the address 0x1c  (since we are using only a block this value is 0)

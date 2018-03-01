from array import array

poly = 0xEDB88320
defaulttable = array('L')
for byte in range(256):
    crc = 0
    for bit in range(8):
        if (byte ^ crc) & 1:
            crc = (crc >> 1) ^ poly
        else:
            crc >>= 1
        byte >>= 1
    defaulttable.append(crc)
       
def crc_table(poly = 0xEDB88320):

    table = array('L')
    for byte in range(256):
        crc = 0
        for bit in range(8):
            if (byte ^ crc) & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            byte >>= 1
        table.append(crc)
        
    return table
    
def crc32(string, table=defaulttable):
    value = 0xffffffffL
    
    for ch in string:
        value = table[(ord(ch) ^ value) & 0x000000ffL] ^ (value >> 8)

    return value^0xffffffffL #%1048576

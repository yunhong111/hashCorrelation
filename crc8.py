
def crc8(crc, data, poly):
    data_len = len(data)
    for x in data:
        extract = ord(x)
        for i in range(0, 8):
            sum_value = (crc^extract) & 0x01
            crc >>= 1
            if(sum_value):
                crc ^= poly
            extract >>= 1
    return crc


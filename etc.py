translate_table = str.maketrans(
    "".join([chr(c) for c in range(0, 256)]),
    "".join(["."] * 32 + [chr(c) for c in range(32, 127)] + ["."] * 129)
)

#hex를 label에 넣기전에 포맷팅해주는 함수
def hexViwer(hextext, count):
    return_value = ''

    for x in range(len(hextext)//16):
        h = s = ''
        line = (count * 4096) + (x * 16)
        for y in range(16):
            h += "{:02X} ".format(hextext[x * 16 + y])
        for y in range(16):
            s += chr(translate_table[hextext[x * 16 + y]])
        return_value += '0x{:08X} | {:48}| {:8}\n'.format(line, h, s)

    return return_value


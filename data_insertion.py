def calculate_volume(file, xref_position):
    size_position = xref_position + 8
    i = 0
    while bytes([file[size_position + i]]) != b'\x0d': #b'\x0d'
        i+=1
    size_in_bytes = file[size_position:size_position+i]
    size_in_integer = 0
    for byte in size_in_bytes:
        size_in_integer = size_in_integer*10 + byte - 48
    return size_in_integer-3 #reserved field, begining field, size field


if __name__ == '__main__':
    #file = input('Path for container-file: ')
    file = 'c:\\Users\\Mike\\Downloads\\ETSP.pdf'
    with open(file, 'rb') as f:
        unparsed = f.read()

    #c:\Users\Mike\Downloads\ETSP.pdf
    xref_signature = b'\x78\x72\x65\x66\x0d\x0a'

    xref_position = unparsed.find(xref_signature)
    size_for_hide = calculate_volume(unparsed,xref_position)
    if size_for_hide < 1:
        print('file too small. Can\'t encapsulate any information')
    else:
        print('free capasity - %d bite' %(size_for_hide*16))

    #file = input('Path for file with data: ')
    file = 'c:\\Users\\Mike\\Downloads\\text.txt'
    with open(file, 'rb') as f:
        unparsed_information = f.read()

    information_to_hide = bin(int.from_bytes(unparsed_information, byteorder='big'))
    information_to_hide = information_to_hide[2:]

    information_by_blocks = []
    block_begin = 0
    while block_begin < len(information_to_hide):
        block_end = min(block_begin+16,len(information_to_hide))
        information_by_blocks.append(information_to_hide[block_begin:block_end])
        block_begin += 16

    print(information_by_blocks)

    begin_signature = '0b000010011001101'
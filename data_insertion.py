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


def make_byte_data(block):
    block = '0b' + block
    block = int(block, 2)

    single_number_block = []
    while block > 0:
        number = block % 10
        single_number_block.append(number)
        block = block // 10
    single_number_block.reverse()
    if len(single_number_block) < 5:
        single_number_block = [0]*(5-len(single_number_block)) + single_number_block

    byte_block = bytearray()
    for number in single_number_block:
        byte_block.append(48+number)

    return byte_block

if __name__ == '__main__':
    #file = input('Path for container-file: ')
    file = 'c:\\Users\\Mike\\Downloads\\ETSP.pdf'
    with open(file, 'rb') as f:
        unparsed = f.read()

    #c:\Users\Mike\Downloads\ETSP.pdf
    xref_signature = b'\x78\x72\x65\x66\x0d\x0a' #xref \r \n

    xref_position = unparsed.find(xref_signature)
    size_for_hide = calculate_volume(unparsed,xref_position)
    if size_for_hide < 1:
        print('file too small. Can\'t encapsulate any information')
    else:
        print('free capasity - %d bite' %(size_for_hide*16 - 20)) #20 bit - addition to save the exstension of file


    #file = input('Path for file with data: ')
    file = 'c:\\Users\\Mike\\Downloads\\text.txt'
    with open(file, 'rb') as f:
        unparsed_information = f.read()

    information_to_hide = bin(int.from_bytes(unparsed_information, byteorder='big'))
    information_to_hide = information_to_hide[2:]

    begin_signature = '0000010011001101'

    information_by_blocks = []
    information_by_blocks.append(begin_signature) #adding signature for hidden information

    information_size = bin(len(information_to_hide))[2:]
    if len(information_size) < 16:
        information_size = '0'*(16-len(information_size))+information_size #formating size - adding 0 before size
    information_by_blocks.append(information_size)  #adding size of hidden information

    #number up to 65535 - 16 bit information in every string of pdf xref table
    i = len(file)-1 #extracting extension of file
    while file[i] != '.':
        i-=1
    exstension = file[i+1:]

    exstension_as_bin = '' #encode exstension in binary
    for symbol in exstension:
        symbol_as_number = ord(symbol)-ord('a')
        symbol_as_binary = bin(symbol_as_number)[2:]
        if len(symbol_as_binary) < 5: #converting to 5bit size
            symbol_as_binary = '0'*(5-len(symbol_as_binary))+symbol_as_binary
        exstension_as_bin += symbol_as_binary
    if len(exstension_as_bin) < 20: #if exstension has only 3 letters
        exstension_as_bin = exstension_as_bin + '1'*5 #add a special mark - '11111'
    information_to_hide = exstension_as_bin + information_to_hide #adding exstension of file to information

    #information for write has a format - signature(1 str) + size(1str) + exstension(20bit) + file itself
    block_begin = 0
    while block_begin < len(information_to_hide):
        block_end = min(block_begin+16,len(information_to_hide))
        information_by_blocks.append(information_to_hide[block_begin:block_end])
        block_begin += 16

    reserved_field_position = unparsed.find(b'\x0a', xref_position + 6) #find reserved string
    availible_string_position = unparsed.find(b'\x0a', reserved_field_position + 1) #find next string - first string, which can accept data
    redacted_file = unparsed[:availible_string_position]

    for block in information_by_blocks:
        availible_field_position = availible_string_position + 12 #find position in string, where data will write
        redacted_file += unparsed[availible_string_position:availible_field_position] #copy unnecessary data from main file
        redacted_file += make_byte_data(block)
        availible_string_position = unparsed.find(b'\x0a',  availible_field_position)
        redacted_file += unparsed[availible_field_position+5:availible_string_position] #copy remaining data

    redacted_file += unparsed[availible_string_position:]

    with open(file, 'wb') as f:
        f.write(redacted_file)



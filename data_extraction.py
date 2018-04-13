def parsing_size(size):
    int_size = 0
    for number in size:
        int_size = int_size*10 + number-48
    return int_size

def parsing_5sign_byte(byte_str):
    int_str = 0
    for number in byte_str:
        int_str = int_str * 10 + number - 48
    bin_str = bin(int_str)[2:]
    if len(bin_str) < 16:
        bin_str = '0'*(16-len(bin_str)) + bin_str
    return  bin_str

def parse_extension(bin_str):
    extension = ''
    for i in range(4):
        representation = int('0b' + bin_str[i*5:i*5+5],2)
        if representation < 29:
            extension += chr(ord('a')+representation)
    return extension

if __name__ == '__main__':
    file = input('enter source file: ')
    #file = 'c:\\Users\\Mike\\Downloads\\ETSP.pdf' #file opening
    i = len(file) - 1  # extracting extension of file with information
    while file[i] != '.':
        i -= 1
    pdf_exstension = file[i + 1:]
    if pdf_exstension != 'pdf':
        print('invelid type of file. Use pdf.')
        exit()
    try:
        with open(file, 'rb') as f:
            unparsed_file = f.read()
    except(FileNotFoundError):
        print('there is no such file.')
        exit()

    xref_signature = b'\x78\x72\x65\x66\x0d\x0a'  # xref \r \n
    xref_position = unparsed_file.find(xref_signature) #finding xref signature to minimize collision with hidden file signature

    # check for signature of hidden data
    begin_signature = b'\x30\x31\x32\x32\x39'
    begin_position = unparsed_file.find(begin_signature, xref_position)
    if begin_position == -1:
        print('there is no encapsylated data.')
        exit()

    #extracting size
    size_position = begin_position+20
    size = unparsed_file[size_position:size_position+5]
    size = parsing_size(size)

    #extracting information
    size_with_extension = size + 20
    information_position = size_position + 20

    #calculating number of blocks, which stores information
    number_of_blocks = size_with_extension // 16
    if size_with_extension % 16 != 0:
        number_of_blocks += 1

    #extracting information from source file
    information_in_bin = ''
    for i in range(number_of_blocks):
        information_in_byte = unparsed_file[information_position:information_position+5]
        information_in_bin += parsing_5sign_byte(information_in_byte)
        information_position += 20

    extension = parse_extension(information_in_bin[:20])
    information = information_in_bin[20:20+size]

    #writing file
    extracted_file = 'extracted_file.'+extension
    with open(extracted_file, 'wb') as f:
        for i in range(len(information)//8):
            current_byte = '0b' + information[i*8:i*8+8]
            current_byte = int(current_byte, 2)
            byte_to_write = bytes([current_byte])
            f.write(byte_to_write)
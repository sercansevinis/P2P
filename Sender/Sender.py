import socket
import os
import math

s = socket.socket()
s.bind((socket.gethostname(), 8081))
s.listen(1)

print(socket.gethostname())

print('waiting for connections...')
conn, address = s.accept()
print(address, ' connected to server')

while 1:
    print("press 1 for send a file \npress 0 to exit program")
    choice = input()
    if choice == '1':
        name = input(str('enter the filename: '))

        filename = name + '.png'
        c = os.path.getsize(filename)
        CHUNK_SIZE = math.ceil(math.ceil(c) / 4)
        index = 1
        with open(filename, 'rb') as infile:
            chunk = infile.read(int(CHUNK_SIZE))
            while chunk:
                chunk_name = name+ '_' + str(index)
                with open(chunk_name, 'wb+') as chunk_file:
                    chunk_file.write(chunk)
                index += 1
                chunk = infile.read(int(CHUNK_SIZE))
        chunk_file.close()

        i = 1
        for x in range(4):
            fname = name + '_' + str(i)
            fi = open(fname, 'rb')
            f_d = fi.read(51200)
            conn.send(f_d)
            i += 1
        print('file sended')
        continue
    elif choice == '0':
        print('ending program...')
        break
    else:
        print('wrong input')
        continue

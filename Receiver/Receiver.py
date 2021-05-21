import socket
import math
import os
import shutil

host = input(str("Please write the computer host name of the sender:"))
s = socket.socket()
port = 8081
s.connect((host, port))
print("Connected to " + host)

while 1:
    print("press 1 if you want to download the file \npress 0 to exit program")
    choice = input()
    if choice == '1':
        name = input(str('Write the file name without extension:'))
        i = 1
        for x in range(4):
            full_name = name + '_' + str(i)
            f_d = s.recv(51200)
            fi = open(full_name, 'wb')
            fi.write(f_d)
            fi.close()
            i += 1
        chunk_names = [name + '_1', name + '_2', name + '_3', name + '_4']
        with open(name + '.png', 'wb') as outfile:
            for chunk in chunk_names:
                with open(chunk, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)
        print('File downloaded')
        continue
    elif choice == '0':
        print('Ending the program...')
        break
    else:
        print('Type either 1 or 0 !')
        continue

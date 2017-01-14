import os, random, struct
from Crypto.Cipher import AES
import hashlib
from Tkinter import Tk
from tkFileDialog import askopenfilename
import time
import string
import getpass
from msvcrt import getch
import ntpath
import Tkinter, tkFileDialog
import easygui
from os.path import basename

def encrypt_file(key, in_filename, out_filename, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]
    # Random IV generator
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    # Type of encryption
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    # get the file size
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename, chunksize=64*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

# Main Function ------------------------------------------------------------

def maindef():
    password = ''
    choise = raw_input("[*] (E)ncrypt or (D)ecrypt: ")
    if choise == "E" or choise == "e":
        folfil = raw_input("[*] A single file or a directory? (S/D): ")
        if folfil == "S" or folfil == "s":
            cls()
            encryptfile(password)
        elif folfil == "D" or folfil == "d":
            cls()
            encryptdirec()
        else:
            print("[*] Invalid option! Insert S/s or D/d")
            maindef()
    elif choise == "D" or choise == "d":
        folfil = raw_input("[*] A single file or a directory? (S/D): ")
        if folfil == "S" or folfil == "s":
            cls()
            decryptfile()
        elif folfil == "D" or folfil == "d":
            cls()
            decryptdirect()
        else:
            cls()
            print("[*] Invalid option! Insert S/s or D/d")
            maindef()
    else:
        cls()
        print("[*] Invalid option! Insert E/e or D/d")
        maindef()


# Encrypt/Decrypt single file
def encryptfile(password):

    print("*------------------------------*")
    print("*                              *")
    print("*    [*] Encrypt File [*]      *")
    print("*                              *")
    print("*------------------------------*")

    if len(password) == 0:
        password = getpass.getpass('[*] Choose a strong password(size 10 at least): ')
    if len(password) < 10:
        print("[*] Password size is less than 10!")
        encryptfile(password)
    elif len(password) >= 10:
        verfpassword(password, verf=[has_lowercase, has_numeric, has_special])
        if " " in password:
            print("[*] Invalid password, please remove the blanks.")
            encryptfile(password)
        print("[*] Look over your shoulder!")
        review = raw_input("[*] Do you want to review your password? yes/no: ")
        if review == "yes":
            print (password)
            print("[*] If you want to change the password, press TAB")
            print("[*] If you want to continue, press ENTER")
            while True:
                key = ord(getch())
                if key == 13:  # Enter
                    encryptkey(password)
                elif key == 9:  # TAB
                    password = ' '
                    encryptfile(password)
                else:
                    print("[*] Invalid option!")
                    cls()
                    encryptfile()
        elif review == "no":
            encryptkey(password)
        else:
            cls()
            print("[*] Invalid option!")
            encryptfile(password)
    else:
        password = ''
        cls()
        print("[*] Some error occurred! " )
        encryptfile(password)

def encryptkey(password):
    key = hashlib.sha256(password).digest()
    print("[*] Select a file to encrypt")
    Tk().withdraw()
    in_filename = askopenfilename()
    if len(in_filename) == 0:
        cls()
        print ("[*] Error! You have to select a file!")
        encryptkey(password)
    if in_filename.lower().endswith('.enc'):
        print("[*] Warning! The file is allready with the extension .enc, if you don't want to encrypt close the program.")
    '\\'.join(in_filename.split('\\')[0:-1])
    print("[*] The default name of the output file is: " + in_filename + ".enc")
    out_filename = (in_filename + ".enc")
    out_filename = out_filename.replace('/', "\\")
    change = raw_input("[*] Do you want to change it? (Y/N): ")
    if change == "Y" or change == "y":
        out_filename = raw_input("[*] Insert the output file name: ")
        out_filename = out_filename + ".enc"
        remove = raw_input("[*] Delete the original after encrypting? (Y/N): ")
        if remove == "Y" or remove == "y":
            print(in_filename)
            encrypt_file(key, in_filename, out_filename, chunksize=64*1024)
            os.remove(in_filename)
            maindef()
        elif remove == "N" or remove == "n":
            encrypt_file(key, in_filename, out_filename, chunksize=64*1024)
            maindef()
        else:
            print("[*] Invalid option!")
            cls()
            encryptkey(password)
    elif change == "N" or change == "n":
        #in_filename = ntpath.basename(in_filename)
        print("[*] The file will be encrypted and the output name is " + in_filename + ".enc")
        remove = raw_input("[*] Delete the original after encrypting? (Y/N): ")
        if remove == "Y" or remove == "y":
            encrypt_file(key, in_filename, out_filename, chunksize=64*1024)
            print('[*] Alert! The file is now encrypted.')
            os.remove(in_filename)
            maindef()
        elif remove == "N" or remove == "n":
            encrypt_file(key, in_filename, out_filename, chunksize=64*1024)
            print("[*] Alert! The file is now encrypted.")
            maindef()
        else:
            cls()
            print("[*] Invalid option!")
            encryptfile()
    else:
        cls()
        print("[*] Invalid option!")
        encryptkey(password)

def decryptfile():
    print("*------------------------------*")
    print("*                              *")
    print("*    [*] Decrypt File [*]      *")
    print("*                              *")
    print("*------------------------------*")
    # recebe a password
    password = getpass.getpass("[*] Insert the decryption password: ")
    print("[*] If you choose wrong the password the file will not be decrypted correctly!")
    # converte a password numa chave de 32 bits
    key = hashlib.sha256(password).digest()
    print("[*] Select the encrypted file")
    Tk().withdraw() 
    in_filename = askopenfilename()
    if len(in_filename) == 0:
        cls()
        print ("[*] Error! You have to select a file!")
        decryptfile()
    if in_filename.lower().endswith('.enc'):
        print("[*] The default name of the output file is: " + os.path.splitext(in_filename)[0])
        pathc = raw_input("[*] Change the path to save the decrypted file? (Y/N): ")
        if pathc == "Y" or pathc == "y":
            print("[*] Choose the path to save the file: ")
            root = Tkinter.Tk()
            path = tkFileDialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')
            t_filename = os.path.splitext(in_filename)[0]
            out_filename = path + "\\" + basename(t_filename)
            remove = raw_input("[*] Delete the encrypted file after decrypting? (Y/N): ")
            if remove == "Y" or remove == "y":
                decrypt_file(key, in_filename, out_filename, chunksize=24*1024)
                os.remove(in_filename)
                maindef()
            elif remove == "N" or remove == "n":
                decrypt_file(key, in_filename, out_filename, chunksize=24*1024)
                maindef()
            else:
                cls()
                print("[*] Invalid option!")
                encryptfile()
        elif pathc == "N" or pathc == "n":
            print("[*] The file will be saved on the same directory than the encrypted file.")
            remove = raw_input("[*] Delete the encrypted file after decrypting? (Y/N): ")
            if remove == "Y" or remove == "y":
                decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024)
                os.remove(in_filename)
                maindef()
            elif remove == "N" or remove == "n":
                decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024)
                maindef()
            else:
                cls()
                print("[*] Invalid option!")
                encryptfile()
        else:
            cls()
            print("[*] Invalid option!")
            decryptfile()
    else:
        cls()
        print("[*] The file is not encrypted!")
        print("[*] Choose another file")
        decryptfile()
# --------------------

# Encrypt/decrypt directory
def encryptdirec():
    print("*------------------------------*")
    print("*                              *")
    print("*  [*] Encrypt Directory [*]   *")
    print("*                              *")
    print("*------------------------------*")
    password = getpass.getpass("[*] Choose a strong password(size 10 at least): ")
    if len(password) < 10:
        print("[*] Password size is less than 10!")
        encryptdirec()
    elif len(password) >= 10:
        verfpassword(password, verf=[has_lowercase, has_numeric, has_special])
        if " " in password:
            print("[*] Invalid password, please remove the blanks.")
            encryptfile()
        print("[*] Look over your shoulder!")
        review = raw_input("[*] Do you want to review your password? yes/no: ")
        if review == "yes":
            print ("[*] The password is: " + password)
            print("[*] If you want to change the password, press TAB")
            print("[*] If you want to continue, press ENTER")
            while True:
                key = ord(getch())
                if key == 13:  # Enter
                    encryptdirkey(password)
                elif key == 9:  # Tab
                    password = ' '
                    encryptdirec()
                else:
                    cls()
                    print("[*] Invalid option!")
                    encryptdirec()
        elif review == "no":
            encryptdirkey(password)
        else:
            cls()
            print("[*] Invalid option!")
            encryptdirec()
    else:
        cls()
        print("[*] Some error occurred! " )
        encryptdirec()

def encryptdirkey(password):
    key = hashlib.sha256(password).digest()
    print("[*] Select a directory to encrypt:")
    root = Tkinter.Tk()
    dirname = tkFileDialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')
    if len(dirname) > 0:
        print("[*] 1 - Encrypt all files on the folder.")
        print("[*] 2 - Encrypt all files on the folder exccept the .enc files.")
        print("[*] 3 - Choose a type of extension to encrypt.")
        opt = raw_input("[*] Select one of the options: ")
        if opt == "1":
            option1(dirname, key)
        elif opt == "2":
            option2(dirname, key)
        elif opt == "3":
            option3(dirname, key)
        else:
            cls()
            print("[*] Error! Invalid option")
            encryptdirkey(password)
    else:
        cls()
        print("[*] Please select a directory.")
        encryptdirec()

def option1(dirname, key):
    print("[*] This will encrypt all files including allready encrypted files!")
    remove = raw_input("[*] Delete the originals after encrypting? (Y/N)")
    if remove == "Y" or remove == "y":
        cfiles = []
        for root, dirs, files in os.walk(dirname):
            for in_filename in files:
                cfiles.append(os.path.join(root, in_filename))
        for x in range(0, len(cfiles)):
            out_filename = (cfiles[x] + ".enc")
            out_filename = out_filename.replace('/', "\\")
            encrypt_file(key, cfiles[x], out_filename, chunksize=64 * 1024)
            os.remove(cfiles[x])
        maindef()
    elif remove == "N" or remove == "n":
        cfiles = []
        for root, dirs, files in os.walk(dirname):
            for in_filename in files:
                cfiles.append(os.path.join(root, in_filename))
        for x in range(0, len(cfiles)):
            out_filename = (cfiles[x] + ".enc")
            out_filename = out_filename.replace('/', "\\")
            encrypt_file(key, cfiles[x], out_filename, chunksize=64 * 1024)
        maindef()
    else:
        cls()
        print("[*] Invalid option!")
        encryptdirec()

def option2(dirname, key):
    print("[*] This will encrypt all files exccept the .enc files.")
    remove = raw_input("[*] Delete the originals after encrypting? (S/N)")
    if remove == "S" or remove == "s":
        for in_filename in os.listdir(dirname):
            if not in_filename.lower().endswith('.enc'):
                file = dirname + "/" + in_filename
                out_filename = (file + ".enc")
                encrypt_file(key, file, out_filename, chunksize=64 * 1024)
                os.remove(file)
            else:
                continue
        maindef()
    elif remove == "N" or remove == "n":
        for in_filename in os.listdir(dirname):
            file = dirname + "/" + in_filename
            if not file.lower().endswith('.enc'):
                out_filename = (file + ".enc")
                encrypt_file(key, file, out_filename, chunksize=64 * 1024)
            else:
                continue
        maindef()
    else:
        cls()
        print("[*] Invalid option!")
        encryptdirec()

def option3(dirname, key):
    print("[*] This will encrypt all files with the given extension.")
    print("[*] If you choose a non existing extension, none of the files will be encrypted correctly!")
    exten = raw_input("[*] Insert the entended extension to encrypt (ex: txt): ")
    remove = raw_input("[*] Delete the originals after encrypting? (Y/N)")
    if remove == "Y" or remove == "y":
        for in_filename in os.listdir(dirname):
            if in_filename.lower().endswith(exten):
                file = dirname + "/" + in_filename
                out_filename = (file + ".enc")
                encrypt_file(key, file, out_filename, chunksize=64 * 1024)
                os.remove(file)
            else:
                continue
        maindef()
    elif remove == "N" or remove == "n":
        for in_filename in os.listdir(dirname):
            file = dirname + "/" + in_filename
            if file.lower().endswith(exten):
                out_filename = (file + ".enc")
                encrypt_file(key, file, out_filename, chunksize=64 * 1024)
            else:
                continue
        maindef()
    else:
        cls()
        print("[*] Invalid option!")
        encryptdirec()

def decryptdirect():
    print("*------------------------------*")
    print("*                              *")
    print("*  [*] Decrypt Directory [*]   *")
    print("*                              *")
    print("*------------------------------*")
    # recebe a password
    password = getpass.getpass("[*] Insert a decryption password: ")
    print("[*] If you choose wrong the password the file will not be decrypted correctly!")
    key = hashlib.sha256(password).digest()
    print("[*] Select the directory where files are encrypted")
    root = Tkinter.Tk()
    dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
    if len(dirname) > 0:
        decryptdirkey(dirname, key)
    else:
        cls()
        print("[*] Please select a directory.")
        decryptdirec()

def decryptdirkey(dirname , key):
    print("[*] 1 - Decrypt all encrypted files on the folder.")
    print("[*] 2 - Decrypt only give extension file")
    opt = raw_input("Select one of the options: ")
    if opt == "1":
        decryptopt1(dirname , key)
    elif opt == "2":
        decryptopt2(dirname , key)
    else:
        cls()
        print("[*] Invalid option.")
        decryptdirkey(dirname, key)

def decryptopt1(dirname , key):
    print("[*] This will decrypt all encrypted files.")
    remove = raw_input("[*] Delete the originals after encrypting? (Y/N)")
    if remove == "Y" or remove == "y":
        cfiles = []
        for root, dirs, files in os.walk(dirname):
            for in_filename in files:
                cfiles.append(os.path.join(root, in_filename))
        for x in range(0, len(cfiles)):
            decrypt_file(key, cfiles[x], out_filename=None, chunksize=64 * 1024)
            os.remove(cfiles[x])
        maindef()
    elif remove == "N" or remove == "n":
        cfiles = []
        for root, dirs, files in os.walk(dirname):
            for in_filename in files:
                cfiles.append(os.path.join(root, in_filename))
        for x in range(0, len(cfiles)):
            decrypt_file(key, cfiles[x], out_filename=None, chunksize=64 * 1024)
        maindef()
    #in_filename = raw_input("Insert the name of the file: ")
    else:
        print("[*] Invalid option!")
        decryptopt1(dirname, key)

def decryptopt2(dirname , key):
    print("[*] This will decrypt all files with the given extension.")
    print("[*] If you choose a non existing extension, none of the files will be decrypted!")
    exten = raw_input("[*] Insert the entended extension to encrypt (ex: txt): ")
    remove = raw_input("[*] Delete the originals after encrypting? (Y/N)")
    if remove == "Y" or remove == "y":
        cfiles = []
        for root, dirs, files in os.walk(dirname):
            for in_filename in files:
                if in_filename.lower().endswith(exten):
                    cfiles.append(os.path.join(root, in_filename))
                    for x in range(0, len(cfiles)):
                        decrypt_file(key, cfiles[x], out_filename=None, chunksize=64 * 1024)
                        os.remove(cfiles[x])
            else:
                continue
        maindef()
    elif remove == "N" or remove == "n":
        cfiles = []
        for root, dirs, files in os.walk(dirname):
            for in_filename in files:
                if in_filename.lower().endswith(exten):
                    cfiles.append(os.path.join(root, in_filename))
                    for x in range(0, len(cfiles)):
                        decrypt_file(key, cfiles[x], out_filename=None, chunksize=64 * 1024)
            else:
                continue
        maindef()
    else:
        print("[*] Invalid option!")
        decryptopt2(dirname, key)
# ----------------------------


def has_lowercase(password):
    'Password must contain a lowercase letter'
    return len(set(string.ascii_lowercase).intersection(password)) > 0

def has_numeric(password):
    'Password must contain a digit'
    return len(set(string.digits).intersection(password)) > 0

def has_special(password):
    'Password must contain a special character'
    return len(set(string.punctuation).intersection(password)) > 0

def verfpassword(password, verf=[has_lowercase, has_numeric, has_special]):
    for test in verf:
        if not test(password):
            print("[*] Password invalid. As to containt at least one letter, one number and one special caracter.")
            maindef()
    return True
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

maindef()

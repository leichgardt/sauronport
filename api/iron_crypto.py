from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import atfork
from base64 import b64decode

key_pair = RSA.generate(1024)
private_key = open("private_key.pem", "wb")
private_key.write(key_pair.exportKey())
private_key.close()
public_key = open("public_key.pem", "wb")
public_key.write(key_pair.publickey().exportKey())
public_key.close()


class RSADecoder:
    def __init__(self):
        self.__private_key = ''
        self.__key = ''
        self.__cipher = ''
        # atfork()

    def decode(self, secret):
        if self.__private_key is '':
            file = open("private_key.pem", "r")
            self.__private_key = file.read()
            file.close()
        self.__key = RSA.importKey(self.__private_key)
        self.__cipher = PKCS1_OAEP.new(self.__key, hashAlgo=SHA256)
        return self.__cipher.decrypt(b64decode(secret))


# def rsa_decode(secret):
#     with open("private_key.pem", "r") as file:
#         private_key = file.read()
#         key = RSA.importKey(private_key)
#         cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
#         return cipher.decrypt(b64decode(secret))

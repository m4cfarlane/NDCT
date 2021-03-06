import base64
import os
import hashlib
import json

from ast import literal_eval
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ndct.core.paths import KEY_PATH, DB_PATH
from ndct.core.log import log

class Crypt:
	@staticmethod
	def generate_key():
		'''
			Summary:
			Generate a key used for symmetric encryption, using the hash of a user entered password for the salt.

			Returns:
			Encryption key

			Encryption type: 
			128-bit AES
		'''
		if os.path.isfile(KEY_PATH):
			log("Using existing key '{}' for encryption/decryption".format(KEY_PATH), 'info')
			key = Crypt.get_key()

			return key
		else:
			log("Attempting to use '{}' but no key found, create a new key or add an existing one".format(KEY_PATH), 'info')

			password = getpass(prompt='New encryption key password: ')
			password_bytes = password.encode()
			salt = os.urandom(16)
			kdf = PBKDF2HMAC(
				algorithm=hashes.SHA256(),
				length=32,
				salt=salt,
				iterations=100000,
				backend=default_backend()
			)
			key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

			with open(KEY_PATH, 'wb') as encryption_key:
				encryption_key.write(key)

			log("Stored encryption key as '{}'".format(KEY_PATH), 'info')

			return key
	
	@staticmethod
	def get_key():
		'''
			Summary:
			Get stored encryption key.

			Returns:
			Encryption key

			Encryption type:
			128-bit AES
		'''
		with open(KEY_PATH, 'rb') as encryption_key:
			key = encryption_key.read()

		return key

	@staticmethod
	def create_encrypted_file(filename, data):
		'''
			Summary:
			Create an encrypted file from data that is passed to the function.

			Takes: 
			filename: Name of encrypted file
			data: Data to encrypt
		'''
		key = Crypt.generate_key()
		
		fernet = Fernet(key)
		encrypted_data = fernet.encrypt(str(data).encode())
		
		with open(DB_PATH + filename, 'wb') as encrypted_file:
			encrypted_file.write(encrypted_data)

	@staticmethod
	def get_encrypted_file_contents(filename):
		'''
			Summary:
			Get the contents of an encrypted file to enable use of the stored data.

			Takes: 
			filename: Name of file to get decrypted contents of

			Returns:
			Decrypted file contents 
		'''
		key = Crypt.generate_key()

		with open(DB_PATH + filename, 'rb') as encrypted_file:
			data = encrypted_file.read()

		fernet = Fernet(key)
		temp_data = fernet.decrypt(data).decode()
		temp_data_list = literal_eval(temp_data)

		return temp_data_list
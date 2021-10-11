import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

import socket
import pickle

from utils.fetchingfiles import file_system_tree_creation
from tkinter import Tk
from tkinter.filedialog import askdirectory

HEADER_LENGTH = 20
HOST_NAME = socket.gethostname()
PORT = 3030
HOST_IP = socket.gethostbyname(HOST_NAME)


class ServerHub:
	def __init__(self, server_socket, host, port):
		self.__server_socket = server_socket
		self.__client_socket = None
		try:
			self.__server_socket.bind((host, port))
			self.__server_socket.listen(5)
			print(f"server is listening on {port} with ip {host}")
		except Exception as e:
			print(e)


	def accept_connection(self):
		self.__client_socket, client_address = self.__server_socket.accept()
		print(f"Connection accepted from {client_address}")


	def receive_packet(self, header_length):
		packet_header = self.__client_socket.recv(header_length)
		packet_length = int(packet_header.decode('utf-8').strip())
		packet = self.__client_socket.recv(packet_length).decode('utf-8')
		return packet


	def send_packet(self, content, header_length, in_chunks=False):
		packet_header = f"{len(content):<{header_length}}".encode('utf-8')
		if in_chunks:
			self.__client_socket.send(packet_header)
			start, end = 0, 0
			while start < int(packet_header.strip()):
				end += 4096
				self.__client_socket.send(content[start:end])
				start = end

			print("packet sending complete")
			self.__client_socket.send("end".encode('utf-8'))

		else:
			self.__client_socket.send(packet_header + content.encode('utf-8'))

	# lambda functions
	close_client_connection = lambda self : self.__client_socket.close()
	close_server = lambda self : self.__server_socket.close()


#Driver code

server_hub = ServerHub(
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM),
	host = HOST_IP,
	port = PORT
)


# ==========> To fetch folder and files from a given drive

Tk().withdraw()

# drive file system tree
# TODO: optimize the tree creation architecture
ref_root = file_system_tree_creation(askdirectory())
serialized_tree_object = pickle.dumps(ref_root)
print("Initialized....")

# ==========> End of fetching from drive



while True:
	server_hub.accept_connection()

	server_hub.send_packet("You have now connected to the net drive server", HEADER_LENGTH)

	client_ack_message = server_hub.receive_packet(HEADER_LENGTH)
	print(client_ack_message)

	server_hub.send_packet(serialized_tree_object, HEADER_LENGTH, in_chunks = True)

	selected_file_path = server_hub.receive_packet(HEADER_LENGTH)
	print(selected_file_path)


	#data streaming part
	file_object = open(selected_file_path, "rb")
	file_content = file_object.read()
	file_object.close()

	server_hub.send_packet(file_content, HEADER_LENGTH, in_chunks = True)

	server_hub.close_client_connection()
	break

server_hub.close_server()

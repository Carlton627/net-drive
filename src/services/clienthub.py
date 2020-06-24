import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

import socket
import pickle
from ui import userinterface

from tkinter import Tk
from tkinter.filedialog import askdirectory 

HEADER_LENGTH = 20
PORT = 3030
HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)


class ClientHub:
	def __init__(self, client_socket, host, port):
		self.__client_socket = client_socket
		try:
			self.__client_socket.connect((host, port))
		except Exception as e:
			print(e)


	def receive_packet(self, header_length, in_chunks=False):
		packet_header = self.__client_socket.recv(header_length)
		packet_length = int(packet_header.decode('utf-8').strip())
		if in_chunks:
			packet = b''
			length_of_segments = 0
			while length_of_segments <= packet_length:
				segment = self.__client_socket.recv(4096)
				try:
					if segment.decode('utf-8')[-3:] == "end":
						break
				except UnicodeDecodeError:
					pass
				finally:
					length_of_segments += len(segment)
					packet += segment

		else:
			packet = self.__client_socket.recv(packet_length).decode('utf-8')
			
		return packet


	def send_packet(self, content, header_length):
		packet_header = f"{len(content):<{header_length}}".encode('utf-8')
		self.__client_socket.send(packet_header + content.encode('utf-8'))


# Driver code 

client_hub = ClientHub(
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM),
	host = HOST_IP,
	port = PORT 
)

welcome_message = client_hub.receive_packet(HEADER_LENGTH) 
print(welcome_message)

ack_message = "Thank you for accepting the connection"
client_hub.send_packet(ack_message, HEADER_LENGTH)


file_system_tree = client_hub.receive_packet(HEADER_LENGTH, in_chunks = True)
file_system_tree = pickle.loads(file_system_tree)

selected_file_path = userinterface.create_CLI(file_system_tree)
client_hub.send_packet(selected_file_path, HEADER_LENGTH)

file_content = client_hub.receive_packet(HEADER_LENGTH, in_chunks = True)

Tk().withdraw()
save_location = askdirectory()

if save_location:
	write_to_file = save_location + "/" + selected_file_path.split("/")[-1] #filename only
	file_object = open(write_to_file, "wb")
	file_object.write(file_content[:-3])
	file_object.close()


# TODO: Handle for client exiting application

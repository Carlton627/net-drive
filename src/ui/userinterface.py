
'''
getter methods from FetchingFiles.FileSystemDirectoriesTree class
- get_next() - class.FileSystemDirectoriesTree
- get_path() - string

getter methods from FetchingFiles.FileSystemFiles class
- get_path() - string
'''

class NetDriveUI:
	def __init__(self, file_system_tree):
		self.__file_system_tree = file_system_tree


	def get_file_system_tree(self):
		return self.__file_system_tree


	def expand_dir(self, directory):
		return [x for x in directory.get_next()]


# TODO: return file path to calling program

def create_CLI(file_system_tree):
	ui = NetDriveUI(file_system_tree)
	root = ui.get_file_system_tree()
	while True:
		try:
			content_list = ui.expand_dir(root)
		except AttributeError:
			print(f"getting file {root.get_path()} from server")
			return root.get_path()

		for i in range(len(content_list)):
			print(i, content_list[i].get_path())
		print("Type (exit) to quit application")
		choice = input("Choose a folder: ")
		if choice.lower() == "exit": break

		choice = int(choice)
		if choice == 99:
			root = content_list[-1].get_prev()
		else:
			root = content_list[choice]

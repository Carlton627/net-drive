
# file manipulation and extraction imports
from pathlib import Path as file_path
import os.path as path
import sys


class FileSystemDirectoriesTree:
	"""
		Class for creating objects of type FileSystemDirectoriesTree
		Each directory fetched from FetchingFiles.get_directories_and_files() will be a object of this class
		
		Instance Variables:

			1. self.__path holds the absolute path name of the directory object present in the selected drive

			2. self.__next is a list that holds all the sub directories and files of the given directory object

		Member Functions:

			1. get_path(self) returns the absolute path of the given directory object

			2. set_next(self, next) populates the list with sub directories and files present in a given directory object

			3. get_next(self) returns the list containing sub directories of the given directory object 

	"""

	def __init__(self, path):
		self.__path = path
		self.__next = []


	def get_path(self):
		return self.__path


	def set_next(self, next):
		self.__next.append(next)


	def get_next(self):
		return self.__next



class FileSystemFiles:
	"""
		Class for creating objects of type FileSystemFiles
		Each file fetched from FetchingFiles.get_directories_and_files() will be a object of this class

		Instance Variable(s):

		1. self.__path holds absolute path of the file object in the selected drive

		Member Function(s):

		1. get_path(self) returns the absolute path of the given file object

	"""

	def __init__(self, path):
		self.__path = path


	def get_path(self):
		return self.__path



class PreviousDirectoryPointer:
	"""
		Class for creating objects of type PreviousDirectoryPointer
		This object will link back to the parent directory of the directory that its present in

		Instance Variables:

			1. self.__name is just a name given to the object that helps it to be identifies in the GUI and CLI programming

			2. self.__prev is the pointer that points back to the parent directory object
		
		Member Functions:

			1. get_path(self) returns the name of the object
			2. get_prev(self) return the parent directory object it points to

	"""

	def __init__(self, prev):
		self.__name = "go back"
		self.__prev = prev


	def get_path(self):
		return self.__name


	def get_prev(self):
		return self.__prev



class FetchingFiles:
	"""
		Class for fetching files and directories in a given drive path set by the server
		Object of this class is created in file_system_tree_creation(drive_root) function to fetch directories and files

		Instance Variable:

			1. self.drive_path holds the root name of the hard drive or pen drive from where directories and files have to be fetched

		Member Function:

			1. get_directories_and_files(self, drive_path) fetches directories and files from the given drive_path, the drive_path should be valid and present on the server system.

			The os.path library under the alias path is used to check if the given path is valid by using the exists(path) method which return true if the path is valid and is present.

			The pathlib library under the alias file_path this library is used to fetch all directories and files from a given root directory. The as_posix() method returns the absolute path of the fetched directories and files.

	"""
	def __init__(self):
		self.drive_path = None


	def get_directories_and_files(self, drive_path):
		self.drive_path = drive_path
		if path.exists(self.drive_path):
			drive_directory = file_path(self.drive_path)
			files = [x.as_posix() for x in drive_directory.iterdir() if x.is_file()]
			directories = [x.as_posix() for x in drive_directory.iterdir() if x.is_dir()]
			return files, directories
		else:
			return None



def file_system_tree_creation(drive_root):
	"""
		This function creates a file system tree using all the above objects created
		This is the function that is invoked by the ServerSocker.py file which sends the drive_root as a parameter

	"""
	ref_drive_root = FileSystemDirectoriesTree(drive_root)
	f = FetchingFiles()
	path_object_list = []
	path_object_list.append(ref_drive_root)

# -------- Setting forward pointer (next) of the tree

	while path_object_list:
		temp_ref = path_object_list.pop()
		try:
			files, directories = f.get_directories_and_files(temp_ref.get_path())
		except PermissionError:
			continue
		except TypeError: # TODO: Handle error in the UI properly
			print("Drive not selected")
			sys.exit(0)

		for directory in directories:
			temp_ref.set_next(FileSystemDirectoriesTree(directory))

		for file in files:
			temp_ref.set_next(FileSystemFiles(file))

		for paths in temp_ref.get_next():
			if type(paths) is FileSystemDirectoriesTree:
				path_object_list.append(paths)

# -------- End of next pointer setting

# -------- Setting backward pointer (prev) of the tree

	path_object_list.append(ref_drive_root)

	while path_object_list:
		temp_ref = path_object_list.pop(0)
		for folder in temp_ref.get_next():
			if type(folder) is FileSystemDirectoriesTree:
				path_object_list.append(folder)
				folder.set_next(PreviousDirectoryPointer(temp_ref))

# -------- End of prev pointer setting

	return ref_drive_root

# __main__.FileSystemDirectoriesTree
# __main__.FileSystemFiles

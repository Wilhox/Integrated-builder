"""
Integrated-builder v.2.0

- Builder for Sublime Text 3
- Compiles and runs c, pyw, py and m-files
- Files with charters ä and ö will be compiled correctly.
- Smarter error handling
- Automatisize your work easily


This is free software; you can redistribute it and/or modify
it. This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY;

(C) 2019 Ville Lauronen <ville.lauronen(at)gmail.com>

"""


INSTALLATION_INSTRUCTIONS = """

-------REQUIREMENTS--------

1. Windows OS
2. Python 3.x: https://www.python.org/downloads/
3. Sublime Text 3.x: https://www.sublimetext.com/3
4. Optional: Matlab R2015 or newer requiret for running m-files

----MANUAL INSTALLATION----

1. Start Sublime Text 3
2. Create new build system: Tools > Build System > New Build System
3. Copy and paste code below:

{
	"cmd" : "python Integrated-builder.pyc \"${file_name}\" \"$file_path\" \"$file_base_name\",
	"working_dir" : "<File_Paht>",
	"selector" : "source.c",
	"shell": true
}


4. Save as: File > save As...
5. Save as "Integrated-Builder" and copy a file path of the save location
6. Replace  section <File_Paht> in code above by path you just copied
7. Replace "\\" by "\\\\" on path copied.
   Example path: "C:\\\\Users\\\\user_name\\\\AppData\\\\Roaming\\\\Sublime Text 3\\\\Packages\\\\User"

8. Save: File > save
9. Copy files named Integrated-builder.pyc and MatlabShell.pyc to same location
10. Activate Integrated-builder from tools > build system
"""


INSTRUCTIONS = """

INSTRUCTIONS

1. Start a program named Sublime Text 3
2. Activate Integrated-builder from tools > build system
3. Use Sublime Text 3 to open your m, c, pyw- and py-files
4. Compile and run your files by using a key binding Ctrl + B

"""


def PackageInstall(error):
	"""
	- Finds out which package is missing
	- Downloads it automatically after five seconds.
	- Restarts script
	- Example:
		try:
			import numpy as np
			import matplotlib.pyplot as plot

		except ImportError as error:
			PackageInstall(error)
	"""
	import time, subprocess, os, sys
	module = str(error)[15:].replace('\'', '')
	print(__doc__)
	print('>>>',str(error))
	print('>>> Downloading missing modules, please wait...')
	print('>>> The scirpt may restart multiple times')
	if 'win32com'in module or 'win32api' in module: #win32com and win32api must be installed as pywin32
		module = 'pypiwin32'
	if subprocess.call("pip install " + module):
		input('Press any key to continue')
	time.sleep(1)
	os.startfile(__file__)
	sys.exit()


try:
	import os, logging, io, subprocess, sys, ctypes, py_compile, time
except ImportError as e:
	PackageInstall(e)
except:
	import logging
	logging.exception('')

class build():
	"""
	Main class

	- Process code
	- Run code
	"""

	def __init__(self, file, path, base):
		print_s('Integrated-builder v.2.0 [py, pyw, c, m]')
		self.own_path = os.getcwd()
		self.name = file
		os.chdir(path) #toimitaan kohteen sijainnissa
		self.path = path + '\\' + file
		self.base = base

		if self.name.endswith('.py'):
			self.build_python('.py')
		elif self.name.endswith('.pyw'):
			self.build_python('.pyw')

		elif self.name.endswith('.m'):
			self.runMatlab(file, path, base)

		elif self.name.endswith('.c'):
			self.cbuild = self.path.replace('.c', '.cbuild')
			self.removeHiding(self.cbuild)
			self.process()
			self.hideFile(self.cbuild)

		else:
			print_s('FILE NOT SUPPORTED')
			print_s('Only c-, m-, py- and pyw-files are supported')
			print_s('Please use other builder:')
			print_s('	1. Choose "Tools" from the top')
			print_s('	2. Click "Build System"')
			print_s('	3. Choose which one you want to use')


	def runMatlab(self, file, path, base):
		'''Run m-files'''
		try:
			try:
				#matlab.engine is running as subprocess under sublime text
				import matlab.engine
				if not base in matlab.engine.find_matlab():
					print_s('>>> Creating Matlab session named "' + base + '"...')
					engine = matlab.engine.start_matlab()
					getattr(engine, 'matlab.engine.shareEngine')(base, nargout=0)
					engine.cd(path)

			except ImportError:
				pass #Matlabshell will handle that

			process = subprocess.Popen([sys.executable,
					self.own_path + '\\MatlabShell.pyc',
					base,
					path],
				creationflags = subprocess.CREATE_NEW_CONSOLE)
		except:
			logging.exception('Internal Error')

	def build_python(self, file_type):
		'''Compile, get errors and run'''
		try:
			self.pybuild = self.path.replace(file_type, '.pyc')
			print_s('Compiling...')
			py_compile.compile(self.path, self.pybuild, doraise = True)
			print_s('Starting...')
			os.startfile('\"' + str(self.pybuild) + '\"')

		except py_compile.PyCompileError as error:
			error = str(error).replace('  File "' + self.path + '", ', '')
			print('There is a bug on ', str(error))

	def hideFile(self, file):
		'''Hide a file by using windows file attributes'''
		try:
			ctypes.windll.kernel32.SetFileAttributesW(file, 0x02)
		except:
			pass

	def removeHiding(self, file):
		'''Make a file visible by using windows file attributes'''
		try:
			ctypes.windll.kernel32.SetFileAttributesW(file, 0x00)
		except:
			pass

	def replaceLetters(self):
		'''
		- Remove incompatible letters
		- Returns:
			return 1: File must be compiled
			return 0: Compilation not needed
		'''
		table = {'ä': '\\x84 \b', 'Ä' : '\\x8E \b', 'ö': '\\x94 \b', 'Ö' : '\\x99 \b'}
		#Table at: https://en.wikipedia.org/wiki/Code_page_850
		
		#Open and processing
		file = io.open(self.path, mode ="r", encoding="utf-8")
		lines = file.readlines()
		file.close()

		if str(lines) == str([]):
			print('The file ' + self.name + ' is empty')
		else:
			lines_2 = []
			for line in lines:
				for letter in table:
					if letter in line:
						line = line.replace(letter, table[letter])
				lines_2.append(line)

			#Trying to open cbuild already exits
			try:
				file = io.open(self.cbuild, mode ="r", encoding="utf-8")
				lines = file.readlines()
				file.close()
			except FileNotFoundError:
				lines = [] #tiedostoa ei ole


			#Writing cbuild only if changes are made
			if lines != lines_2:
				file = io.open(self.cbuild, mode="w", encoding = "utf-8")
				for line in lines_2:
					file.write(line)
				file.close()
				return 1 #changes are made

		return 0 #changes are not made


	def process(self):
		'''
		- Process incompatible letters, compile and run
		- No args, no return.
		'''

		ok = True
		if self.replaceLetters():
			print_s('Compiling...')
			command = 'gcc  -std=c99  -x c  -Wall  -lm  -o ' + '\"' + str(self.path).replace('.c', '') + '\"' + " " + '\"' + str(self.path).replace('.c', '.cbuild') + '\"'
			feedback = subprocess.getoutput(command) #k\x84 \x84 nnet\x84 \x84 n ja pyydet\x84 \x84 n feedback

			#Processing feedback
			feedback = feedback.replace(self.path, '')
			for line in feedback.split('\n'):
				if 'collect2.exe: error: ld returned 1 exit status' in line:
					ok = False
					self.clear()
					print_s('\n\nPERMISSION DENIED')
					print_s('The most common reasons why you see that:')
					print_s('	1. The scrip is already running.')
					print_s('	2. The scrip is opened in other application.')
					print_s('	3. The script is buggy.')
					print_s('	4. Unknown issue, just try again!\n')

				else:
					if line.startswith('build:'):
						try:
							if 'In function' not in line:
								line = 'Line ' + line.split(' ')[0].split(':')[1] + ': ' + ' '.join(line.split()[1:])
							else:
								line = ' '.join(line.split()[1:])
						except:
							pass

						if 'error' in line and ok:
							self.clear()
							ok = False

					if line != '':
						print(line)

		else:
			print_s('The file is already compiled')

		try:
			if ok:
				print_s('Starting...')
				#run
				comm = '\"' + str(self.path).replace('.c', '.exe') + '\"'
				os.startfile(comm)
		except:
			print_s('Sorry, the file can not be executed')
			self.clear()

	def clear(self):
		"""
		- Clear a file
		- No args, no return.
		"""
		file = io.open(self.cbuild, mode ="w", encoding="utf-8")
		file.close()

def print_s(text):
	sys.stdout.write(text + '\n')
	sys.stdout.flush()

def autoSetup():
	"""
	Automated installation
	- Find Sublime Text 3
	- Make a config file
	- Copy this script to right place
	- Returns:
		return 1 if succesfull
		return 0 if failed
	""" 

	print('>>> Running autosetup...')
	try:
		import shutil, json
	except ImportError as e:
		PackageInstall(e)

	#where is Sublime text?
	path = os.environ['APPDATA']
	for folder in os.listdir(path):
		if str(folder) == 'Sublime Text 3':
			path += '\\Sublime Text 3\\Packages\\User'
			#Config data
			data = {
				"cmd" : "python Integrated-builder.pyc \"${file_name}\" \"$file_path\" \"$file_base_name\"",
				"working_dir" : path,
				"selector" : "source.python",
				"shell" : True,
				#"target" : "Integrated-builder"
				}

			filePath = path + '\\Integrated-builder.sublime-build'
			file = io.open(filePath, 'w')
			file.write(json.dumps(data, indent = True))
			file.close()
			print('>>> '+filePath+' created')

			#copy files
			for file in [__file__, 'MatlabShell.py']:
				if file.endswith('.pyc'):
					shutil.copy(file, path)
					print('>>> '+file+' copied to '+path)
				else:
					py_compile.compile(file, file.replace('.py', '.pyc'), doraise = True)
					shutil.copy(file.replace('.py', '.pyc'), path)
					print('>>> '+file+' compiled and copied to '+path)

			return 1

	print('>>> Sublime Text 3 not found from ' + path)
	print('>>> AutoSetup Failed')
	return 0

		
if __name__ == "__main__":
	if len(sys.argv) < 3: #The script is started without arguments -> Install
		try:
			print('Integrated-builder v.2.0\n')
			if os.name != 'nt':
				print('>>> UNSUPPORTED OPERATING SYSTEM')
			elif autoSetup():
				print(INSTRUCTIONS)
			else:
				print(INSTALLATION_INSTRUCTIONS)
		except SystemExit:
			sys.exit()
		except:
			#Unknown issue, lest print more information
			logging.exception('ERROR')
			print(INSTALLATION_INSTRUCTIONS)
		
		input()

	else: #The script is started with argumets, like Sublime text does
		try:
			builder = build(sys.argv[1], sys.argv[2], sys.argv[3])
		except PermissionError:
			print('PERMISSION DENIED (PermissionError)')
			print('The most common reasons why you see that:')
			print('	1. The scrip is already running.')
			print('	2. The scrip is opened in other application.')
		except OSError as e:
			if 'WinError 123' in str(e):
				print('FILE NOT FOUND (WinError 123)')
				print('The most common reasons why you see that:')
				print('	1. The scrip is not saved')
				print('		>>> Press Ctrl + s')
			else:
				raise OSError
		except SystemExit:
			sys.exit()
		except:
			#Unknown issue
			logging.exception('Oh my god, what the hell happened?')
			input()

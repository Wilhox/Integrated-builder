"""
Integrated-builder v.2.0

- Builder for Sublime Text 3
- Compiles and runs c, pyw- and py-files
- m-files will be automatically opened at matlab.
- The file won´t be compiled, if there is no changes made after last run.
- Files with charters ä and ö will be compiled correctly.
- Smarter error handling
- Automatisize your work easily
- Made for Windows operating system


This is free software; you can redistribute it and/or modify
it. This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY;

Copyright (C) 2019 Ville Lauronen <ville.lauronen(at)gmail.com>
============================================================================
"""

INSTRUCTIONS = """
INSTRUCTIONS
1. Start a program named Sublime Text 3
2. Activate Integrated-builder from tools > build system
3. Use Sublime Text 3 to open your m, c, pyw- and py-files
4. Compile and run your files by using a key binding Ctrl + B
"""


INSTALLATION_INSTRUCTIONS = """
----MANUAL INSTALLATION----

1. Do you have those programs intalled?

   Python 3.x: https://www.python.org/downloads/
   Sublime Text 3.x: https://www.sublimetext.com/3

   >>If not, install them and run this scipt again.
   		>>>The script will be installed automatically

   >>Else, Automatic installation is failed. Continue reading.



3. Start Sublime Text 3
4. Create new build system: Tools > Build System > New Build System
5. Copy a code below and paste it for file opened:

{
	"cmd" : "python Integrated-builder.pyc \"${file_name}\" \"$file_path\"",
	"working_dir" : "<File_Paht>",
	"selector" : "source.c",
	"shell": true
}


6. Save as: File > save As...
7. Save as "Integrated-Builder" and copy a file path of the save location
8. Replace  section <File_Paht> in code above by path you just copied
9. Replace "\\" by "\\\\" on path copied.
   Example path: "C:\\\\Users\\\\user_name\\\\AppData\\\\Roaming\\\\Sublime Text 3\\\\Packages\\\\User"

10. Save: File > save
11. Move this file in same location
12. Activate Integrated-builder from tools > build system
13. Now you can use a key binding Ctrl + B to compile and run your files directly from Sublime Text 3
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
	print(__doc__)
	print('>>>',str(error))

	print('>>> Download will start after five seconds')
	time.sleep(5)
	subprocess.call("pip install " + str(error)[15:].replace('\'', ''))

	print('>>> Restarting')
	os.startfile(__file__)
	sys.exit()


try:
	import os, logging, io, subprocess, sys, ctypes, py_compile
except ImportError as e:
	PackageInstall(e)


class build():
	"""
	Main class

	- Process code
	- Run code
	"""

	def __init__(self, file, path):
		print('Integrated-builder v.2.0 [py, pyw, c, m]')
		self.name = file
		os.chdir(path) #toimitaan kohteen sijainnissa
		self.path = path + '\\' + file

		if self.name.endswith('.py') or self.name.endswith('.pyw'):
			self.pybuild = self.path.replace('.py', '.pyc')
			try:
				py_compile.compile(self.path, self.pybuild, doraise = True)

				try:
					os.startfile('\"' + str(self.pybuild) + '\"')
				except:
					print('Sorry, file can not be executed.')

			except py_compile.PyCompileError as error:
				error = str(error).replace('  File "' + self.path + '", ', '')
				print('There is a bug on ', str(error))

		elif self.name.endswith('.m'):
			#matlab.exe -r \"cd c:\outdir; try, run ('c:\outdir\my.m'); end; quit\"
			command = ''
			os.startfile('\"' + str(self.path) + '\"', command)
			#command = 'matlab.exe -r \"cd ' + path + '\; run (\'' + self.path + '\'); end; quit;\"'
			#command = 'matlab.exe -r run (\'' + self.path + '\'); end; quit;\"'
			#print(command)
			#feedback = subprocess.getoutput(command) #käännetään ja pyydetään feedback
			#print(feedback)

		elif self.name.endswith('.c'):
			self.cbuild = self.path.replace('.c', '.cbuild')
			self.removeHiding(self.cbuild)
			self.process() #prosessoidaan file
			self.hideFile(self.cbuild)

		else:
			print('FILE NOT SUPPORTED')
			print('Only c-, m-, py- and pyw-files are supported')
			print('Please use other builder:')
			print('		1. Choose "Tools" from the top')
			print('		2. Click "Build System"')
			print('		3. Choose which one you want to use')

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
		Letters = {'ä': '\\x84 \b', 'Ä' : '\\x8E \b', 'ö': '\\x94 \b', 'Ö' : '\\x99 \b', '°' : '\\xF8 \b', '€':'e'}
		#Taulukko löytyy täältä: https://en.wikipedia.org/wiki/Code_page_850
		
		#avataan lähdefile
		file = io.open(self.path, mode ="r", encoding="utf-8")
		linet = file.readlines()
		file.close()

		if str(linet) == str([]):
			print('file ' + self.name + ' on tyhjä!')
		else:
			#Outojen merkkien käsittely
			linet_2 = []
			for line in linet:
				for merkki in Letters:
					if merkki in line:
						line = line.replace(merkki, Letters[merkki])
				linet_2.append(line)

			#Etsitään ja avataan jo mahdollisesti olemassa oleva ja prosessoitu lähdefile
			try:
				file = io.open(self.cbuild, mode ="r", encoding="utf-8")
				linet = file.readlines()
				file.close()
			except FileNotFoundError:
				linet = [] #filea ei ole


			#kirjoitus vain, jos lähdefileen on on tehty muutoksia
			if linet != linet_2:
				file = io.open(self.cbuild, mode="w", encoding = "utf-8")

				for line in linet_2:
					file.write(line)
				file.close()
				return 1
			else:
				return 0


	def process(self):
		'''
		- Process incompatible letters, compile and run
		- No args, no return.
		'''

		ok = True
		if self.replaceLetters():
			command = 'gcc  -std=c99  -x c  -Wall  -lm  -o ' + '\"' + str(self.path).replace('.c', '') + '\"' + " " + '\"' + str(self.path).replace('.c', '.cbuild') + '\"'
			feedback = subprocess.getoutput(command) #käännetään ja pyydetään feedback

			#Käsitellään ja esitetään feedback:
			feedback = feedback.replace(self.path, '')
			for line in feedback.split('\n'):
				if 'collect2.exe: error: ld returned 1 exit status' in line:
					ok = False
					self.clear()
					print('\n\nPERMISSION DENIED')
					print('The most common reasons why you see that:')
					print('		1. The scrip is already running.')
					print('		2. The scrip is opened in other application.')
					print('		3. The script is buggy.')
					print('		4. Unknown issue, just try again!\n')

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
			print('The file is already compiled.')

		try:
			if ok:
				#Ajetaan ohjelma omassa ikkunassa:
				comm = '\"' + str(self.path).replace('.c', '.exe') + '\"'
				os.startfile(comm)
		except:
			print('The file can not be executed')

	def clear(self):
		"""
		- Clear a file
		- No args, no return.
		"""
		file = io.open(self.cbuild, mode ="w", encoding="utf-8")
		file.close()


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

	try:
		import shutil
	except ImportError as e:
		PackageInstall(e)

	#where is Sublime text?
	path = os.environ['APPDATA']
	for folder in os.listdir(path):
		if str(folder) == 'Sublime Text 3':
			path += '\\Sublime Text 3\\Packages\\User'

			#Config data
			data = ['{\n',
			'\n"cmd" : "python Integrated-builder.pyc \\"${file_name}\\" \\"$file_path\\"",',
			'\n"working_dir" : "'+ path.replace('\\', '\\\\') +'",',
			'\n"selector" : "source.c",',
			'\n"shell" : true',
			'\n}']

			filePath = path + '\\Integrated-builder.sublime-build'
			file = io.open(filePath, 'w')
			for line in data:
				file.write(line)
			file.close()
			print('>>> Config file updated \n>>> ' + filePath)

			#copy
			if __file__.endswith('.pyc'):
				shutil.copy(__file__, path) #kopiodaan tämä file oikeaan pathiinsa
			else:
				py_compile.compile(__file__, __file__.replace('.py', '.pyc'), doraise = True)
				shutil.copy(__file__.replace('.py', '.pyc'), path) #kopiodaan tämä file oikeaan pathiinsa
			
			print('>>> AutoSetup Completed \n>>> ' + path)	
			return 1

	print('>>> Sublime Text 3 not found from ' + path)
	print('>>> AutoSetup Failed')
	return 0

		
if __name__ == "__main__":
	try:
		#When this script is called by sublimetext using arguments
		builder = build(sys.argv[1], sys.argv[2])

	except IndexError:
		print(__doc__)
		try:
			if autoSetup():
				print(INSTRUCTIONS)
			else:
				print(INSTALLATION_INSTRUCTIONS)
		except:
			#Unknown issue, lest print more information
			logging.exception('>>> AutoSetup Failed')
			print(INSTALLATION_INSTRUCTIONS)
		
		input()

	except PermissionError:
		print('PERMISSION DENIED')
		print('The most common reasons why you see that:')
		print('		1. The scrip is already running.')
		print('		2. The scrip is opened in other application.')

	except OSError as e:
		if 'WinError 123' in str(e):
			print('FILE NOT FOUND')
			print('The most common reasons why you see that:')
			print('		1. The scrip is not saved')
			print('			>>> Press Ctrl + s')
		else:
			raise OSError
	except:
		#Unknown issue
		logging.exception('Oh my god, what the hell happened?')
		input()
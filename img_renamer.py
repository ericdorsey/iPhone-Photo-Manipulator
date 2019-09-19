#!/usr/local/bin/python3

import glob
import os
import random
import sys
import string
import shutil
import datetime
import argparse
#from PIL import Image 
from exif import Image

# Initialize the parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", help="rename all files in supplied directory")
parser.add_argument("-r", "--removeaae", action="store_true", help="delete the .aae files; for use with --directory argument")
parser.add_argument("-f", "--file", help="rename only supplied file")
parser.add_argument("-w", "--whatif", action="store_true", help="what if; dry run")
args = parser.parse_args()
print(args)

# Ensure we don't have bad argument/flag combinations
if args.dir and args.file:
	print(f"-d and -f are mutually exclusive; choose either a directory or a file, not both")
if args.file and args.removeaae:
	print(f"-f and -r are incompatible; -r can only be used with -d")
if not args.file and not args.dir:
	print(f"-f or -d are required; you must supply a file or directory")
#sys.exit()

# dry run? 
dryrun = False
if args.whatif:
	#print("whatif flag detected")
	dryrun = True

# Get a date object
date_now = datetime.datetime.now()

# Get an epoch date from it (time in seconds)
epoch_date_now = date_now.strftime("%s")
epoch_date_now = int(epoch_date_now)

#print(epoch_date_now)
#print(type(epoch_date_now))
#sys.exit(0)
#epoch_date_now = int(epoch_date_now)

# Change to dir 
if args.dir:
	try:
		os.chdir(args.dir)
	except FileNotFoundError as err:
		print("Caught error!:")
		print(err)
		print(f"{args.dir} is not a valid directory? Quitting.")
		sys.exit()
	print(f"Current directory: {os.getcwd()}")
	#sys.exit()

def rand_num_and_letter(length):
	"""
	Function to create a series of random letters and numbers
	param length: how long the combination of random letters and numbers should be
	"""
	rand_num_and_letter_string = ""
	for i in range(length):
		char_or_num = random.randint(0, 1)
		if char_or_num == 0:
			my_rand_number = random.randint(0, 9)
			rand_num_and_letter_string += str(my_rand_number)
		if char_or_num == 1:	
			my_rand_letter = random.choice(string.ascii_lowercase)
			rand_num_and_letter_string += my_rand_letter
	if rand_num_and_letter_string[-1] == "0":	
		#print("oops, last char is 0")
		rand_num_and_letter_string = rand_num_and_letter_string[:-1]
		rand_num_and_letter_string += str(random.randint(1, 9))
	return rand_num_and_letter_string

def remove_aae_files(dryrun):
	#print(f"Removing aae_files")
	aae_files = glob.glob("*.AAE")
	for i in aae_files:
		if dryrun == False:
			print(f"Removing {i}")
			os.remove(i)
		elif dryrun == True:
			print(f"DRYRUN: would remove {i}")

def rename_file(myfile, rand_fname, dryrun, counter, append_padding, directory_root=None):
	if not myfile.lower().endswith(".jpg") is True:
		print(f"{myfile} is not a .jpg! Exiting!")
		sys.exit()
	#print(f"rename_file() called against {myfile}")
	#print(f"rand_fname: {rand_fname}, dryrun: {dryrun}, counter: {counter}, append_padding: {append_padding}")
	new_filename = rand_fname
	padding_addon = str(counter).zfill(append_padding)
	new_filename += padding_addon
	new_filename += ".jpg"
	new_filename = f"IMG_RENAME_{new_filename}"
	# we're modifying an individual file
	if directory_root is not None:
		my_file = f"{directory_root}/{myfile}"
		new_filename = f"{directory_root}/{new_filename}"
	if dryrun == False:
		print(f"{myfile} is being renamed {new_filename}")
		#sys.exit()
		#shutil.copy(new_filename, new_filename)
		shutil.move(myfile, new_filename)
		# Get stat info
		stinfo = os.stat(new_filename)
		#print(dir(stinfo))
		#sys.exit(0)
		# Make the file accessed time now
		#print(f"Modified time before: {stinfo.st_mtime}")
		#print(datetime.datetime.fromtimestamp(stinfo.st_mtime).strftime('%Y-%m-%d-%H:%M'))
		print("Printing at_time, mtime, ctime")
		for i in [stinfo.st_atime, stinfo.st_mtime, stinfo.st_ctime]:
			print(datetime.datetime.fromtimestamp(i).strftime('%Y-%m-%d-%H:%M'))
		os.utime(new_filename, (stinfo.st_atime, epoch_date_now)) 
		# Make the file modified time now
		os.utime(new_filename, (stinfo.st_mtime, epoch_date_now)) 
		# Make the ctime modified time now
		os.utime(new_filename, (stinfo.st_ctime, epoch_date_now)) 

		# Get the stat info again
		stinfo = os.stat(new_filename)
		# Print modified time after
		#print(f"Modified time after: {stinfo.st_mtime}")
		print("Printing at_time, mtime, ctime")
		for i in [stinfo.st_atime, stinfo.st_mtime, stinfo.st_ctime]:
			print(datetime.datetime.fromtimestamp(i).strftime('%Y-%m-%d-%H:%M'))
		#print(datetime.datetime.fromtimestamp(stinfo.st_mtime).strftime('%Y-%m-%d-%H:%M'))
		# Strip the exif info with PIL
		#my_image = Image.open(new_filename)
		#my_image.save(new_filename, "JPEG", subsampling=0, quality=100)
		print("EXIF")
		# Strip off the date of the image with exif
		with open(new_filename, "rb") as image_file:
			my_image = Image(image_file)
			print(my_image.datetime)
			print(my_image.datetime_original)
			print(my_image.datetime_digitized)
			print(my_image.gps_datestamp)
			my_image.datetime = f"{date_now.year}:{date_now.month}:{date_now.day} {date_now.hour}:{date_now.minute}:{date_now.second}"
			my_image.datetime_original = f"{date_now.year}:{date_now.month}:{date_now.day} {date_now.hour}:{date_now.minute}:{date_now.second}"
			my_image.datetime_digitized = f"{date_now.year}:{date_now.month}:{date_now.day} {date_now.hour}:{date_now.minute}:{date_now.second}"
			my_image.gps_datestamp = f"{date_now.year}:{date_now.month}:{date_now.day}"
			#my_image.datetime = (date_now.year, date_now.month, date_now.day)
			#del my_image.datetime
			#del my_image.datetime_original
			#del my_image.gps_datestamp
			print("AFTER")
			print(my_image.datetime)
			print(my_image.datetime_original)
			print(my_image.datetime_digitized)
			print(my_image.gps_datestamp)
			#my_image.write(new_filename)
		with open(new_filename, "wb") as new_image_file:
			new_image_file.write(my_image.get_file())
		#sys.exit()
	elif dryrun == True:
		print(f"DRYRUN: {myfile} would have been renamed {new_filename}")

# Create a random filename
rand_fname = rand_num_and_letter(8)	
#print(f"rand_fname is {rand_fname}")
#sys.exit()

# append padding holders; ie 4 means append 4 0's to the filename: example gdf67dgf0000
append_padding = 5

if args.file:
	counter = 1
	directory_root = os.path.dirname(args.file)
	print(directory_root)	
	#sys.exit()
	rename_file(args.file, rand_fname, dryrun, counter, append_padding, directory_root)	
if args.dir:
	# get the number of files in the directory
	num_files = len(os.listdir())
	# counter; increment the append padding by one each iteration
	counter = 0
	# create a list to hold all the file names
	files_in_dir = []
	for i in os.listdir():
		# grab all the .jpg files
		if i.lower().endswith("jpg"):
			files_in_dir.append(i)
	for i in files_in_dir:
		rename_file(i, rand_fname, dryrun, counter, append_padding)
		counter += 1
	if args.removeaae:
		remove_aae_files(dryrun)
	
#	if args[0] == "all":
#		for i in os.listdir():
#			my_rand_starting_number += 1
#			if i.lower().endswith("jpg"):
#				common_rename_actions(my_rand_starting_number, my_letters)
#	elif args[0] == "space_twos":
#		funky_files = glob.glob("* 2.JPG")
#		for i in funky_files:
#			my_rand_starting_number += 1
#			common_rename_actions(my_rand_starting_number, my_letters)

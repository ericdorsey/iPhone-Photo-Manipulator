#!/usr/local/bin/python3

import os
import random
import sys
import string
import shutil
import datetime
import argparse
import collections
import logging
import re
from tqdm import tqdm
from exif import Image

# Initialize the parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", required=True, help="run this script against files in supplied directory")
parser.add_argument("-r", "--removeaae", action="store_true", help="delete the .aae files; for use with --directory argument")
parser.add_argument("-w", "--whatif", action="store_true", help="what if; dry run")
parser.add_argument("-c", "--changenames", action="store_true", help="change filename(s), rename (all) file(s)")
parser.add_argument("-s", "--stripexifdates", action="store_true", help="strip exif dates from file(s)")
parser.add_argument("-n", "--numberspaced", type=str, help="integer; for `XXXX 1.JPG` filename renames. For use with -c")
args = parser.parse_args()

# Get a date object
date_now = datetime.datetime.now()

# Get the directory where the script is running
current_dir = os.path.dirname(os.path.abspath(__file__))

# Name of Logs Dir
logs_dir = "logs"

# Logs full path directory 
logs_dir_fullpath = f"{current_dir}/{logs_dir}"  

# Create logs dir if it doesn't exist
os.chdir(current_dir)
if not os.path.exists(logs_dir_fullpath):
	#logger.debug(f"creating logs dir at {logs_dir_fullpath}")
	os.makedirs(logs_dir_fullpath)

# Logging Config
logging_filename = f"{logs_dir_fullpath}/{date_now.year}-{date_now.month}-{date_now.day}_{date_now.hour}-{date_now.minute}-{date_now.second}.log"

# Create a custom logger
logger = logging.getLogger(__name__)

# Create logger handler(s)
logfile_handler = logging.FileHandler(logging_filename)

# Set the handler logging level
logfile_handler.setLevel(logging.DEBUG)

# Create logger formatter
logfile_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#stream_handler = logging.StreamHandler(stream=None)

# Add formatters to handlers
logfile_handler.setFormatter(logfile_format)

# Add handlers to logger
logger.addHandler(logfile_handler)

# Set the logging level
logger.setLevel(logging.DEBUG)


# Ensure we don't have bad argument/flag combinations
#if args.dir and args.file:
#	print(f"-d and -f are mutually exclusive; choose either a directory or a file, not both")
#if args.file and args.removeaae:
#	print(f"-f and -r are incompatible; -r can only be used with -d")
#if not args.file and not args.dir:
#	print(f"-f or -d are required; you must supply a file or directory")
#sys.exit()

# Is this a dry run? Default to False
dryrun = False
if args.whatif:
	dryrun = True

# Log some information around this run
#logger.debug(f"args were {args}")
for i in vars(args).items():
	logger.debug(i)
logger.debug(f"current_dir is {current_dir}")
#logger.debug("date_now is {date_now_strf}".format(date_now_strf=date_now.strftime("%s"))
logger.debug(f"date_now is {date_now.strftime('%Y-%m-%d %H:%M:%S')}") 
logger.debug(f"logging_filename is {logging_filename}")

# Get an epoch date from it (time in seconds)
#epoch_date_now = date_now.strftime("%s")
#epoch_date_now = int(epoch_date_now)

# Append padding var; if set to 4 means append 4 0's to the filename: example gdf67dgf0000
# Only used if args.changenames flag is true
append_padding = 5

# Function Definitions 

def rand_num_and_letter(length):
	"""
	Function to create a series of random letters and numbers

	length (int): How long the combination of random letters and numbers should be

	Returns:
	str: Newly created str of letters and numbers
	
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

	# oops, last char is 0 .. maybe this doesn't matter now?
	if rand_num_and_letter_string[-1] == "0":	
		rand_num_and_letter_string = rand_num_and_letter_string[:-1]
		rand_num_and_letter_string += str(random.randint(1, 9))
	return rand_num_and_letter_string

def remove_aae_files(directory, dryrun):
	"""Remove all files with .AEE extension in given directory"""
	logger.debug(f"Removing all .AAE files in {directory}")
	regex = re.compile(f".+.AAE", re.IGNORECASE)
	for i in os.listdir():
		if re.match(regex, i):
			if dryrun == False:
				print(f"Deleting {i}")
				logger.debug(f"Deleting {i}")
				os.remove(i)
			elif dryrun == True:
				print(f"DRYRUN: would have deleted {i}")

def rename_file(myfile, rand_fname, counter, append_padding, dryrun):
		"""Rename a file"""
		#logger.debug(f"rename_file() called against {myfile}")
		if not myfile.lower().endswith(".jpg") is True:
			print(f"{myfile} is not a .JPG! No action taken.")
			logger.debug(f"{myfile} is not a .jpg! No action taken.")
			return
		if dryrun == False:
			# Create a random filename
			#rand_fname = rand_num_and_letter(4)	
			rand_fname = rand_fname.upper()
			new_filename = rand_fname
			padding_addon = str(counter).zfill(append_padding)
			new_filename += padding_addon
			new_filename += ".JPG"
			new_filename = f"IMG_RENAME_{new_filename}"
			logger.debug(f"{myfile} is being renamed {new_filename}")
			shutil.move(myfile, new_filename)
		elif dryrun == True:
			print(f"DRYRUN: {myfile} would have been renamed {new_filename}")
		return

def strip_exifdates(myfile, date_now, dryrun):
	"""Function to remove known EXIF date data that affects sorting"""
	if dryrun == False:
		local_exceptions = {}
		with open(myfile, "rb") as image_file:
			try:
				my_image = Image(image_file)
			except AssertionError as err:
				exc_type, value, traceback = sys.exc_info()
				local_exceptions[myfile] = exc_type
				logger.exception(f"exif library exception caught with {myfile}", exc_info=True)
				return	
			try:
				logger.debug(f"Attempting to modify EXIF datetime for {myfile}")
				logger.debug(f"Before my_image.datetime: {my_image.datetime}")
				my_image.datetime = f"{date_now.year}:{date_now.month}:{date_now.day} {date_now.hour}:{date_now.minute}:{date_now.second}"
				logger.debug(f"After my_image.datetime: {my_image.datetime}")
			except (AttributeError, KeyError) as err:
				exc_type, value, traceback = sys.exc_info()
				local_exceptions[myfile] = exc_type
				logger.exception(f"Exception caught modifying datetime with {myfile}", exc_info=True)
				pass
			try:
				logger.debug(f"Attempting to modify EXIF datetime_original for {myfile}")
				logger.debug(f"Before my_image.datetime_original: {my_image.datetime_original}")
				my_image.datetime_original = f"{date_now.year}:{date_now.month}:{date_now.day} {date_now.hour}:{date_now.minute}:{date_now.second}"
				logger.debug(f"After my_image.datetime_original: {my_image.datetime_original}")
			except (AttributeError, KeyError) as err:
				exc_type, value, traceback = sys.exc_info()
				local_exceptions[myfile] = exc_type
				logger.exception(f"Exception caught modifying datetime_original with {myfile}", exc_info=True)
				pass
			try:
				logger.debug(f"Attempting to modify EXIF datetime_digitized for {myfile}")
				logger.debug(f"Before my_image.datetime_digitized: {my_image.datetime_digitized}")
				my_image.datetime_digitized = f"{date_now.year}:{date_now.month}:{date_now.day} {date_now.hour}:{date_now.minute}:{date_now.second}"
				logger.debug(f"After my_image.datetime_digitized: {my_image.datetime_digitized}")
			except (AttributeError, KeyError) as err:
				exc_type, value, traceback = sys.exc_info()
				local_exceptions[myfile] = exc_type
				logger.exception(f"Exception caught modifying datetime_digitized with {myfile}", exc_info=True)
				pass
			try:
				logger.debug(f"Attempting to modify EXIF gps_datestamp for {myfile}")
				logger.debug(f"Before my_image.gps_datestamp: {my_image.gps_datestamp}")
				my_image.gps_datestamp = f"{date_now.year}:{date_now.month}:{date_now.day}"
				logger.debug(f"After my_image.gps_datestamp: {my_image.gps_datestamp}")
			except (AttributeError, KeyError) as err:
				exc_type, value, traceback = sys.exc_info()
				local_exceptions[myfile] = exc_type
				logger.exception(f"Exception caught modifying gps_datestamp with {myfile}", exc_info=True)
				pass
			with open(myfile, "wb") as new_image_file:
				new_image_file.write(my_image.get_file())
	if dryrun == True:
		print(f"DRYRUN: Would have removed EXIF date data on {myfile}")
	logger.debug(f"Iteration exceptions: {local_exceptions}")
	return local_exceptions

#def rename_file(myfile, rand_fname, dryrun, counter, append_padding, directory_root=None):
#	if not myfile.lower().endswith(".jpg") is True:
#		print(f"{myfile} is not a .jpg! Exiting!")
#		sys.exit()
#	exceptions = {}
#	#print(f"rename_file() called against {myfile}")
#	#print(f"rand_fname: {rand_fname}, dryrun: {dryrun}, counter: {counter}, append_padding: {append_padding}")
#	if args.changenames:
#		new_filename = rand_fname
#		padding_addon = str(counter).zfill(append_padding)
#		new_filename += padding_addon
#		new_filename += ".jpg"
#		new_filename = f"IMG_RENAME_{new_filename}"
#	#print(f"-----> {new_filename}")
#	#sys.exit()

#	if directory_root is not None:
#		# we're modifying an individual file
#		if args.changenames:
#			#my_file = f"{directory_root}/{myfile}"
#			new_filename = f"{directory_root}/{new_filename}"
#		else:
#			#my_file = f"{directory_root}/{myfile}"
#			new_filename = f"{directory_root}/{myfile}"

#	if dryrun == False:
#		#sys.exit()
#		#shutil.copy(new_filename, new_filename)
#		if args.changenames:
#			logger.debug(f"{myfile} is being renamed {new_filename}")
#			shutil.move(myfile, new_filename)
#		else:
#			new_filename = f"{myfile}"
#			logger.debug(f"{new_filename} is current file")

#		logger.debug("EXIF")
#		if args.stripexifdates:
#			# Strip off the date of the image with exif
		
#	if dryrun == True and not args.changenames:
#		new_filename = f"{directory_root}/{myfile}"
#		print(f"DRYRUN: {myfile} would have had EXIF date data modified")
#	elif dryrun == True and args.changenames:
#		print(f"DRYRUN: {myfile} would have been renamed {new_filename}")

# Create a random filename
rand_fname = rand_num_and_letter(8)	
#print(f"rand_fname is {rand_fname}")
#sys.exit()

# Main 
if args.dir:
	try:
		os.chdir(args.dir)
		logger.debug(f"Changed dir to {os.getcwd()}")
	except FileNotFoundError as err:
		print(err)
		print(f"{args.dir} is not a valid directory? Quitting.")
		#logger.debug(f"{args.dir} is not a valid directory? Quitting.")
		logger.exception(f"Exception caught with {myfile}", exc_info=True)
		sys.exit()

	# Dict to collect the exceptions as we iterate
	exceptions = {}

	# Counter; increment the append padding by one each iteration
	counter = 0

	# Remove the .AAE files first
	if args.removeaae:
		remove_aae_files(args.dir, dryrun)

	# Create a list to hold all the file names
	files_in_dir = []

	# Modify only the files named `XXXX {args.numberspaced}.JPG` 
	if args.numberspaced:
		regex = re.compile(f".+ {args.numberspaced}.JPG", re.IGNORECASE)
		for i in os.listdir():
			if re.match(regex, i):
				files_in_dir.append(i)

	# Modify all the .JPG files 
	if not args.numberspaced:	
		for i in os.listdir():
			# grab all the .jpg files
			if i.lower().endswith("jpg"):
				files_in_dir.append(i)

	# Maintain the order of files based on their names
	files_in_dir.sort()
	
	if args.changenames:
		rand_fname = rand_num_and_letter(4)	

	# Take appropriate actions against every file in files_in_dir list
	for i in tqdm(files_in_dir):
		if args.stripexifdates:
			# Perhpas this iteration exceptions should just be logged to a different logger
			iteration_exceptions = strip_exifdates(i, date_now, dryrun)
			if iteration_exceptions != None:
				# Append this iterations exceptions to the outer exception tracking dict
				exceptions.update(iteration_exceptions)
		if args.changenames:
			rename_file(i, rand_fname, counter, append_padding, dryrun)
#		else:
#			new_filename = f"{myfile}"
#			logger.debug(f"{new_filename} is current file")
		counter += 1

	#print(f"Log file:\n{logging_filename}")
	print(f"{logging_filename}")
	if not (len(exceptions) == 0):
		print("Exceptions collected:")
		for i in exceptions.items():
			print(i)
	#print(exceptions)
	exceptcounts = collections.Counter(exceptions.values())
	#print(type(exceptcounts))
	if not (len(exceptcounts) == 0):
		print(exceptcounts)

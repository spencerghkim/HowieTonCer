from os import listdir
from os.path import isfile, join

mypath = "."
# retrieve names of files in directory
files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

seqno = 0

for f in files:
	# split filename by _ delimiting character
	prefix = f.split('_')[0]
	picid = f.split('.')[0]
	ext = f.split('.')[1]
	if ext != 'jpg':
		continue
	date = "2001-02-02"
	print '''INSERT INTO photo VALUES ("''' + picid  + '''", "/pictures/''' + f + '''", "''' + ext + '''", "''' + date + '''");'''
	albumnum = 0
	if prefix == "football":
		albumnum = 2
	elif prefix == "sports":
		albumnum = 1
	elif prefix == "world":
		albumnum = 3
	elif prefix == "space":
		albumnum = 4
	print '''INSERT INTO contain VALUES (''' + str(albumnum) + ''', "''' + picid + '''", "''' + picid + '''", ''' + str(seqno) + ''');'''
	seqno += 1


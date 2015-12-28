################################################################################ IMPORTS ##############

import mechanize
from bs4 import BeautifulSoup
from CaptchaParser import CaptchaParser
from PIL import Image
import sqlite3
from login import login

################################################################################ Code ##############

#add your username and password
br = login("14BCE0104","canttrustanyone")

print br.geturl()
if br.geturl()==("https://academics.vit.ac.in/student/home.asp"):
	print "SUCCESS"

	
	br.open("https://academics.vit.ac.in/student/getfacdet.asp?fac= ")
	response = br.open("https://academics.vit.ac.in/student/getfacdet.asp?fac= ")

	#selecting the form

	soup = BeautifulSoup(response.get_data())
		
	#extracting status of password changing procedure

	tables = soup.findAll("table")
	myTable = tables[0]
	rows = myTable.findChildren(['th','tr'])
	rows = rows[1:]

	#initialising some required variables
	links = []

	#extracting data
	for row in rows:

		rowdata =  []
		cells = row.findChildren('td')
		cells = cells[0:4]
		
		links.append("https://academics.vit.ac.in/student/"+cells[3].find('a')['href'])

	#print len(links)

	#connecting to the database
	db = sqlite3.connect("faculty.sqlite")
	cur = db.cursor()

	#setting up the database
	cur.execute('''DROP TABLE IF EXISTS Faculty''')
	cur.execute('''DROP TABLE IF EXISTS open_hr''')
	cur.execute('''DROP TABLE IF EXISTS open_hr1''')
	cur.execute('''DROP TABLE IF EXISTS open_hr2''')
	cur.execute('''DROP TABLE IF EXISTS open_hr3''')

	cur.execute('''CREATE TABLE open_hr1 (fac_id INTEGER, week TEXT, frm TEXT, too TEXT)''')
	cur.execute('''CREATE TABLE open_hr2 (fac_id INTEGER, week TEXT, frm TEXT, too TEXT)''')
	cur.execute('''CREATE TABLE open_hr3 (fac_id INTEGER, week TEXT, frm TEXT, too TEXT)''')
	cur.execute('''CREATE TABLE open_hr (fac_id INTEGER, open_hr1_id INTEGER, open_hr2_id INTEGER, open_hr3_id INTEGER)''')
	cur.execute('''CREATE TABLE Faculty (name TEXT, school TEXT, designation TEXT, venue TEXT, intercom INTEGER, email TEXT, division TEXT, additionalRole TEXT, img BLOB, open_hr_id INTEGER)''')

	#extracting the data
	for l in links:

		br.open(l)
		response = br.open(l)
		print links.index(l)

		emp_id = int(l[67:])

		soup = BeautifulSoup(response.get_data())

		img = soup.findAll('img')

		br.retrieve("https://academics.vit.ac.in/student/"+img[0]['src'], "fac_img.png")
		pic = "fac_img.png"

		with open(pic, 'rb') as input_file:
			ablob = input_file.read()

		tables = soup.findAll('table')
		myTable = tables[1]
		rows = myTable.findChildren(['th','tr'])
		rows = rows[1:10]
		data = []

		for row in rows:

			cells = row.findChildren('td')
			cells = cells[1]
			value = cells.string
			data.append(value)

		cur.execute('''INSERT INTO Faculty (name, school, designation, venue, intercom, email, division, additionalRole, img, open_hr_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], sqlite3.Binary(ablob), emp_id))

		try:
			myTable = tables[2]

		except IndexError:
			cur.execute('''INSERT INTO open_hr (fac_id, open_hr1_id, open_hr2_id, open_hr3_id) VALUES (?,?,?,?)''',(emp_id, emp_id, emp_id, emp_id))
			cur.execute('''INSERT INTO open_hr1 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, None, None, None))
			cur.execute('''INSERT INTO open_hr2 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, None, None, None))
			cur.execute('''INSERT INTO open_hr3 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, None, None, None))

		else:
			rows = myTable.findChildren(['th','tr'])
			rows = rows[1:4]
			data = []

			for row in rows:

				rowdata = []
				cells = row.findChildren('td')
				
				for cell in cells:
					value = cell.string
					rowdata.append(value)

				data.append(rowdata)

			cur.execute('''INSERT INTO open_hr (fac_id, open_hr1_id, open_hr2_id, open_hr3_id) VALUES (?,?,?,?)''',(emp_id, emp_id, emp_id, emp_id))
			cur.execute('''INSERT INTO open_hr1 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, data[0][0], data[0][1], data[0][2]))
			try:
				cur.execute('''INSERT INTO open_hr2 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, data[1][0], data[1][1], data[1][2]))
			except IndexError:
				cur.execute('''INSERT INTO open_hr2 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, None, None, None))
			try:
				cur.execute('''INSERT INTO open_hr3 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, data[2][0], data[2][1], data[2][2]))
			except IndexError:
				cur.execute('''INSERT INTO open_hr3 (fac_id, week, frm, too) VALUES (?,?,?,?)''',(emp_id, None, None, None))

		db.commit()
import mysql.connector
import pandas as pd 
from sqlalchemy import create_engine
import csv

# Initialize mysql connection
host = "localhost"
user = "root"
passwd = "Nakuru9665*"
database = "ClinicalTrials"

db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  passwd = "Nakuru9665*",
  database = "ClinicalTrials"
)
print(db)

# Create cursor
mycursor = db.cursor()

# Create our database
# mycursor.execute("CREATE DATABASE ClinicalTrials") 

# create_engine
engine = create_engine('mysql+pymysql://{user}:{passwd}@{host}/{database}'.format(host=host, database=database, user=user, passwd=passwd))

# Show tables in database
mycursor.execute("Show tables;")
myresult = mycursor.fetchall()
for x in myresult:
  print(x)

# Check first 20 items in table
mycursor.execute("SELECT * from GeneticDisorders LIMIT 20")
for i in mycursor:
  print(i)

# Delete table
# mycursor.execute("DROP TABLE GeneticDisorders")

# Get number of columns in our table
mycursor.execute('SELECT COUNT(*) AS NUMBEROFCOLUMNS FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name="GeneticDisorders"') 
for i in mycursor:
  print(i)

# Check number of rows in table
mycursor.execute('SELECT COUNT(*) FROM GeneticDisorders')
for i in mycursor:
  print(i)

# View first 10 table items in order by name
mycursor.execute('SELECT * FROM ClinicalTrials ORDER BY Names LIMIT 10')
for i in mycursor:
  print(i)

# Remove duplicates from table
# First create table like first one
mycursor.execute('CREATE TABLE temp_table LIKE GeneticDisorders')
for i in mycursor:
  print(i)

# Insert distinct values from first table to the temp_table and check if that worked
mycursor.execute('INSERT INTO temp_table SELECT DISTINCT * FROM GeneticDisorders')
mycursor.execute('SELECT COUNT(*) FROM temp_table')
for i in mycursor:
  print(i)

# Rename both tables
mycursor.execute('RENAME TABLE GeneticDisorders  TO Old_GeneticDisorders, temp_table TO ClinicalTrials')

mycursor.execute('RENAME TABLE ClinicalTrials TO GeneticDisorders')

# Delete original table
mycursor.execute("DROP TABLE Old_GeneticDisorders")

# Get some details for optimized search
mycursor.execute("DESCRIBE GeneticDisorders")
for i in mycursor:
  print(i)

# Rename Study Title because we anticipate problems
mycursor.execute('ALTER TABLE GeneticDisorders RENAME COLUMN `Study Title` TO Title')


# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:39:35 2015

@author: smichel
"""

''' TESTING FILES '''
full_path = "../datafiles/USC/"
full_path2 = "../datafiles/CFR/"
# Create a database. After "import" use "pgDatabase" for postgres or "mongoDatabase" for mongo
from docDatabase import pgDatabase
from docDatabase import mongoDatabase

#assign the class to a variable, but don't chain functions here. We want to pass the class object to other functions later for various write-outs. 
#db = pgDatabase('host', 'desired_database_name', 'user', 'password', 'initial_database_name')
db = pgDatabase('localhost', 'rulesets8', 'postgres', 'aasda', 'postgres')
#db = mongoDatabase('host', 'desired_db_name', 'user', 'password' )

# Use "autocreate()" to create the database and its tables
#db.autocreate()
#db.autocreate(createDB=False, tables=["edges"])

# Create the parser object. This handles all parsing functions. 
from docParser import parser 
# Create a parser object for each filepath to be parsed. The filepath should contain the file(s) to be parsed, and also pass the database object created above
usc = parser(fp=full_path, db=db)
cfr = parser(fp=full_path2, db=db)

# Tell the parser to identify and store section numbers in the database
#usc.extractSections()
#cfr.extractSections()


# We'll record the time needed to parse each corpus
import time
t_start = time.time()
#usc.extractReferences(capture=["cfr", "usc"], body=True, citations=False, notes=False)

t_2 = time.time()
cfr.extractReferences(capture=["cfr", "usc"], body=True, citations=False)

print("UPDATING nodelist to include nodes identified from edgelist")
db.updateNodes()

#print("Calculating Network Metrics")
#usc.extractMetrics(db=db)


print("\nUSC Elapsed time was {} minutes".format((t_2 - t_start)/60))
print("\nCFR Elapsed time was {} minutes".format((time.time() - t_2)/60))
print("\nTotal Elapsed time was {} minutes".format((time.time() - t_start)/60))
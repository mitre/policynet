# -*- coding: utf-8 -*-

import sys
import shutil
sys.path.insert(0, './parser/')
from docDatabase import pgDatabase
from docParser import parser

full_path_usc = "/tmp/usc.zip_unzipped/"
full_path_cfr = "/tmp/cfr.zip_unzipped/"

username = sys.argv[1];
password = sys.argv[2];
database = sys.argv[3];
db = pgDatabase('localhost', database, username, password, 'postgres')
db.autocreate(createDB=False)


usc = parser(fp=full_path_usc, db=db)
cfr = parser(fp=full_path_cfr, db=db)


if sys.getdefaultencoding() == 'ascii':
	reload(sys)
	sys.setdefaultencoding('utf8')

usc.extractSections()
cfr.extractSections()

usc.extractReferences(capture=["cfr", "usc"], body=True, citations=False, notes=False)
cfr.extractReferences(capture=["cfr", "usc"], body=True, citations=False)

db.updateNodes()
shutil.rmtree(full_path_usc)
shutil.rmtree(full_path_cfr)

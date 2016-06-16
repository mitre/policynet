# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 15:00:35 2015

@author: Shaun Michel on behalf of MITRE

This script runs through approx. 6 steps for each of the files, with obvious overlaps:

1) Strip text content and place section texts into manageable directories. 
2) Strip XML and put data into manageable .csv files. 
3) Re-open each file from Step 2 and place contents into a single "master nodelist" file (.tsv)
4) Re-open the "master nodelist" tsv from Step 3 and remove duplicates. 
5) Write the unique node data to a new file
6) With each write-out from Step 5, check for and add section texts when possible. 

The purpose of using .csv/.tsv output format is to maximize universality for further use. 
I selected .tsv for final output because it has fewer known complications with in-text commas, 
particularly where double- and single-quotes are used frequently and unpredictably. 

"""

from bs4 import BeautifulSoup as Soup
import os
import csv

# Maximize csv.field_size_limit according to Windows standards. Adjust for other platforms. 
# This seems a necessary adjustment to handle large amounts of text. 
# The only known alternative (attempted) drastically reduced processing speed. 
#csv.field_size_limit(2147483647)
csv.field_size_limit(2147483647)

def uniq(output):
    last = object()
    for item in output:
        if item[0] == last:
            continue
        yield item
        last = item[0]

def fix_masternode():
    print("\n   -(CLEAN) master list of node data... [Step 4/6]")
    from operator import itemgetter

    for file in os.listdir("tmp/final/"):
        if file.endswith("-nodelist.csv"):

            with open("tmp/final/{}".format(file), "r", encoding="UTF-8") as f:
                reader = csv.reader(f, delimiter=",")
                next(f)
                all_nodes = sorted(reader, key = itemgetter(0, 1))
                print("   --Removing duplicate nodes")
                l = uniq(all_nodes)
        
            with open("tmp/final/{}-final.csv".format(file.split(".")[0]), "a", encoding="UTF-8") as f:
                node_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_ALL, lineterminator="\n")
                node_writer.writerow(["Node", "Heading", "url", "Doctype", "Text", "L1", "L2", "L3", "L4"])
                print("\n   --(WRITE) new master node list [Step 5/6] ")
                print("\n   --(ADD) extracted texts to node data... [Step 6/6]")
                for line in l:
                    if line[0] != "Source" and line[0] != "Target":
                        node = line[0]
                        heading = line[1]
                        url = line[2]
                        doctype = line[3].lower()
                        text_loc = "null"
                        level_list = []
                        
                        try:
                            form = node.split(" ")
                            if doctype == "usc":
                                text_loc = open("texts/{}/{}/sections/{}.txt".format(doctype.lower(), form[0], form[2]), "r", encoding="utf-8").read()                
                            elif doctype == "cfr":
                                text_loc = open("texts/{}/2014/{}/sections/{}.txt".format(doctype.lower(), form[0], form[2]), "r", encoding="utf-8").read()
                                print("texts/{}/2014/{}/sections/{}.txt".format(doctype, form[0].zfill(2), form[2].zfill(2)))
                            elif doctype == "hr":
                                text_loc = open("texts/{}/{}/sections/{}.txt".format(doctype.lower(), form[0], form[2]), "r", encoding="utf-8").read()
                                print("texts/{}/2014/{}/sections/{}.txt".format(doctype, form[0].zfill(2), form[2].zfill(2)))
                                
                        except: pass
            
            
                        '''Let's make "null" values a little more informative.'''
                        if text_loc == "null":
                            text_loc = "Text unavailable (either repealed or not yet added)."
                        
                        if heading == "null":
                            heading = node
            
                                    
                        level_list = [url.split("/")[i] for i in range(2, len(url.split("/")))]
                        while len(level_list) < 4:
                            level_list.append("null")
                        output = [node, heading, url, doctype, text_loc]
                        for i in range(0, len(level_list)):
                            output.append(level_list[i])
                        node_writer.writerow(output)    

def create_masternode():
    print("\n   -(CREATE) master list of node data... [Step 3/6]")
    #nodelist_outpath = "tmp/final/master-nodelist-USC.tsv"
 
    for folder in os.listdir("tmp/netdata/"):
        if folder == "HR" and not folder.endswith(".bak"):
            nodelist_outpath = "tmp/final/{}-nodelist.csv".format(folder)
            for file in os.listdir("tmp/netdata/{}".format(folder)):
                if file.endswith("-edgelist.csv"):
                    print("   --Adding {} to master list".format(file))
            
                    with open("tmp/netdata/{}/{}".format(folder, file), "r", encoding="UTF-8") as f:
                        reader = csv.DictReader(f)
                        for line in reader:
                            src = line["Source"]
                            src_head = line["Source_Heading"].strip().strip("\"")
                            tgt = line["Target"]
                            src_url = line["Source_url"]
                            tgt_url = line["Target_url"]
                            tgt_url_broad = line["Target_url_broad"]
                            #edgetype = line["EdgeType"]
                            #note = line["Note"]
                            #context = line["Context"]
                            src_doctype = line["Source_Doctype"].lower()
                            tgt_doctype = line["Target_Doctype"].lower()
                            src_outpath = "tmp/final/{}-nodelist.csv".format(src_doctype)
                            tgt_outpath = "tmp/final/{}-nodelist.csv".format(tgt_doctype)
                            src_writer = csv.writer(open(src_outpath, "a", encoding="UTF-8"), delimiter=",", quoting=csv.QUOTE_ALL, lineterminator="\n")
                            tgt_writer = csv.writer(open(tgt_outpath, "a", encoding="UTF-8"), delimiter=",", quoting=csv.QUOTE_ALL, lineterminator="\n")
                            if not os.path.exists(src_outpath):
                                os.makedirs(nodelist_outpath)
                                src.writerow(["Node", "Heading", "url", "Doctype", "Text", "L1", "L2", "L3", "L4"])

                            if not os.path.exists(src_outpath):
                                os.makedirs(nodelist_outpath)
                                tgt.writerow(["Node", "Heading", "url", "Doctype", "Text", "L1", "L2", "L3", "L4"])
                                
                            src_writer.writerow([src, src_head, src_url, src_doctype, "null", "null", "null", "null", "null"])
                            tgt_writer.writerow([tgt, "null", tgt_url_broad, tgt_doctype, "null", "null", "null", "null", "null"])
                            
    for folder in os.listdir("texts"):
        os.walk(folder)            

def parse_doc(file, doctype, extract_texts = True, parse_texts = False):
    if doctype == "USC":
        import USC_parser3 as parser

    elif doctype == "CFR":
        import CFR_parser3 as parser
    
    elif doctype == "HR":
        import HR_parser2 as parser
    
    elif doctype == "Strategy":
        import stratdoc_parser3 as parser

    elif doctype == "CFR-C":
        import CFR_Cornell_parser3 as parser

    if extract_texts == True:
        print("\n   -(STRIP) section texts... [Step 1/6]")
        print("    --Adding txts directory and relevant texts to this script's folder...")
        parser.sections_to_txt(file)

    if parse_texts == True:
        print("\n   -(PARSE) XML... [Step 2/6]")
        parser.xml_parse(file)


def detect_doctype(path):
    
    doctype = ""

    with open(path, "rb") as f:
        soup = Soup(f) 
        if soup.find("uscdoc"):
            doctype = "USC"
            print("\nFile {} appears to be a US Code document.".format(path))
        elif soup.find("cfrdoc"):
            doctype = "CFR"
            print("\nFile {} appears to be a Code of Federal Regulations document.".format(path))
        elif soup.find("legis-num") and "H. R. " in soup.find("legis-num").text:
            doctype = "HR"
            print("\nFile {} appears to be a House of Representatives document.".format(path))
        elif soup.find("lii_cfr_xml"):
            doctype = "CFR-C"
            print("\nFile {} appears to be a CFR document tagged by Cornell.".format(path))
        else:
            doctype = "Strategy"
            print("\nFile {} does not match a known document classification. Attempting miscellany parse as \"Strategy\" document.".format(path))
    if doctype != "":
        parse_doc(path, doctype)
    else: 
        print("Cannot continue with file: {}".format(path))
 
def init(path, directory=bool):
    ''' Accepts  '''    
    
    import os
    print(directory)
    if os.path.isdir(path) or directory == True:
        print("Input appears to be a directory. Scanning for XML files...")
        if not path.endswith("/"):
            path = "{}/".format(path)
        for file in os.listdir(path):
            if (file.endswith(".xml") or file.endswith(".html")) and not file.lower().split(".")[0].endswith("a"):
                detect_doctype(path + file)    
        #for i in os.walk(path):
        #    directory = i[0]
        #    for file in i[2]:
        #        detect_doctype(directory + "/" + file)
                #print(i[0].split("\\")[-1], i[2])

    elif os.path.isfile(path) or directory == False:
        if path.endswith(".xml") or path.endswith(".html"):
            detect_doctype(path)
    #create_masternode()
    #fix_masternode()

def move_files_CFR():
    import shutil
    import os
    main_folder = "tmp/datafiles/CFR"
    for folder in os.listdir(main_folder):
        for file in os.listdir("{}/{}".format(main_folder, folder)):
            filesplit = file.split("-")
            newfile = "{}-{}{}-{}".format(filesplit[1], filesplit[0].lower(), filesplit[2].replace("title", ""), filesplit[3].replace("vol", ""))
            shutil.copy2("{}/{}/{}".format(main_folder,folder,file), "{}/{}".format(main_folder, newfile))

def output_log_CFR():
    with open("CFR_regex_log.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        confirmed = []
        for line in reader:
            if line not in confirmed:
                confirmed.append(line)
    print(confirmed)

#move_files_CFR()
'''
for dirpath, dirnames, filenames in os.walk("texts/"):
    dir_split = dirpath.replace("\\", "/").split("/")
    for f in filenames:
        section = dir_split[2]
        doctype = dir_split[1]
        if section.startswith("0"):
            section = section[1:]
        f = f[:-4]
        if f.startswith("0"):
            f = f[1:]
            if f == "0":
                f = ""
        node_label = "{} {} {}".format(section, dir_split[1], f).strip()
        print(node_label)
'''
#init("tmp/datafiles/strategy_docs/DODGIG20ImplementationGuidanceDoD20110818FOUOs.html")
#init("tmp/datafiles/CFR-Cornell/")
#init("tmp/datafiles/USC/")
#init("tmp/datafiles/HR/BILLS-114hr6rfs.xml")
#init("tmp/datafiles/HR/hr3590.xml")
#init("tmp/datafiles/CFR/title-5/CFR-2014-title5-vol3.xml")
#init("tmp/datafiles/USC/usc48.xml")
#init("tmp/datafiles/CFR/title-29/CFR-2014-title29-vol7.xml")
create_masternode()
fix_masternode()
#output_log_CFR()
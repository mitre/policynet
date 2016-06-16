# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 12:37:44 2015

@author: SMICHEL
"""

import csv
from bs4 import BeautifulSoup as Soup
import os
import calendar

src_doctype = "cfr-c" #use lower case: act, cfr, pl, stat, usc

def standardize_act_target(tgt_url): 
    ''' Produce label for identified Act target based on URL. This is cleaner 
    than pulling the text and accounting for typos and inconsistencies.'''

    surl = tgt_url.split("/")    
    
    date = surl[3].split("-")
    date = "{} {}, {}".format(calendar.month_name[int(date[1])], date[2], date[0])
    try:
        tgt_title = "Act of {}, ch. {} {}".format(date, surl[4].strip("ch"), surl[5].strip("s"))
    except:
        try:
            if "ch" in surl[4]:
                tgt_title = "Act of {}, ch. {}".format(date, surl[4].strip("ch"))
            elif "s" in surl[4]:
                tgt_title = "Act of {}, {}".format(date, surl[4].strip("s"))
        except: 
            tgt_title = "Act of {}".format(date)
            
    try:    surl[4] = surl[4].lstrip("ch")
    except: pass
    try:    surl[5] = surl[5].lstrip("s")
    except: pass

    tgt_url = "/".join(x for x in surl)

    try: 
        tgt_url_broad = "/".join(tgt_url.split("/")[0:6]) 
    except: 
        tgt_url_broad = "/".join(tgt_url.split("/")[0:5]) 

        
    return tgt_title, tgt_url, tgt_url_broad    
    
def standardize_cfr_target(tgt_url):
    ''' Produce label for identified Code of Federal Regulations target based 
    on URL. This is cleaner than pulling the text and accounting for typos and 
    inconsistencies.'''
    
    surl = tgt_url.split("/")    

    try:
        if "s" in surl[4] or surl[4][0].isdigit():
            tgt_title = "{} CFR {}".format(surl[3].replace("t", ""), surl[4].replace("s", ""))
        else:
            tgt_title = "{} CFR".format(surl[3].replace("t", ""))
    except: 
        pass
    try:    surl[3] = surl[3].lstrip("t")
    except: pass
    try:    surl[4] = surl[4].lstrip("s")
    except: pass

    tgt_url = "/".join(x for x in surl)
    
    try: # use this code block if you want to shorten CFR urls to the section number only
        tgt_url_broad = "/".join(tgt_url.split("/")[0:5]) #this works if there's a section number
    except: 
        tgt_url_broad = "/".join(tgt_url.split("/")[0:4]) #if the above fails, just pull the top-level name (there are no sections)

    return tgt_title, tgt_url, tgt_url_broad
    
def standardize_pl_target(tgt_url): 
    ''' Produce label for identified Public Law target based on URL. This is 
    cleaner than pulling the text and accounting for typos and inconsistencies.'''
    
    surl = tgt_url.split("/")    
    try:    surl[5] = surl[5].lstrip("s")
    except: pass
    tgt_url = "/".join(x for x in surl)


    try: # use this code block if you want to shorten Pub. L. urls to the section number only
        tgt_url_broad = "/".join(tgt_url.split("/")[0:6]) #this works if there's a section number
    except: 
        tgt_url_broad = "/".join(tgt_url.split("/")[0:5]) #if the above fails, just pull the top-level name (there are no sections)

    surl = tgt_url_broad.split("/")
    try:
        tgt_title = "Pub. L. {}-{} {}".format(surl[3], surl[4], surl[5].replace("s", ""))
    except:
        tgt_title = "Pub. L. {}-{}".format(surl[3], surl[4])
    
    return tgt_title, tgt_url, tgt_url_broad

def standardize_stat_target(tgt_url): 
    ''' Produce label for identified Statute target based on URL. This is 
    cleaner than pulling the text and accounting for typos and inconsistencies.'''
    surl = tgt_url.split("/")    

    try: 
        tgt_title = "{} Stat. {}".format(surl[3].replace("t", ""), surl[4].replace("s", ""))
    except: 
        tgt_title = "{} Stat.".format(surl[3].replace("t", ""))

    try:    surl[3] = surl[3].lstrip("t")
    except: pass
    try:    surl[4] = surl[4].lstrip("s")
    except: pass

    tgt_url = "/".join(x for x in surl)

    try:
        tgt_url_broad = "/".join(tgt_url.split("/")[0:5])
    except:
        tgt_url_broad = "/".join(tgt_url.split("/")[0:4])

    return tgt_title, tgt_url, tgt_url_broad

def standardize_usc_target(tgt_url):    
    ''' Produce label for identified USC target based on URL. This is cleaner 
    than pulling the text and accounting for typos and inconsistencies.'''
    
    surl = tgt_url.split("/")    
    print(surl)
    tgt_title = str
    try:
        if surl[4]:
            tgt_title = "{} USC {}".format(surl[3].replace("t", ""), surl[4].replace("s", ""))
        else:
            tgt_title = "{} USC".format(surl[3].replace("t", ""))
            tgt_url_broad = "/".join(tgt_url.split("/")[0:4])
    except: 
        pass
    
    surl[3] = surl[3].lstrip("t")
    surl[4] = surl[4].lstrip("s")

    tgt_url = "/".join(x for x in surl)

    try:
        tgt_url_broad = "/".join(tgt_url.split("/")[0:5])
    except:
        tgt_url_broad = "/".join(tgt_url.split("/")[0:4])

    return tgt_title, tgt_url, tgt_url_broad

def standardize_special_characters(title):
    ''' Excel is particularly bad at handling special characters. The following 
    lists of recurring special characters will be replaced and can be extended 
    to include any number of known special characters.'''
    
    special_spaces_list = [b"\xe2\x80\x81"]
    special_single_quotes_list = [b"\xc3\xa2\xc2\xac\xc3\x9c",
                                  b"\xc3\xa2\xc2\xac",
                                  b"\xe2\x80\x98",
                                  b"\xe2\x80\x99"]
    special_section_list = [b"\xc2\xa7"]    
    special_empty_list = [b"\xe2\x80\xaf"]
    special_hyphens_list = [b"\xe2\x80\x93", 
                            b"\xe2\x80\x94", 
                            b"\xc3\xa2\xc2\xac"]
    special_double_quotes_list = [b"\xe2\x80\x9c",
                                  b"\xe2\x80\x9d"]
    
    for x in special_spaces_list:
        try:
            title = bytes.decode(title.encode("utf-8").replace(x, b" "))
        except: pass

    for x in special_single_quotes_list:
        try:
            title = bytes.decode(title.encode("utf-8").replace(x, b"\'"))
        except: pass

    for x in special_section_list:
        try:
            title = bytes.decode(title.encode("utf-8").replace(x, b"Sec. "))
        except: pass

    for x in special_empty_list:
        try:
            title = bytes.decode(title.encode("utf-8").replace(x, b""))
        except: pass

    for x in special_hyphens_list:
        try:
            title = bytes.decode(title.encode("utf-8").replace(x, b"-"))
        except: pass

    for x in special_double_quotes_list:
        try:
            title = bytes.decode(title.encode("utf-8").replace(x, b"\""))
        except: pass

    return title        

def determine_target(url):
    doctype = url.split("/")[2].lower()
    
    if doctype == "act":
        tgt_title, tgt_url, tgt_url_broad = standardize_act_target(url)
    if doctype == "cfr":
        tgt_title, tgt_url, tgt_url_broad = standardize_cfr_target(url)
    if doctype == "pl":
        tgt_title, tgt_url, tgt_url_broad = standardize_pl_target(url)
    if doctype == "stat":
        tgt_title, tgt_url, tgt_url_broad = standardize_stat_target(url)
    if doctype == "usc":
        tgt_title, tgt_url, tgt_url_broad = standardize_usc_target(url)

    return tgt_title, tgt_url, tgt_url_broad
    
    
def xml_parse(full_path):
    
    ''' This function handles primary attribute collection. It calls additional 
    functions as necessary in order to clean data points and standardize them 
    into matching formats. '''
    
    outpath = "tmp/netdata/{}/".format(src_doctype)
    csv_edge_path = "{}{}-edgelist.csv".format(outpath, src_doctype)
    csv_node_path = "{}{}-nodelist.csv".format(outpath, src_doctype)
    
    soup = Soup(open(full_path, "rb").read())
    # in Cornell's CFR, the first <num> tag is the title number. Other <num> tags are used elsewhere. 
    docnum = soup.find("num").text
    
    section_list = soup.findAll("section")
    
    fieldnames = ["Source", "Source_Heading", "Target", "Source_url", "Target_url", "Target_url_broad", "Context", "Original_Citation_Text", "Source_Doctype", "Target_Doctype", ]

    # Check if the desired filepath exists. If not, create by writering a header; but, if so, just skip this step. 
    if not os.path.exists(csv_edge_path):
        with open(csv_edge_path, "w", encoding="UTF-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
   
    for section in section_list:
        try:
            data = {}
            
            # create basic section-level data that's readily available and only needs to be pulled once
            data["section"] = section.num.text
            #print(data["section"])
            data["Source_url"] = "/us/{}/{}/{}".format(src_doctype.lower(), docnum.split(" ")[0], data["section"])
            data["Source"] = "{} {} {}".format(data["Source_url"].split("/")[3], src_doctype.upper(), data["Source_url"].split("/")[4])
            data["Source_Heading"] = standardize_special_characters("{} {}".format(section.num.text, section.subject.text.strip()))
                
            data["Source_Doctype"] = src_doctype
            del(data["section"])
            # now dive into the section to identify references

            ref_list = section.findAll("aref")
            
            # now look at each reference link in turn
            for reference in ref_list:
                #print(reference.parents)
                url = str
                l = list([x.name for x in reference.parents])
                if reference["type"] == "CFR":
                    
                    sub = reference.subref["psec"].strip("#").split("_")
                    subs = "{}".format("/".join(x for x in sub).strip("(")).replace("()", "")
                    url = "/us/{}/{}/{}.{}/{}".format(reference["type"], reference.subref["title"], reference.subref["part"], reference.subref["sect"], subs).replace("//", "/").lower()
                    
                elif reference["type"] == "USC":                                        
                    sub = reference.subref["psec"].strip("#").split("_")
                    subs = "{}".format("/".join(x for x in sub).strip("(")).replace("()", "")
                    url = "/us/{}/{}/{}/{}".format(reference["type"], reference.subref["title"], reference.subref["sect"], subs).replace("//", "/").lower()

                else:
                    print(reference["type"])
                    url = "/us/stat/999/999fake"
                    
                if not url.endswith("999fake"):
                    title, url, url_broad = determine_target(url)  
                        
                    if reference.parent.name == "p" or reference.parent.name == "heading" or reference.parent.name == "chapeau":
                        context = standardize_special_characters("{}".format(reference.parent.text.replace("\n", "\\\\n").strip()))
                    else:
                        context = standardize_special_characters("{}".format(reference.parent.parent.text.replace("\n", "\\\\n").strip()))
                                                
                    data["Target_url"] = url
                    data["Target_url_broad"] = url_broad
                    data["Target"] = title #"{} {} {}".format(data["Target_url"].split("/")[3], src_doctype, data["Target_url"].split("/")[4])
                    data["Target_Doctype"] = url.split("/")[2].lower()
                    data["Context"] = context
                    data["Original_Citation_Text"] = standardize_special_characters("{}".format(reference.text))
                    #print(data)
                    with open(csv_edge_path, "a", encoding="UTF-8") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                        writer.writerow(data)
        except:
            pass
    
    # write out the dictionary data for nodes ONLY. Remember to collect text data
    #with open(csv_node_path, "a", encoding="UTF-8") as f:
    #    writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
    #    writer.writerow(data)

def sections_to_txt(full_path):
    
    soup = Soup(open(full_path, "rb").read())

    docnum = soup.find("docnumber").text
    file = full_path.split("/")[-1].split(".")[0].replace(src_doctype.lower(),"").lstrip("0")
    
    for section in soup.findAll("section"):
        sec = ""
        sec = section.num["value"]
        sec = sec.replace(", ", "-")
        sec = sec.replace(" to ", "-")
        
        clears = [section.sourcecredit, section.notes]
        try:
            for c in clears:
                if c is not None:
                    c.clear()
        except: continue
        
        try:    content = section.text.strip()
        except: content ="(Document text unavailable.)"
        #sec = sec.zfill(2)
        outpath = "texts/{}/{}/sections/".format(src_doctype, file)        

        if section.has_key("identifier") and str(sec.lstrip("0")) in section["identifier"]:        
            if not os.path.exists(outpath):
                os.makedirs(outpath)
    
            filepath = "{}{}.txt".format(outpath, sec)
            if not os.path.exists(filepath):
                f = open(filepath, 'w', encoding="utf-8")

                text = "{}".format(content).strip()
                text = standardize_special_characters(text.replace("\n", "\\\\n").strip())

                f.write(text)
                #print("   --Text added to directory {}".format(outpath))
    return docnum
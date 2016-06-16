# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 15:00:35 2015

@author: smichel

#reg_list_master currently uses regex patterns where sections are ID'd to the right of the title object. 
Change this variable identifier to specify this condition, then replicate and modify the same patterns to identify sections to the left of the title object (e.g. "(of|in) section * of some_title"). 
These separate master lists need to be handled separately, as returned patterns will have very different tuple ordering. 
Should be able to find a universal pattern so that index values in the organized tuples are consistent with the appropriate right/left class, regardlesss of what doctype is found. 

"""

import csv
from bs4 import BeautifulSoup as Soup
import os
import calendar
import re
    
src_doctype = "cfr"

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
    tgt_url = tgt_url.replace("(", "/").replace(")", "")
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

def standardize_fr_target(tgt_url):
    ''' Produce label for identified Federal Regulations target based 
    on URL. This is cleaner than pulling the text and accounting for typos and 
    inconsistencies.'''
    tgt_url = tgt_url.replace("(", "/").replace(")", "")
    surl = tgt_url.split("/")    

    try:
        if "s" in surl[4] or surl[4][0].isdigit():
            tgt_title = "{} FR {}".format(surl[3].replace("t", ""), surl[4].replace("s", ""))
        else:
            tgt_title = "{} FR".format(surl[3].replace("t", ""))
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
    
    surl = tgt_url.replace("-", "/").split("/")    
    
    try:    surl[5] = surl[5].lstrip("s")
    except: pass
    tgt_url = "{}/{}".format("/".join(x for x in surl[:3]), "/".join(x for x in surl[4:]))

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
    
    tgt_url = tgt_url.replace("(", "/").replace(")", "")
    surl = tgt_url.split("/")    
        
    tgt_title = str
    try:
        tgt_title = "{} USC {}".format(surl[3].replace("t", ""), surl[4].replace("s", ""))

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

    title = title.replace("  ", " ")

    return title        

def determine_target_doctype(regex_function):
    if regex_function == reg_list_CFR:
        doctype = "CFR"
        
    elif regex_function == reg_list_FR:
        doctype = "FR"

    elif regex_function == reg_list_PL:
        doctype = "PL"
                    
    elif regex_function == reg_list_STAT:
        doctype = "Stat."

    elif regex_function == reg_list_USC:
        doctype = "USC"
    return doctype

def determine_target(url):

    doctype = url.split("/")[2]
    
    if doctype == "act":
        tgt_title, tgt_url, tgt_url_broad = standardize_act_target(url)
    if doctype == "cfr":
        tgt_title, tgt_url, tgt_url_broad = standardize_cfr_target(url)
    if doctype == "fr":
        tgt_title, tgt_url, tgt_url_broad = standardize_fr_target(url)
    if doctype == "pl":
        tgt_title, tgt_url, tgt_url_broad = standardize_pl_target(url)
    if doctype == "stat":
        tgt_title, tgt_url, tgt_url_broad = standardize_stat_target(url)
    if doctype == "usc":
        tgt_title, tgt_url, tgt_url_broad = standardize_usc_target(url)

    return tgt_title.strip(), tgt_url.strip(), tgt_url_broad.strip()
    
def get_only_text(elem, removalList):

    txt = elem.text
    try:
        txt = txt.replace(elem.su.text, "")
    except:
        pass
    return txt
    
def xml_parse(full_path, citations=False):
    ''' This function handles primary attribute collection. It calls additional 
    functions as necessary in order to clean data points and standardize them 
    into matching formats. '''
    
    outpath = "tmp/netdata/{}/".format(src_doctype)
    csv_edge_path = "{}{}-edgelist.csv".format(outpath, src_doctype)
    csv_node_path = "{}{}-nodelist.csv".format(outpath, src_doctype)
    
    soup = Soup(open(full_path, "rb").read())
    docnum = soup.find("titlenum").text.replace("Title ", "")


    fieldnames = ["Source", "Source_Heading", "Target", "Source_url", "Target_url", "Target_url_broad", "Context", "Original_Citation_Text", "Source_Doctype", "Target_Doctype", ]
    
    # Check if the desired filepath exists. If not, create by writering a header; but, if so, just skip this step. 
    if not os.path.exists(csv_edge_path):
        with open(csv_edge_path, "w", encoding="UTF-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
    #ref_list is the "Bread 'n' Butter of the function. Without link data, nothing happens. 
    #add regex here to modify how references are found. 
    #The regex-found items will need to modified, first to create the url, then the url parsed to create standardized titling in the function salready used by USC and HR programs. 

#    section_to_search = soup.findAll("section").text

    #''' REGEX CODES FOR CFR '''
    cfrTitle = "([\\d]+)\\s*C\\.?F\\.?R\\.?\\s*"
    cfrNumbers = "[0-9]+[a-z]*,?\\s*"
    cfrAlphaNum = "([0-9]+|[a-z]+)+,?\\s*"
    cfrSubsec = "([0-9]+|[a-z]+)+"
    cfrSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"
    #cfrSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)" 
    cfrContentPNew = cfrTitle + cfrSection + "(?!\\s*[\\d]*\\s*C\\.?F\\.?R\\.?)"# + "((?:((and|through|to|or|,)*\\s*(" + cfrNumbers + ")?(\\.|\\-)?(" + cfrNumbers + ")?^(\\s*C\\.?F\\.?R\\.?))+|((\\.|\\-)" + cfrNumbers + ")+)+)?"
    ### comfortable checkpoint: cfrContentPNew = cfrTitle + cfrSection + "((?:(" + cfrNumbers + ")+|((and|through|to|or|,)\\s*" + cfrNumbers + "^(C\\.?F\\.?R\\.?))+|((\\.|\\-)" + cfrNumbers + ")+)+)?"
    #"|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:\\-?\\d+(?:\\.\\d+)?^(\\s*C\\.?F\\.?R\\.?)(?:\\s*\\([0-9a-z]+\\)^(\\s*C\\.?F\\.?R\\.?))*)|" + "(?:(\\([0-9a-z]+\\))+)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*))+)?"
    #cfrContentPNew = cfrTitle + cfrSection + "((?:(?:et (seq|al)\\.)|" + "(?:(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "(([\\d]+|\\d+|[ILMVX]+),?\\s*)^(\\s*C\\.?F\\.?R\\.?))|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:(\\d+,?\\s)+^(\\s*C\\.?F\\.?R\\.?))|" + "(?:\\-?\\d+(?:\\.\\d+)?^(\\s*C\\.?F\\.?R\\.?)(?:\\s*\\([0-9a-z]+\\)^(\\s*C\\.?F\\.?R\\.?))*)|" + "(?:(\\([0-9a-z]+\\))+)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*))+)?"
# "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*^(\\s*C\\.?F\\.?R\\.?)) # this triggers big changes. 2.5, 2.6, 2.7 look good, hypen thing at bottom looks good, but the 11 cfr #### and 11 cfr #### stays messed up

#backup 2 (more recent)    cfrContentPNew = cfrTitle + cfrSection + "((?:(?:et (seq|al)\\.)|" + "(?:(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "([\\d]+|\\d+|[ILMVX]+),?\\s*)|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:(\\d+,?\\s)+)(?!\\s*CFR)|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*).(?!\\s*CFR)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*)(?!\\s*CFR))+(?!\\s*CFR))?"


#known, safe backup line:    cfrContentPNew = cfrTitle + cfrSection + "((?:(?:et (seq|al)\\.)|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:(\\d+,?\\s)+)(?!\\s*CFR)|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*).(?!\\s*CFR)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*)(?!\\s*CFR))+)?"

    #original code: 
    #cfrContentPNew = "([\\d]+)\\s*CFR\\s*(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "([\\d]+|\\d+|[ILMVX]+),?\\s*" + "((?:(?:et (seq|al)\\.)|" + "(?:\\s*(and|through|or|,)\\s+)|" + "(?:(\\d+,?\\s)+)|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\([0-9a-z]+\\))*)|" + "(?:\\.[0-9a-z]+(?:\\([0-9a-z]+\\))*))+)?"
    
    #''' REGEX CODES FOR FR'''
    frTitle = "([\\d]+)\\s*F\\.?R\\.?\\s*"
    frNumbers = "[0-9]+[a-z]*,?\\s*"
    frAlphaNum = "([0-9]+|[a-z]+)+,?\\s*"
    frSubsec = "([0-9]+|[a-z]+)+"
    frSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"
    #cfrSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)" 
    frContentPNew = frTitle + frSection + "(?!\\s*[\\d]*\\s*F\\.?R\\.?)"# + "((?:((and|through|to|or|,)*\\s*(" + cfrNumbers + ")?(\\.|\\-)?(" + cfrNumbers + ")?^(\\s*C\\.?F\\.?R\\.?))+|((\\.|\\-)" + cfrNumbers + ")+)+)?"

    
    #''' REGEX CODES FOR USC '''
    uscTitle = "([\\d]+)\\s*U\\.?S\\.?C\\.?\\s*"
    uscNumbers = "([\\d]+|\\d+),?\\s*"
    uscAlphaNum = "([0-9]+|[a-z]+)+,?\\s*"
    uscSubsec = "([0-9]+|[a-z]+)+"
    uscSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"
        
    #uscSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "([\\d]+|\\d+|[ILMVX]+),?\\s*"
    uscContentPNew = uscTitle + uscSection + "(?!\\s*[\\d]*\\s*(U\\.?S\\.?C\\.?))"#+ "(((?:(?:et (seq|al)\\.)|" + "(?:(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "(([\\d]+|\\d+|[ILMVX]+),?\\s*)(?!\\s*USC))|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:([\\d+a-z*],?\\s)+(?!\\s*USC))|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))|" + "(?:(\\([0-9a-z]+\\))+)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))))+(?!\\s*USC)+)?"
    
    #'''# REGEX CODES FOR PL '''
    lawContentP = "(\\b(?:Public|Private|Pub|Priv|Pvt|P)\\.*\\s*(?:Law|L|R)\\.*)\\s*(?:No\\.)?\\s*(\\d+)[-\\xAD]+\\s*(\\d+)"
    multiLawNumbersP = "(\\d+)[-\\xAD]*\\s*(\\d+)"
    multiLawContentP = "(\\b(?:Public|Private|Pub|Priv|Pvt)\\.?\\s*(?:Laws?|L)\\.?)(\\s*)(?:Nos?\\.|Numbers?)?(\\s*\\d+[-]\\d+)"
    #multiLawContentP = "(\\b(?:Public|Private|Pub|Priv|Pvt)\\.?\\s*(?:Laws|L)\\.?)\\s*(?:Nos?\\.|Numbers?)?(\\s*\\d+[-\\xAD]+\\s*\\d+(?:\\b\\d+[-\\xAD]+\\s*\\d+|,|and|\\s+)+)"

    #''' REGEX CODES FOR STATUTES '''
    statTitle = "([\\d]+)\\s*Stat\\.\\s*"
    statSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"    
    statContentPNew = statTitle + statSection + "(?!\\s*[\\d]*\\s*(Stat\\.))"#+ "(((?:(?:et (seq|al)\\.)|" + "(?:(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "(([\\d]+|\\d+|[ILMVX]+),?\\s*)(?!\\s*USC))|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:([\\d+a-z*],?\\s)+(?!\\s*USC))|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))|" + "(?:(\\([0-9a-z]+\\))+)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))))+(?!\\s*USC)+)?"
    #statuteAtLargeP = "([0-9]+)\\s*(?:Stat\\.)\\s*(\\d+[a-z]*(?:-[0-9]+)?(?: et seq\\.)?)"

    #thisSection = uscContentPNew
    thisSection = "(?:((by|in|of|under)?\\s*(this\\s*)?(sub)?(chapter|paragraph|section|part)s?\\s*))"
    localRef = "(" + "((by|in|of|under)?\\s*(sub)?(chapter|paragraph|section|part)s?\\s*)" + "?" + "(\\(" + cfrSubsec + "\\)\\s*)*" + thisSection + ")"# + "(\\(" + cfrSubsec + "\\))*" + "((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to\\s+|or)?\\s*)+)+"
    #localRef = thisSection

    #''' REGEX CODES FOR USC '''
    uscT = "U\\.?\\s*S\\.?\\s*C(?:\\.|ode)?\\s*"
    postAUscT = "app\\.|Appendix"
    singleSectionNoCaptureRegex = "\\d[a-z0-9-]*\\b(?:\\([a-z0-9]+\\))*(?:\\s+note|\\s+et seq\\.?)?"
    singleChapterNoCaptureRegex = "\\d[a-z0-9-]*\\b"
    
    '''
    * Matches following formats: chapter 8 of title 212, United States Code
    * Section 1477 of title 10, United States Code
    '''
    usCodeLargeP = "(?:sections?\\s*(\\w+)\\s*(?:of\\s*))?CHAPTERS?\\s*(\\d+[a-z]*) of title (\\d+),\\s*UNITED\\s*STATES\\s*CODE"

    ''' 
    * Matches the following formats: 42 USC 1526 42 U.S.C. 1526 42 U.S.
    * Code 1526 42 US Code 1526. All previous formats plus the following appendix
    * and details 42 USC app. 1526 42 USC appendix 1526 42 USC app. 1526, 1551,
    * 1553, 1555, and 1561
    '''
    #usCodeShortA2P = "[0-9]+\\s*U\\.?\\s*S\\.?\\s*C(?:\\.|ode)?\\s*"
    usCodeShortA2P = "([0-9]+)\\s*" + uscT + "(?:" + postAUscT + ")\\s*(?:((?:(?:and )?\\d+[az]*(?:,\\s*)?)+(?:-[\\w]+)?)((?:\\([\\w]+\\))*\\s*(?:note|et seq\\.)?))"
    usCodeLarge2P = "CHAPTER\\s*(\\d+[a-z]*)(?: \\([^\\)]*\\)) of title (\\d+),\\s*UNITED\\s*STATES\\s*CODE"
    usCodeMultiLargeSectionsBP = "sections?\\s+(.{1,100}?)\\s+of\\s+title\\s+(\\d+)(?:,|\\sof\\s+the)?\\s+united\\s+states\\s+code"
    usCodeMultiShortSectionsP = "([0-9]+)\\s*" + uscT + "(?:sections?|sec\\.?)?\\s*" + "((?:" + singleSectionNoCaptureRegex + "(?!\\s+" + uscT + ")" + "|and|through|,|\\s)+)"
    usCodeMultiShortChaptersP = "([0-9]+)\\s*" + uscT + "(?:chapters?|ch\\.?)\\s*" + "((?:" + singleChapterNoCaptureRegex + "(?!\\s+" + uscT + ")" + "|and|through|,|\\s)+)"

    ''' COMPOSE LISTS OF REGEX CODES FOR CLEANER UTILITY VIA LIST ITERATION '''
    reg_list_CFR = [cfrContentPNew]
    reg_list_FR = [frContentPNew]
    reg_list_PL = [multiLawContentP]
    #reg_list_STAT = [statuteAtLargeP]
    reg_list_STAT = [statContentPNew]
    reg_list_USC = [uscContentPNew]
    reg_list_local = [localRef]
    reg_list_master = [reg_list_CFR, reg_list_FR, reg_list_PL, reg_list_STAT, reg_list_USC]
#    reg_list_master = [reg_list_local]
    outpath = "tmp/netdata/{}/".format(src_doctype)
    csv_path = "{}{}-netdata.csv".format(outpath, full_path.split("/")[-1].split(".")[0])
    if not os.path.exists(outpath):
            os.makedirs(outpath)
            
    print("   --Adding data to {}".format(csv_path))
    with open(csv_edge_path, "a", encoding="UTF-8") as f:
        writer = csv.writer(f, delimiter = ",", quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerow(["Source", "Source_Heading", "Target", "Source_url", "Target_url", "Target_url_broad", "EdgeType", "Note", "Context", "Source_Doctype", "Target_Doctype", "Citation"])
        for section in soup.findAll("section"):

            try:
                data = {}
                # create basic section-level data that's readily available and only needs to be pulled once
                #<section><sectno>""
                data["section"] = section.sectno.text.strip().split(" ")[-1]
                #print(data["section"])
                data["Source_url"] = "/us/{}/{}/{}".format(src_doctype.lower(), docnum.split(" ")[0], data["section"]).strip()
                data["Source"] = "{} {} {}".format(data["Source_url"].split("/")[3], src_doctype.upper(), data["Source_url"].split("/")[4]).strip()
                data["Source_Heading"] = standardize_special_characters("{} {}".format(section.sectno.text, get_only_text(section.subject, [section.subject.su])).replace("\n", "").replace("  ", " "))
                data["Source_Doctype"] = src_doctype
                sec = data["section"].strip()
                del(data["section"])
#                print(data)

                for reg_list in reg_list_master:
                    if reg_list == reg_list_CFR:
                        data["Target_Doctype"] = "cfr"
                    
                    if reg_list == reg_list_FR:
                        data["Target_Doctype"] = "fr"                
                
                    elif reg_list == reg_list_PL:
                        data["Target_Doctype"] = "pl"
                                    
                    elif reg_list == reg_list_STAT:
                        data["Target_Doctype"] = "stat"
                
                    elif reg_list == reg_list_USC:
                        data["Target_Doctype"] = "usc"

                    elif reg_list == reg_list_local:
                        data["Target_Doctype"] = src_doctype

                    else:
                        data["Target_Doctype"] = "other"

                    for x in reg_list:
                        try:
                            #match = x
                            match = re.compile(x, re.IGNORECASE)
                            p_set = section.findAll("p")
                            for p in p_set:
                                # now dive into the section to identify references
#                                ref_list = re.findall(match, p.text)
#                                if sec == "1.1":
#                                    print("1.1", p, ref_list)

                                # now look at each reference link in turn                
                                for reference in match.finditer(p.text):
#                                    if sec == "1.14":
#                                        print(reference, len(ref_list))
                                    # a tuple of the matched components of our desired pattern is easier to work with. Create that tuple. Note that re.findall() would return this by default, but we need finditer() to get the start() and end() positions of the text, which allows us to catch the original text
                                    ref_tuple = tuple(reference.groups())
                                    #print(ref_tuple)
#                                    print(ref_tuple[2])
                                    citation_list = [x.strip(" ") for x in ref_tuple[2].replace(" ", "").replace(",and", "and").replace("and", ",").replace("or", ",").replace(",,", ",").replace(",", ", ").replace("through", "-").replace("to", "-").strip("-").split(", ") if x.startswith("(") or x[:1].isdigit() or x.isdigit()]
                                    #if "and" in ref_tuple[2]:
                                        #print("AND....", ref_tuple[2], citation_list)
#                                    print(p.text[reference.start():reference.end()].strip(" ").strip(","))
                                    #print(citation_list, ref_tuple[2], ref_tuple[2].replace(" ", "").replace("and", ", ").replace("or", ", ").replace(",, ", ",").replace(",", ", ").replace("through", "-").strip("-").split(", "))
                                    junk1, base_url, junk2 = determine_target("/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation_list[0]).strip(","))
                                    base_url_list = base_url.split("/")
                                    base_alpha = [base_url_list.index(i) for i in base_url_list if i.isalpha()]
                                    base_digit = [base_url_list.index(i) for i in base_url_list if i.isdigit()]
                                    for citation in citation_list:
                                        if citation.startswith("("):
                                            #print("\n", citation_list)
                                            if citation[1].isdigit():
                                                #print("digit:", base_url, base_url_list[max(base_digit)], citation)
                                                title, url, url_broad = determine_target("{}{}".format("/".join(base_url_list[:max(base_digit)]),citation))
                                                #print(url)
                                                '''
                                                print("DIGIT FOUND:", citation)
                                                print(base_url.split("/"))                                                                                                
                                                url = "{}{}".format("/".join(base_url.split("/")[:-1]), citation)
                                                title, url, url_broad = determine_target(url)
                                                print(url)
                                                '''
                                            elif citation[1].isalpha():
                                                #print("alpha:", base_url, base_url_list[max(base_alpha)], citation)
                                                title, url, url_broad = determine_target("{}{}".format("/".join(base_url_list[:max(base_alpha)]),citation))
                                                #print(url)
                                                '''
                                                print("ALPHA FOUND:", citation)
                                                print(base_url.split("/"))
                                                url = "{}{}".format("/".join(base_url.split("/")[:-1]), citation)
                                                title, url, url_broad = determine_target(url)
                                                print(url)
                                                '''
                                            else:
                                                url = "/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation).strip(",")
                                                title, url, url_broad = determine_target(url)  
                                        else:
                                            url = "/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation).strip(",")
                                            title, url, url_broad = determine_target(url)
                                            junk1, base_url, junk2 = determine_target("/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation).strip(","))
                                            base_url_list = base_url.split("/")
#                                        print(url)
                                        #if reference.parent.name == "p" or reference.parent.name == "heading" or reference.parent.name == "chapeau":
                                        #    context = standardize_special_characters("{}".format(reference.parent.text.replace("\n", "\\\\n").strip()))
                                        #else:
                                        #    context = standardize_special_characters("{}".format(reference.parent.parent.text.replace("\n", "\\\\n").strip()))
                                                                    
                                        data["Target_url"] = url.strip()
                                        data["Target_url_broad"] = url_broad.strip()
                                        data["Target"] = title.strip()#"{} {} {}".format(data["Target_url"].split("/")[3], src_doctype, data["Target_url"].split("/")[4])
                                        data["Context"] = standardize_special_characters(p.text.replace("\n", "\\\\n").strip())
                                        data["Original_Citation_Text"] = standardize_special_characters(p.text[reference.start():reference.end()].replace("\n", "")).strip()#standardize_special_characters("{}".format(reference))
                                        #`data["Citation"] = reference
                                        #print(data)
                                        
                                        with open(csv_edge_path, "a", encoding="UTF-8") as f:
                                            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                                            writer.writerow(data)
                            
                            if citations == True:
                                match = re.compile(x, re.IGNORECASE)
                                citation_set = section.findAll("cita")
                                for p in citation_set:
                                    # now dive into the section to identify references
    #                                ref_list = re.findall(match, p.text)
    #                                if sec == "1.1":
    #                                    print("1.1", p, ref_list)
                                    # now look at each reference link in turn                
                                    for reference in match.finditer(p.text):
    #                                    if sec == "1.14":
    #                                        print(reference, len(ref_list))
                                        # a tuple of the matched components of our desired pattern is easier to work with. Create that tuple. Note that re.findall() would return this by default, but we need finditer() to get the start() and end() positions of the text, which allows us to catch the original text
                                        ref_tuple = tuple(reference.groups())
    #                                    print(ref_tuple[2])
                                        citation_list = [x.strip(" ") for x in ref_tuple[2].replace(" ", "").replace(",and", "and").replace("and", ",").replace("or", ",").replace(",,", ",").replace(",", ", ").replace("through", "-").replace("to", "-").strip("-").split(", ") if x.startswith("(") or x[:1].isdigit() or x.isdigit()]
                                        #if "and" in ref_tuple[2]:
                                            #print("AND....", ref_tuple[2], citation_list)
    #                                    print(p.text[reference.start():reference.end()].strip(" ").strip(","))
                                        #print(citation_list, ref_tuple[2], ref_tuple[2].replace(" ", "").replace("and", ", ").replace("or", ", ").replace(",, ", ",").replace(",", ", ").replace("through", "-").strip("-").split(", "))
                                        junk1, base_url, junk2 = determine_target("/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation_list[0]).strip(","))
                                        base_url_list = base_url.split("/")
                                        base_alpha = [base_url_list.index(i) for i in base_url_list if i.isalpha()]
                                        base_digit = [base_url_list.index(i) for i in base_url_list if i.isdigit()]
                                        for citation in citation_list:
                                            if citation.startswith("("):
                                                #print("\n", citation_list)
                                                if citation[1].isdigit():
                                                    #print("digit:", base_url, base_url_list[max(base_digit)], citation)
                                                    title, url, url_broad = determine_target("{}{}".format("/".join(base_url_list[:max(base_digit)]),citation))
                                                    #print(url)
                                                    '''
                                                    print("DIGIT FOUND:", citation)
                                                    print(base_url.split("/"))                                                                                                
                                                    url = "{}{}".format("/".join(base_url.split("/")[:-1]), citation)
                                                    title, url, url_broad = determine_target(url)
                                                    print(url)
                                                    '''
                                                elif citation[1].isalpha():
                                                    #print("alpha:", base_url, base_url_list[max(base_alpha)], citation)
                                                    title, url, url_broad = determine_target("{}{}".format("/".join(base_url_list[:max(base_alpha)]),citation))
                                                    #print(url)
                                                    '''
                                                    print("ALPHA FOUND:", citation)
                                                    print(base_url.split("/"))
                                                    url = "{}{}".format("/".join(base_url.split("/")[:-1]), citation)
                                                    title, url, url_broad = determine_target(url)
                                                    print(url)
                                                    '''
                                                else:
                                                    url = "/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation).strip(",")
                                                    title, url, url_broad = determine_target(url)  
                                            else:
                                                url = "/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation).strip(",")
                                                title, url, url_broad = determine_target(url)
                                                junk1, base_url, junk2 = determine_target("/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation).strip(","))
                                                base_url_list = base_url.split("/")
                                            #if reference.parent.name == "p" or reference.parent.name == "heading" or reference.parent.name == "chapeau":
                                            #    context = standardize_special_characters("{}".format(reference.parent.text.replace("\n", "\\\\n").strip()))
                                            #else:
                                            #    context = standardize_special_characters("{}".format(reference.parent.parent.text.replace("\n", "\\\\n").strip()))
                                                                        
                                            data["Target_url"] = url.strip()
                                            data["Target_url_broad"] = url_broad.strip()
                                            data["Target"] = title.strip()#"{} {} {}".format(data["Target_url"].split("/")[3], src_doctype, data["Target_url"].split("/")[4])
                                            data["Context"] = standardize_special_characters(p.text.replace("\n", "\\\\n").strip())
                                            data["Original_Citation_Text"] = standardize_special_characters(p.text[reference.start():reference.end()].replace("\n", "")).strip()#standardize_special_characters("{}".format(reference))
                                            #`data["Citation"] = reference
                                            
                                            with open(csv_edge_path, "a", encoding="UTF-8") as f:
                                                writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                                                writer.writerow(data)
                        except:
                            pass
            except:
                pass
                


def sections_to_txt(full_path):
    
    soup = Soup(open(full_path, "rb").read())

    docnum = soup.find("titlenum").text.replace("Title ", "")
    filesplit = full_path.split("/")[-1].split(".")[0].replace(src_doctype.lower(),"")
    file = filesplit.split("-")[2]
    year = filesplit.split("-")[0]
    
    for section in soup.findAll("section"):
        text = section.text.strip()
        text = standardize_special_characters(text.replace("\n", "\\\\n").strip())
        sec = ""
        sec = standardize_special_characters(section.sectno.text).replace("Sec. ", "")
        sec = sec.replace(", ", "-")
        sec = sec.replace(" to ", "-")
        sec = sec.replace(" through ", "-")

        sec = sec.strip()
#        print(sec)
        outpath = "texts/{}/{}/{}/sections/".format(src_doctype, year, docnum)        
        
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        filepath = "{}{}.txt".format(outpath, sec)
        if not os.path.exists(filepath):
            f = open(filepath, 'w', encoding="utf-8")
            f.write(text)
            print("   --Text added to directory {}".format(filepath))
    return docnum
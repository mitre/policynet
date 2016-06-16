# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 15:00:35 2015

@author: smichel

"""
import json
import csv
from bs4 import BeautifulSoup as Soup
import os
import calendar
import urllib.parse
from unidecode import unidecode
import re

src_doctype = "Strategy" #use lower case: act, cfr, pl, stat, usc

def export_csv(csv_edge_path, data, fieldnames):
    with open(csv_edge_path, "a", encoding="UTF-8") as f:
        writer = csv.DictWriter(f, fieldnames = fieldnames, lineterminator="\n")
        writer.writerow(data)  

def export_json(json_edge_path, json_holder):
    open(json_edge_path,'w').write("[{}]".format(",\n ".join(e for e in json_holder)))


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
        
    tgt_title = str
    try:
        if "s" in surl[4]:
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

def standardize_strategy_target(tgt_url):    
    ''' Produce label for identified USC target based on URL. This is cleaner 
    than pulling the text and accounting for typos and inconsistencies.'''
    
    surl = tgt_url.split("/")    

    tgt_title = str
    try:
        tgt_title = "{} {}".format(surl[2], surl[3])
    except: 
        pass
    
    surl[3] = surl[3].lstrip("t")
    surl[4] = surl[4].lstrip("s")

    tgt_url = "/".join(x for x in surl)

    tgt_url_broad = "/".join(tgt_url.split("/")[0:2])

    print(tgt_url)

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

    if "http" in url or "www" in url:
        doctype = urllib.parse.urlparse(url)
        tgt_url_broad = doctype[2].split("/")[-1]
        #print(doctype[2].split("/")[-1])
        return None, url, tgt_url_broad
    else:
        doctype = url.split("/")[2]
        
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
        if doctype == "strategy":
            tgt_title, tgt_url, tgt_url_broad = standardize_usc_target(url)            

        return tgt_title, tgt_url, tgt_url_broad
    
    
def xml_parse(full_path):
    
    ''' This function handles primary attribute collection. It calls additional 
    functions as necessary in order to clean data points and standardize them 
    into matching formats. '''
    
    outpath = "tmp/netdata/{}/".format(src_doctype)
    csv_edge_path = "{}{}-edgelist.csv".format(outpath, src_doctype)
    csv_node_path = "{}{}-nodelist.csv".format(outpath, src_doctype)
    #json_edge_path = "{}{}-edgelist.json".format(outpath, src_doctype)
    print(full_path.split("/")[-1].split(".")[0])
    json_edge_path = "{}{}-edgelist.json".format(outpath, full_path.split("/")[-1].split(".")[0])
    if os.path.exists(json_edge_path):
        os.remove(json_edge_path)
    
    soup = Soup(open(full_path, "rb").read())
    #docnum = src_doctype
    fieldnames = ["Target", "Target_url", ]
    #fieldnames = ["Source", "Source_Heading", "Target", "Source_url", "Target_url", "Target_url_broad", "Context", "Original_Citation_Text", "Source_Doctype", "Target_Doctype", ]

    # Check if the desired filepath exists. If not, create by writering a header; but, if so, just skip this step. 
    
    if not os.path.exists(csv_edge_path):
        with open(csv_edge_path, "w", encoding="UTF-8") as f:
            writer = csv.DictWriter(f, fieldnames = fieldnames, lineterminator="\n")
            writer.writeheader()
   
    try:
        data = {}
        json_holder = []

        #data["Source"] = src_docname
        #data["Source_Heading"] = src_heading
        #data["Source_url"] = "/us/strategy/{}/{}".format(agency, src_docname)
        
        #url_levels = data["Source_url"].split("/")
        
        '''
        # Begin project-specific data definition
        data["filename"] = full_path.split("/")[-1]
        data["fileurl"] = full_path
        data["url"] = full_path
        for i in range(0,len(url_levels)):
            data["l{}".format(i+1)] = url_levels[i]
        data["heading"] = src_heading
        data["name"] = src_docname
        data["issuingAgency"] = agency
        data["date"] = date
        data["version"] = version
        data["author"] = author
        data["unsaved"] = unsaved
        data["parsed"] = parsed
        data["text"] = text
        data["type"] = src_doctype
        '''
        ref_list = soup.findAll("a")
        
        ## now look at each reference link in turn
        for reference in ref_list:
            ##print(reference.parents)
            if reference.has_attr("href") and "s.html#" not in reference["href"]:
                #print("REF:", reference)

                title, url, url_broad = determine_target(reference["href"])  
                if reference.parent.name == "p" or reference.parent.name == "heading" or reference.parent.name == "chapeau":
                    context = standardize_special_characters("{}".format(reference.parent.text.replace("\n", "\\\\n").strip()))
                else:
                    context = standardize_special_characters("{}".format(reference.parent.parent.text.replace("\n", "\\\\n").strip()))
                data["Target_url"] = url.strip()
                #data["Target_url_broad"] = url_broad
                data["Target"] = unidecode(reference.text).strip() #"{} {} {}".format(data["Target_url"].split("/")[3], src_doctype, data["Target_url"].split("/")[4])
                #data["Target_Doctype"] = unidecode(reference["href"].split("/")[-1].split(".")[-1]).lower().strip()
                #if data["Target_Doctype"] == None or data["Target_Doctype"] == "":
                #    data["Target_Doctype"] = "unknown"
#                data["Context"] = context
                #data["Original_Citation_Text"] = unidecode(standardize_special_characters("{}".format(reference.text)))
                #print(data)
                if data["Target_url"] not in open(csv_edge_path, "r").read():
                    export_csv(csv_edge_path, data, fieldnames)
                    json_holder.append(json.dumps(data))

        # BEGIN REGEX WORK

        #CFR SEARCH PATTERN
        cfrTitle = "([\\d]+)\\s*C\\.?F\\.?R\\.?\\s*"
        cfrNumbers = "[0-9]+[a-z]*,?\\s*"
        cfrAlphaNum = "([0-9]+|[a-z]+)+,?\\s*"
        cfrSubsec = "([0-9]+|[a-z]+)+"
        cfrSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"
        cfrContentPNew = cfrTitle + cfrSection + "(?!\\s*[\\d]*\\s*C\\.?F\\.?R\\.?)"# + "((?:((and|through|to|or|,)*\\s*(" + cfrNumbers + ")?(\\.|\\-)?(" + cfrNumbers + ")?^(\\s*C\\.?F\\.?R\\.?))+|((\\.|\\-)" + cfrNumbers + ")+)+)?"

        #USC SEARCH PATTERN
        uscSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"    
        uscTitle = "([\\d]+)\\s*U\\.?S\\.?C\\.?\\s*"
        uscContentPNew = uscTitle + uscSection + "(?!\\s*[\\d]*\\s*(U\\.?S\\.?C\\.?))"#+ "(((?:(?:et (seq|al)\\.)|" + "(?:(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "(([\\d]+|\\d+|[ILMVX]+),?\\s*)(?!\\s*USC))|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:([\\d+a-z*],?\\s)+(?!\\s*USC))|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))|" + "(?:(\\([0-9a-z]+\\))+)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))))+(?!\\s*USC)+)?"

        #STAT SEARCH PATTERN
        statSection = "(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*((" + cfrNumbers + "((\\.|\\-)" + cfrNumbers +")?" + "((\\(" + cfrSubsec + "\\))*(,|and)*\\s*)*" + "(,|and|through|to|or)?\\s*)+)"
        statTitle = "([\\d]+)\\s*Stat\\.\\s*"
        statContentPNew = statTitle + statSection + "(?!\\s*[\\d]*\\s*(Stat\\.))"#+ "(((?:(?:et (seq|al)\\.)|" + "(?:(Chapters?|Ch\\.|Parts?|Sec\\.|sections?)*\\s*" + "(([\\d]+|\\d+|[ILMVX]+),?\\s*)(?!\\s*USC))|" + "(?:\\s*(and|through|to|or|,)\\s+)|" + "(?:([\\d+a-z*],?\\s)+(?!\\s*USC))|" + "(?:\\-?\\d+(?:\\.\\d+)?(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))|" + "(?:(\\([0-9a-z]+\\))+)|" + "(?:\\.[0-9a-z]+(?:\\s*\\([0-9a-z]+\\))*(?!\\s*USC))))+(?!\\s*USC)+)?"

        #Public Law SEARCH PATTERN
        multiLawContentP = "(\\b(?:Public|Private|Pub|Priv|Pvt)\\.?\\s*(?:Laws?|L)\\.?)(\\s*)(?:Nos?\\.|Numbers?)?(\\s*\\d+[-]\\d+)"

        # Strategy Docs
        # experiment and add optional periods so we can turn this into a more universal regex pattern that caps e.g.: CFR and C.F.R.
        strategydoc = '(((([\\d]+)\\s*)?([A-Z]+[a-z]*[A-Z]+))(\\s+)([\\d]+(.?[\\d]+[A-Za-z]*)?),?\\s*(?:―(([A-Za-z]+,?\\s*)+)+)?)'
        #strategydoc = '([A-Z]+[a-z]*[A-Z]+)(\\s+)([\\d]+(.?[\\d]+[A-Za-z]*)?),?\\s*(?:―(([A-Za-z]+,?\\s*)+)+)?'
        
        reg_list_CFR = [cfrContentPNew]
        reg_list_PL = [multiLawContentP]
        reg_list_STAT = [statContentPNew]
        reg_list_USC = [uscContentPNew]
        reg_list_strategydoc = [strategydoc]
        reg_list_master = [reg_list_CFR, reg_list_PL, reg_list_STAT, reg_list_USC, reg_list_strategydoc]
        #reg_list_master = [reg_list_strategydoc]        
        for reg_list in reg_list_master:
            if reg_list == reg_list_CFR:
                data["Target_Doctype"] = "cfr"

            elif reg_list == reg_list_PL:
                data["Target_Doctype"] = "pl"
                            
            elif reg_list == reg_list_STAT:
                data["Target_Doctype"] = "stat"
        
            elif reg_list == reg_list_USC:
                data["Target_Doctype"] = "usc"
            
            elif reg_list == reg_list_strategydoc:
                data["Target_Doctype"] = "Strategy"

            if reg_list != reg_list_strategydoc:
                for x in reg_list:
                    try:
                        match = re.compile(x, re.IGNORECASE)
                        # now dive into the section to identify references
                        ref_list = re.findall(match, soup.text)
                        for reference in match.finditer(soup.text):
                            ref_tuple = tuple(reference.groups())
                            citation_list = [x.strip(" ") for x in ref_tuple[2].replace(" ", "").replace(",and", "and").replace("and", ",").replace("or", ",").replace(",,", ",").replace(",", ", ").replace("through", "-").replace("to", "-").strip("-").split(", ") if x.startswith("(") or x[:1].isdigit() or x.isdigit()]
                            junk1, base_url, junk2 = determine_target("/us/{}/{}/{}".format(data["Target_Doctype"].lower(), ref_tuple[0], citation_list[0]).strip(","))
                            base_url_list = base_url.split("/")
                            base_alpha = [base_url_list.index(i) for i in base_url_list if i.isalpha()]
                            base_digit = [base_url_list.index(i) for i in base_url_list if i.isdigit()]
    
                            for citation in citation_list:
                                if citation.startswith("("):
                                    if citation[1].isdigit():
                                        #print("digit:", base_url, base_url_list[max(base_digit)], citation)
                                        title, url, url_broad = determine_target("{}{}".format("/".join(base_url_list[:max(base_digit)]),citation))
                                        #print(url)
                                        '''
                                        print("DIGIT FOUND:", citaion)
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
                                #data["Target_url_broad"] = url_broad
                                data["Target"] = title.strip()#"{} {} {}".format(data["Target_url"].split("/")[3], src_doctype, data["Target_url"].split("/")[4])
                                #data["Context"] = None#unidecode(standardize_special_characters(soup.text.replace("\n", "\\\\n").strip()))
                                #data["Original_Citation_Text"] = unidecode(soup.text[reference.start():reference.end()])#standardize_special_characters("{}".format(reference))
                                try:    del data["Target_Doctype"]
                                except: pass
                                if data["Target_url"] not in open(csv_edge_path, "r").read():
                                    export_csv(csv_edge_path, data, fieldnames)
                                    json_holder.append(json.dumps(data))
                    except:
                        pass
            else:
                reject_list = ["fouo","page","january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
                pre_defined_doctypes = ["act", "cfr", "fr", "pl", "usc", ]
                #reject_list = []
                for x in reg_list:
                    try:
                        match = re.compile(x)
                        # now dive into the section to identify references
                        ref_list = re.findall(match, soup.text)
                        for reference in match.finditer(soup.text):
                            ref_tuple = tuple(reference.groups())
                            if ref_tuple[4].lower() in pre_defined_doctypes:
                                url = "/us/{}/{}/{}".format(ref_tuple[4].lower(), ref_tuple[3], ref_tuple[6])
                            else:
                                url = "/us/strategy/{}/{}".format(ref_tuple[4], ref_tuple[6])                                
                            data["Target_url"] = url.strip()
                            if ref_tuple[4].lower() in pre_defined_doctypes:
                                data["Target"] = ref_tuple[0].split(",")[0].strip()
                            else:
                                data["Target"] = "{} {}".format(ref_tuple[4], ref_tuple[6])
                            try:    del data["Target_Doctype"]                            
                            except: pass
                            if data["Target_url"].split("/")[3].lower() not in reject_list:
                                json_holder.append(json.dumps(data))
#                            title, url, url_broad = determine_target(url)
#                            print(ref_tuple, url)
                    except:
                        pass
        export_json(json_edge_path, set(json_holder))
        os.remove(csv_edge_path)
    except:
        pass
    
    # write out the dictionary data for nodes ONLY. Remember to collect text data
    #with open(csv_node_path, "a", encoding="UTF-8") as f:
    #    writer = csv.DictWriter(f, fieldnames = fieldnames, lineterminator="\n")
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
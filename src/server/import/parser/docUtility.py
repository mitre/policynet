# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:39:35 2015

@author: smichel

NEXT STEPS:

Check this: Add capability for multiple chapters/sections etc. For example "of chapter 51 and subchapter III of chapter 53 of title 5" in 41 USC still only returns "/us/usc/5/51"...

1) Regex still is incomplete. 
    *from file CFR-2014-title38-vol1.xml, we're missing 18 U.S.C., sections 792...: (1) In title 18 U.S.C., sections 792, 793, 794, 798, 2381 through 2385, 2387 through 2390, and chapter 105
    # regarding the above: Regex needs a modification to look for doctype immediately after the title number is identified. It could be abbreviated or spelled-out
    # this will also help resolve the docType identification of titles, which I'm intentionally not auto-assigning based on the source's own docType
    
    * I think what I call right_title docTypes are not fully supported because of the RegEx pattern assuming a fullsection precedes the docType. This needs to be addressed to maximize parsing comprehension. 
    
    UPDATED (ignore for now; not in in-text of most recent USC corpus:
        a) Example from usc31.xml: 41 U.S.C. 7105(a), (c), (d), (e)(1)(C) outputs a correct list, but the (e)(1)(C) gets combined as e1C
        b) Example (same file): Pub. L. 88-58, 77 is a correct capture of PL 88-58 and a partial capture of 77 Stat... This often shows up for PL items in a list, but does happen on other elements too. 
            -> This creates a /us/pl/88/58 and a /us/pl/88/77 (which is wrong because 77 is title for next object)
    
2) Add "acts" to RegEx parse.

3) Condense functions in parse() to outside functions so calls can be made and duplication can be mitigated.

4) Do better at adding comments and cleaning out commented code lines.
"""

from bs4 import BeautifulSoup as Soup # XML-parsing tool
import re #RegEx
from unidecode import unidecode # Library for reducing unicode values into "Americanized" values
import os
from dateutil.parser import parse

        
def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False        

def check_existing_node(node, db):
    status = db.checkNodeExists(node)
    return status

def create_citation_datapoint(data, urlList, capture, db):
    ''' Accepts data from regex and creates a row of data from it.'''
    
    data["srcDocype"] = data["srcUrl"].split("/")[2]
    n = 0
    data["targets"] = {}

    for url, original_citation_text in urlList:
        url = url.strip().strip("-").strip(",").strip("-")
        print(url)
        if (url.split("/")[2].strip() != "") and (url.split("/")[3].strip() != "") and any(x in capture for x in ["all", url.split("/")[2]]):
            n += 1
            data["targets"][n] = {}
            data["targets"][n]["tgtDocType"] = url.split("/")[2]
            data["targets"][n]["original_citation_text"] = original_citation_text
            data["targets"][n]["tgtUrl"] = url
        
            try:
                if data["targets"][n]["tgtDocType"] in ["cfr", "far", "fr", "stat", "usc"]:
                    data["targets"][n]["tgtTitle"] = get_tgt_title(url)
                    #if "(" in data["targets"][n]["tgtTitle"]:
                        #print(data["targets"][n]["tgtTitle"])
                    if check_existing_node(data["targets"][n]["tgtTitle"], db):
                        # if node exists in current format, just go with it and convert to URL
                        data["targets"][n]["tgtUrl"] = url
                    else:
                        # otherwise, take best guess and turn hyphenate into a range, and update title accordingly
                        #data["targets"][n]["tgtUrl"] = url.replace("-", "/") #TO-DO: check that this being commented doesn't break anything. Uncommented, it ruins section numbers with "-" correctly existing in the section. 
                        try:
                            data["targets"][n]["tgtTitle"] = "{} {} {}".format(data["targets"][n]["tgtUrl"].split("/")[3], data["targets"][n]["tgtUrl"].split("/")[2].upper(), data["targets"][n]["tgtUrl"].split("/")[4])
                        except:
                            data["targets"][n]["tgtTitle"] = "{} {}".format(data["targets"][n]["tgtUrl"].split("/")[3], data["targets"][n]["tgtUrl"].split("/")[2].upper())   
                else:
                    data["targets"][n]["tgtTitle"] = get_tgt_title(url)
                    if check_existing_node(data["targets"][n]["tgtTitle"], db):
                        # if node exists in current format, just go with it and convert to URL
                        data["targets"][n]["tgtUrl"] = url
                        #data["targets"][n]["tgtUrl"] = "/us/{}/{}/{}".format(data["srcDocType"], data["targets"][n]["tgtTitle"].split()[1], data["targets"][n]["tgtTitle"].split()[-1])
                    else:
                        # otherwise, take best guess and turn hyphenate into a range, and update title accordingly
                        data["targets"][n]["tgtUrl"] = url#data["targets"][n]["tgtUrl"] = "/us/{}/{}/{}".format(data["srcDocType"], data["targets"][n]["tgtTitle"].split()[1], data["targets"][n]["tgtTitle"].split()[-1].replace("-","/"))
                        if url.split("/")[2] not in ["pl"]:
                            data["targets"][n]["tgtTitle"] = data["targets"][n]["tgtTitle"].split("-")[0]
                            
                    # testSpace: disable the part after "and" to write-out all URLs, even those missing a docType   
                if len(data["targets"][n]["tgtUrl"].split("/")) >=5:
                    data["targets"][n]["tgtUrlBroad"] = "/".join(data["targets"][n]["tgtUrl"].split("/")[:5])
                elif len(data["targets"][n]["tgtUrl"].split("/")) >=4:
                    data["targets"][n]["tgtUrlBroad"] = "/".join(data["targets"][n]["tgtUrl"].split("/")[:4])
                else:
                    data["targets"][n]["tgtUrlBroad"] = data["targets"][n]["tgtUrl"]

                data["targets"][n]["tgtDoctype"] = data["targets"][n]["tgtUrl"].split("/")[2]
        
            
                    #if any(x in capture for x in ["all", data[n]["tgtUrl"].split("/")[2]]) and (data[n]["tgtUrl"].split("/")[2] != " " and data[n]["tgtUrl"].split("/")[3] != " "):
                        #write_edges(data)
            except: 
                print("Failed generating datapoint: {}: {}".format(url, original_citation_text, data["targets"][n]["tgtTitle"]))
                pass#return None

    if data["targets"]:
        write_edges(data, db)


def create_url(srcUrl, cit):
    ''' Creates url out of matched regex-pattern (cit). The srcUrl is included to help determine the value of 'this ___'. '''    
#    print("DATA:", docType, titles, chapters, sections, subsections, paragraphs)
    urlList = []

    known_docTypes_extended = ["Code of Federal Regulations", "United States Code"]

    # left_title indicates that the document's primary identifying number precedes the document (e.g. 18 U.S.C. == title 18 of U.S.C.)
    known_abbrs_left_title = ["cfr", "far", "fr", "stat", "usc", "us"]

    # right_title indicates that the document's primary identifying number follows the document (e.g. E.O. 11222 == Executive Order Number 11222)
    # note: eo (Executive Orders) are frequently spelled out in entire words, so there's another if clause to handle those, too. Public Laws have not been observed except in spelled-out. 
    known_abbrs_right_title = ["eo", "nfpa", "pl"]
            
    citItems= cit.strip().split(" ")

    url = ""

    docType = " "
    title = " " 
    sections = [] # to be clear, this is an item that takes the place of the section-level identifier in our URL structure. This can be qualified by "part" in CFR.
    paragraph = " " # clarification: this isn't necessarily a paragraph, but whatever next-level item below the section exists in a reference
    
    citItems = [c for c in citItems if c != ""]

    for c in citItems:
        c = c.replace("  ", " ").strip()
        #if "Executive" in c:
        #    print(citItems)

    for c in citItems:
        # Handle left_title abbrs
        # convert traditional ## USC ### format ("USC" is just an example)
        if c.replace(".","").lower() in known_abbrs_left_title and len(citItems) > citItems.index(c) + 1: 
            docType = c.replace(".","").lower()
            #print()
            if citItems[citItems.index(c) + 1][0].isdigit():
                for secs in citItems[citItems.index(c) + 1:]:
                    if secs[0].isdigit():
                        sections.append(secs.strip(".").strip(","))

            if citItems[citItems.index(c) - 1][0].isdigit():
                title = citItems[citItems.index(c) - 1].strip(".").strip(",")

        # Handle right_title abbrs
        if c.replace(".","").lower() in known_abbrs_right_title and len(citItems) > citItems.index(c) + 1: 
            docType = c.replace(".","").lower()
            for secs in citItems[citItems.index(c) + 1:]:
                if secs[0].isdigit():
                    title = citItems[citItems.index(c) + 1].strip(".").strip(",")

            #if "_" in section and "(" in section:
            #    url = "/us/{}/{}/{}".format(docType, title, section).strip()            
            #else:
            #    url = "/us/{}/{}/{}".format(docType, title, section).replace("(","/").replace(")","").strip()
            #urlList.append(url)
#            print(url, citItems)

        # convert "Public Law ##-###, ... " format
        elif c.replace(".","") in ["Pub", "Public"] and citItems[citItems.index(c) + 1].replace(".", "") in ["L", "Law"]:
            docType = "pl"
            if len(citItems) > citItems.index(c) + 2:
                title = citItems[citItems.index(c) + 2].replace("-", "/").strip(",")

        # convert "Executive Order [No.] ####"
        elif c.replace(".","") in ["Ex", "Exec", "Executive"] and len(citItems) > citItems.index(c) + 1 and citItems[citItems.index(c) + 1].replace(".", "") in ["Ord", "Order"]:
            docType = "eo"
            if len(citItems) > citItems.index(c) + 2 and citItems[citItems.index(c) + 2].isdigit():
                title = citItems[citItems.index(c) + 2].replace("-", "/").strip(",")

            elif len(citItems) > citItems.index(c) + 3 and citItems[citItems.index(c) + 2].replace(".", "") in ["No", "Number"]:
                title = citItems[citItems.index(c) + 3].replace("-", "/").strip(",")

        # convert "this (something)" format to match currently-parsed information
        elif c.lower() == "this" and len(citItems) > citItems.index(c) + 1:
            # add a handler for "chapter", "subchapter", "part", "subpart", "item", "subitem"
            flag = citItems[citItems.index(c) + 1].lower()
            if flag in ["subtitle", "§", "section", "subsection", "paragraph", "subparagraph", "clause", "subclause"]:
                docType = srcUrl.split("/")[2]
                title = srcUrl.split("/")[3]
                sections.append(srcUrl.split("/")[4])
            elif flag in ["title", "chapter", "subchapter", "subtitle", "part", "subpart"]:
                docType = srcUrl.split("/")[2]
                title = srcUrl.split("/")[3]

        elif citItems.index(c) >= 1 and len(citItems) > citItems.index(c) + 1 and c.lower() == "through" and citItems[citItems.index(c) - 1] == "section":
            sections.append(citItems[citItems.index(c) + 1])

        # convert individual elements identified in the reference into the elements necessary for a URL structure        
        elif c.lower() in ["subtitle", "chapter", "subchapter", "§", "section", "subsection", "paragraph", "subparagraph", "clause", "subclause", "part", "subpart", "title", "subtitle"] and citItems[citItems.index(c) - 1].lower() != "this" and len(citItems) > citItems.index(c) + 1:
            flag = c.lower()
            if flag in ["part", "section", "subsection"] and not sections:
                if citItems[citItems.index(c) + 1][0].isdigit():
                    sections.append(citItems[citItems.index(c) + 1])
            elif flag in ["§"]:
                docType = srcUrl.split("/")[2]
                title = srcUrl.split("/")[3]
                sections.append(citItems[citItems.index(c) + 1])               
            elif flag in ["title"] and title == " ":
                title = citItems[citItems.index(c) + 1]
            elif flag in ["paragraph"] and paragraph == " ":
                paragraph = citItems[citItems.index(c) + 1]                

        # identify multiple elements of a single type identified in the reference
        elif c.lower() in ["§§", "sections", "parts"] and len(citItems) > citItems.index(c) + 1:
            flag = c.lower()
            if flag in ["sections", "parts"]:
                for secs in citItems[citItems.index(c) + 1:]:
                    if secs[0].isdigit():
                        sections.append(secs.strip(".").strip(","))
                    elif secs == "of":
                        break
            elif flag in ["§§"]:
                docType = srcUrl.split("/")[2]
                title = srcUrl.split("/")[3]
                #print(citItems)
                for secs in citItems[citItems.index(c) + 1:]:
                    if secs[0].isdigit():
                        sections.append(secs.strip(".").strip(","))
                    elif secs == "of":
                        break
                                    
    if url == "":    
        if docType == " ":
            for y in known_docTypes_extended: 
                if y in cit:
                    doc = "".join([z[0] for z in y.strip().split(" ") if z[0].isupper()]).strip().lower()
                    if doc in known_abbrs_left_title or doc in known_abbrs_right_title:
                        docType = doc
                    else: 
                        docType = " "
            else:
                if docType == " ":
                    docType = srcUrl.split("/")[2]

        if title and not sections:
            if docType == " ":
                docType = srcUrl.split("/")[2]
            url = "/us/{}/{}".format(docType, title).strip()
            urlList.append(url)

        else:        
            for section in sections:        
                if ("_" in section and "(" in section) or "_et_seq" in section:
                    url = "/us/{}/{}/{}".format(docType, title, section).strip()
                else:
                    url = "/us/{}/{}/{}/{}".format(docType, title.strip("-").strip(".").strip(","), section.strip(".").strip(","), paragraph.strip(".")).replace("(","/").replace(")","").replace("//","/").strip().strip(",")
                if url.endswith("/"):
                    url = url[:-1] # remove final "/" just for consistency
                urlList.append(url)#.replace("-/","_to_")) #TO-DO: make sure commenting this doesn't break the code. Uncommented, it removes "-" from legitimate section numbers

    return urlList

def create_urlList(reference):
    urlList = []
    known_docs = ["cfr", "far", "fr", "usc", "us"]
    components = dict()
    reference = reference.replace(" through ", "_through_").replace(" to ", "_to_").strip()
    reference = reference.strip("_through_").strip("_to_").strip()
    itemList = reference.replace(" (","(").replace(",(",", (").replace("and(", "and (").split(" ")
    for x in itemList:
        if x.replace(".","").lower() in known_docs:
            components["docType"] = x.replace(".","").lower()
            components["title"] = itemList[itemList.index(x) - 1]  
            
            if itemList[itemList.index(x) + 1] in ["part", "subpart", "paragraph", "paragraphs", "section", "subsection"]:
                components["section"] = itemList[itemList.index(x) + 2]
            else:
                components["section"] = itemList[itemList.index(x) + 1]
            
            base_url = "/us/{}/{}/{}".format(components["docType"], components["title"], components["section"]).replace("(", "/").replace(")","").replace("-/","-").strip(",").strip().strip(".").strip("-")
            urlList.append(base_url)

            
            if len(itemList) > itemList.index(x) + 2:
                base_url_list = base_url.split("/")    
                #print(base_url_list)
                base_alpha_upper = [base_url_list.index(i) for i in base_url_list[1:] if i[0].isalpha() and i[0].isupper()]
                base_alpha_lower = [base_url_list.index(i) for i in base_url_list[1:] if i[0].isalpha() and i[0].islower()]
                base_digit = [base_url_list.index(i) for i in base_url_list[1:] if i[0].isdigit()]

                for i in itemList[itemList.index(x)+2:]:
                    if i not in ["and", "&", "or","through","to"]:
                        i = i.strip("(").strip(")")
                        if i[0].isdigit():
                            url = "{}/{}".format("/".join(base_url_list[:max(base_digit)]), i).strip(",").replace("(","/").replace(")","")
                            urlList.append(url)
                        elif i[0].isalpha() and i[0].isupper():
                            url = "{}/{}".format("/".join(base_url_list[:max(base_alpha_upper)]), i).strip(",").replace("(","/").replace(")","")
                            urlList.append(url)
                        elif i[0].isalpha() and i[0].islower():
                            url = "{}/{}".format("/".join(base_url_list[:max(base_alpha_lower)]), i).strip(",").replace("(","/").replace(")","")
                            urlList.append(url)
    return urlList

def write_edges(dataList, db):
    #db.insertEdge(dataList["srcTitle"], dataList["srcHeading"], dataList["tgtTitle"], dataList["srcUrl"], dataList["tgtUrl"], dataList["tgtUrlBroad"], dataList["context"], dataList["original_citation_text"], dataList["location"], dataList["srcUrl"].split("/")[2], dataList["tgtUrl"].split("/")[2], dataList["source_ver"], dataList["original_date"], dataList["source_date"])
    db.insertEdge(dataList)

def create_nodelists(dataLists, db):
    db.insertNodes(dataLists)#dataList["node"], dataList["heading"], dataList["url"], dataList["doctype"], dataList["text"], dataList["xml"], dataList["l1"], dataList["l2"], dataList["l3"], dataList["l4"])

def create_node_metric(dataList, db):
    #db.insertEdge(dataList["srcTitle"], dataList["srcHeading"], dataList["tgtTitle"], dataList["srcUrl"], dataList["tgtUrl"], dataList["tgtUrlBroad"], dataList["context"], dataList["original_citation_text"], dataList["location"], dataList["srcUrl"].split("/")[2], dataList["tgtUrl"].split("/")[2], dataList["source_ver"], dataList["original_date"], dataList["source_date"])
    db.insertNodeMetric(dataList)

def create_edge_metric(dataList, db):
    #db.insertEdge(dataList["srcTitle"], dataList["srcHeading"], dataList["tgtTitle"], dataList["srcUrl"], dataList["tgtUrl"], dataList["tgtUrlBroad"], dataList["context"], dataList["original_citation_text"], dataList["location"], dataList["srcUrl"].split("/")[2], dataList["tgtUrl"].split("/")[2], dataList["source_ver"], dataList["original_date"], dataList["source_date"])
    db.insertEdgeMetric(dataList)

def get_clean_url(url):
    if not url.startswith("/us/"):
        url = "/us/{}".format(url).replace("//","/")
    urlSet = url.split("/")
    urlSet[3] = urlSet[3].strip("t")
    if len(urlSet) >= 5:
        urlSet[4] = urlSet[4].strip("s").strip("ch")
    if len(urlSet) >= 6:
        urlSet[5] = urlSet[5].strip("s")
    newurl = "/".join(urlSet)
    return newurl     

def create_nodelists2(outputs=["all"]):
    if ("all" or "csv") in outputs:
        import csv
        csv.field_size_limit(2147483647)
        # review the edgelist and get nodes from it, store them in dictionary

    if any(x in outputs for x in ["all", "csv"]):
        import csv

        data = {} 
        edgelistPath = "../output/edgelists/"
        for file in os.listdir(edgelistPath):
            with open("{}{}".format(edgelistPath, file), "r", newline="\n") as edgeFile:
                reader = csv.reader(edgeFile)
                for line in reader:
                    data[line[0]] = {}
                    data[line[0]]["url"] = line[3]
                    data[line[0]]["heading"] = line[1]
    #                print(data[line[0]]["heading"])
    
            with open("{}{}".format(edgelistPath, file), "r", newline="\n") as edgeFile:
                reader = csv.reader(edgeFile)
                for line in reader:
                    if line[2] not in data.keys():
                        data[line[2]] = {}
                        data[line[2]]["url"] = line[5]
                            
            # get unnamed references too
            #with open("../output/{}-nodelist.csv".format(data[x]["url"].split("/")[2]), "a", newline="\n") as nodeFile:
            for docTypeFolder in os.listdir("../output/xml/"):
                for titleFolder in os.listdir("../output/xml/{}".format(docTypeFolder)):
                    for sectionFile in os.listdir("../output/xml/{}/{}/sections/".format(docTypeFolder, titleFolder)):
                        if "\n" in sectionFile:
                            print(sectionFile)
                        if "{} {} {}".format(titleFolder, docTypeFolder.upper(), sectionFile.split(".")[0]).replace(" to ", "_to_").replace(" and ", "_and_").replace(" through ", "_through_").replace(" or ", "_or_") not in data.keys():
                            data["{} {} {}".format(titleFolder, docTypeFolder.upper(), sectionFile.split(".")[0]).replace(" to ", "_to_").replace(" and ", "_and_").replace(" through ", "_through_").replace(" or ", "_or_")] = {}
                            data["{} {} {}".format(titleFolder, docTypeFolder.upper(), sectionFile.split(".")[0]).replace(" to ", "_to_").replace(" and ", "_and_").replace(" through ", "_through_").replace(" or ", "_or_")]["url"] = "/us/{}/{}/{}".format(docTypeFolder, titleFolder, sectionFile.split(".")[0].replace(" to ", "_to_").replace(" and ", "_and_").replace(" through ", "_through_").replace(" or ", "_or_"))
    
        for x in data:
            #if "heading" not in data[x].keys():
            #    data[x]["heading"] = x
            if "all" in outputs or data[x]["url"].split("/")[2] in outputs:
                
                if len(data[x]["url"].split("/")) > 3:
                    if not os.path.isfile("../output/{}-nodelist.csv".format(data[x]["url"].split("/")[2])):
                        with open("../output/{}-nodelist.csv".format(data[x]["url"].split("/")[2]), "a", newline="\n") as outfile:
                            writer = csv.writer(outfile)
                            writer.writerow(["Node", "Heading", "url", "Doctype", "Text", "XML", "L1", "L2", "L3", "L4"])
                    doc = data[x]["url"].split("/")[2]
                    try:
                        xml = unidecode(open("../output/xml/{}/{}/sections/{}.txt".format(data[x]["url"].split("/")[2], data[x]["url"].split("/")[3], data[x]["url"].split("/")[4].replace("_", " ")), "r", encoding="utf-8").read()).replace("SS", "§").replace("\n","\\n").replace("\\n","\\\\n")
                        txt = Soup(xml).text
                    except:
                        try:
                            xml = unidecode(open("../output/xml/{}/{}/sections/{}.txt".format(data[x]["url"].split("/")[2], data[x]["url"].split("/")[3], data[x]["url"].split("/")[4].replace("_", " ").replace("_to_",", ")), "r", encoding="utf-8").read()).replace("SS", "§").replace("\n","\\n").replace("\\n","\\\\n")
                            txt = Soup(xml).text
                        except:
                            try:
                                xml = unidecode(open("../output/xml/{}/{}/sections/{}.1.txt".format(data[x]["url"].split("/")[2], data[x]["url"].split("/")[3], data[x]["url"].split("/")[4]), "r", encoding="utf-8").read()).replace("SS", "§").replace("\n","\\n").replace("\\n","\\\\n")
                                txt = Soup(xml).text
                            except:
                                txt = "(Text Unavailable)"
                    
                    if "heading" not in data[x].keys():
                        try:
                            import docInfo
                            s = Soup(open("../output/xml/{}/{}/sections/{}.txt".format(data[x]["url"].split("/")[2], data[x]["url"].split("/")[3], data[x]["url"].split("/")[4].replace("_", " ")), "r", encoding="utf-8"))
                            srcDocType, docNumTag, urlTag, urlAttr, sectionTag, secNumTag, secValueTag, headingTag, headingAltTag, contextTags, citationTag, noteTag, verTag, originalDateTag, verDateTag = docInfo.get(s, data[x]["url"].split("/")[2])
                            try:
                                sec = s.find(secNumTag)
                                sec = "§ {}".format(unidecode(sec[secValueTag]))
                            except:
                                sec = unidecode(s.find(secNumTag).text).replace("SS", "§").strip(" ").strip(".").split(" ")[-1]#.replace("Sec. ", "")
                                sec = sec.strip()
                            data[x]["heading"] = "{} {}".format(sec, unidecode(s.find("heading").text))
                        except:
                            try:
                                s = Soup(open("../output/xml/{}/{}/sections/{}.1.txt".format(data[x]["url"].split("/")[2], data[x]["url"].split("/")[3], data[x]["url"].split("/")[4]), "r", encoding="utf-8"))
                                try:
                                    sec = s.find(secNumTag)
                                    sec = "§ {}".format(unidecode(sec[secValueTag]))
                                except:
                                    sec = unidecode(s.find(secNumTag).text).replace("SS", "§").strip(" ").strip(".").split(" ")[-1]#.replace("Sec. ", "")
                                    sec = sec.strip()
                                data[x]["heading"] = "{} {}".format(sec, unidecode(s.find("heading").text))
                            except:
                                data[x]["heading"] = x
                                

                    with open("../output/{}-nodelist.csv".format(doc), "a", newline="\n") as nodeFile:
                        writer = csv.writer(nodeFile, delimiter=",")
                        for k in data[x]:
                            data[x][k] = data[x][k].replace("\n", "\\n").replace("\\n", "\\\\n")
                        if len(data[x]['url'].split("/")) >= 6:
                            writer.writerow([x, data[x]['heading'], data[x]['url'], data[x]['url'].split("/")[2], txt, xml, data[x]['url'].split("/")[2], data[x]['url'].split("/")[3], data[x]['url'].split("/")[4], data[x]['url'].split("/")[5]])
                        elif len(data[x]['url'].split("/")) >= 5:
                            writer.writerow([x, data[x]['heading'], data[x]['url'], data[x]['url'].split("/")[2], txt, xml, data[x]['url'].split("/")[2], data[x]['url'].split("/")[3], data[x]['url'].split("/")[4], "null"])
                        elif len(data[x]['url'].split("/")) >= 4:
                            writer.writerow([x, data[x]['heading'], data[x]['url'], data[x]['url'].split("/")[2], txt, xml, data[x]['url'].split("/")[2], data[x]['url'].split("/")[3], "null", "null"])
                        '''         
            if regex:
                # review the edgelist created by RegEx search
                with open("../output/{}-edgelist_(RE).csv".format(srcDocType), "r", newline="\n") as edgeFile:
                    data = {}
                    reader = csv.reader(edgeFile)
                    for line in reader:
                        data[line[0]] = {}
                        data[line[1]] = {}
                        data[line[0]]["url"] = line[2]
                        data[line[1]]["url"] = line[3]
    
                    # create the nodelist
                    with open("../output/{}-nodelist.csv".format(srcDocType), "a", newline="\n") as nodeFile:
                        writer = csv.writer(nodeFile, delimiter=",")
                        for k in data.keys():
                            writer.writerow([k, data[k]['url']])    
            '''

def sections_to_txt(full_path, docType, docNumTag, sectionTag, secNumTag, secValueTag, noteTag):
    
    soup = Soup(open(full_path, "rb").read())

    docnum = soup.find(docNumTag).text.replace("Title ", "")
    
    for section in soup.findAll(sectionTag):
        parents = [x.name for x in section.parents]
        if noteTag not in parents:
            text = section.text.strip()
            text = unidecode(text.strip()).replace("SS", "§")
            sec = ""
            try:
                sec = section.find(secNumTag)
                sec = unidecode(sec[secValueTag])
                #print(sec[secValueTag])
            except:
                sec = unidecode(section.find(secNumTag).text).replace("SS", "§").strip(" ").strip(".").split(" ")[-1]#.replace("Sec. ", "")
        #        sec = sec.replace(", ", "-")
                sec = sec.replace(" to ", "_to_")
                sec = sec.replace(" through ", "_to_")
        
                sec = sec.strip()
    #        print(sec)
            outpath = "../output/texts/{}/{}/sections/".format(docType, docnum)
            
            if not os.path.exists(outpath):
                os.makedirs(outpath)
    
            filepath = "{}{}.txt".format(outpath, sec)
            if not os.path.exists(filepath):
                f = open(filepath, 'w', encoding="utf-8")
                f.write(text)
                print("   --Text added to directory {}".format(filepath))

def xml_to_txt(full_path, docType, docNumTag, sectionTag, secNumTag, secValueTag, noteTag):
    
    soup = Soup(open(full_path, "rb").read())

    docnum = soup.find(docNumTag).text.replace("Title ", "")
    
    for section in soup.findAll(sectionTag):
        parents = [x.name for x in section.parents]
        if noteTag not in parents:
            sec = ""
            try:
                sec = section.find(secNumTag)
                sec = unidecode(sec[secValueTag])
            except:
                sec = unidecode(section.find(secNumTag).text).replace("SS", "§").strip(" ").strip(".").split(" ")[-1]#.replace("Sec. ", "")
                sec = sec.replace(" to ", "_to_")
                sec = sec.replace(" through ", "_to_")
        
                sec = sec.strip()
            outpath = "../output/xml/{}/{}/sections/".format(docType, docnum)
            
            if not os.path.exists(outpath):
                os.makedirs(outpath)
    
            filepath = "{}{}.txt".format(outpath, sec)
            if not os.path.exists(filepath):
                f = open(filepath, 'w', encoding="utf-8")
                f.write(str(section))
                print("   --XML added to directory {}".format(filepath))

def get_regex_matches(context, srcUrl, loc, customRegex):
    urlItems = []
    original_citation_text_list = []

    init_digit = "([0-9]+){1}"
    docTypes = "((U\.?S\.?C\.?)|(C\.?F\.?R\.?)|(STAT)|(Stat\.?(?!e))){1}"
    sections = "(([Aa]pp.?\s*)?([0-9]+[A-Za-z.-]*)*(\s*[Ee]t\.?\s*[Ss]eq\.?)?){1}"
    paren = "\([0-9]{0,6}[A-Za-z-]{0,3}\)"
    
    ############################    
    ######## TDS FORMAT ########
    ############################

    # TDS format includes CFR, Statutes-at-large, USC
    # matches formats like: "## USC" to "## U.S.C. ##-aa(#)(a), (b), and (d)" and patterns between
    title_doc_sec = "({}\s*{}(\s*([Pp]arts?\s*|§\s*|[Ss]ections?)?({})?(\s*{}(?!(\s*{})))*,?\s*(\s*(and|or)\s*)?)+)".format(init_digit, docTypes, sections, paren, docTypes)   
    tds_match = re.compile(title_doc_sec)
    # reflist contains the actual references which must be processed further. 
    title_doc_sec_reflist = [tuple(reference.groups())[0].strip().strip(",") for reference in tds_match.finditer(context)]
    
    for tds in title_doc_sec_reflist:
        context = tds
        tds = tds.replace(" (","(").replace(",(", ", (").replace("and", "").replace("or", "").replace(" et seq", "_et_seq").replace("App. ", "App._").replace(",","")
        for u in create_url(srcUrl, tds):
            urlItems.append(u)
            original_citation_text_list.append(context)
        
    ################################################    
    ######## "...of (this) Title..." FORMAT ########
    ################################################

    # "of Title" format includes anything including "... of Title #" in the string
    # matches formats like: "chapter ##, part #, sections ### and ### of title #"
    of_title = "((([Ss]ub\-?)?([Cc]hapters?|[Pp]aragraphs?|[Pp]arts?|[Ss]ections?)\s?(\(?[A-Z()a-z0-9.-]+\)?(,?\s?(or|and|to|through)\s?)?){0,4},?\s?(of)?\s?)?(([Tt]itle [0-9]{1,6})|(this [Tt]itle))((,|of the)?\s?(United\s?States\s?Code)|(Code\s?of\s?Federal\s?Regulations)|(U\.?S\.?C\.?)|(C\.?F\.?R\.?))?)"
    #of_title = "((([Ss]ub\-?)?([Cc]hapters?|[Pp]aragraphs?|[Pp]arts?|[Ss]ections?)(\s?\(?[A-Z()a-z0-9.-]+\)?(,?\s?(or|and|to|through)\s?)?){0,6},?\s?(of)?\s?)?(([Tt]itle [0-9]{1,6})|(this [Tt]itle))((,|of the)?\s?(United\s?States\s?Code)|(Code\s?of\s?Federal\s?Regulations)|(U\.?S\.?C\.?)|(C\.?F\.?R\.?))?)"
    #of_title = "((([Ss]ub\-?)?([Cc]hapters?|[Pp]aragraphs?|[Pp]arts?|[Ss]ections?)\s*(\(?[A-Z()a-z0-9-]+\)?(\s*(or|and|to|through)\s*)?)*,?\s*(of)?\s*)?(([Tt]itle \d+)|(this [Tt]itle)))"#(,?\s*(United\s*States\s*Code)|(Code\s*of\s*Federal\s*Regulations)|(U\.?S\.?C\.?)|(C\.?F\.?R\.?))?)"
    ot_match = re.compile(of_title)
    ot_reflist = [tuple(reference.groups())[0].strip().strip(",") for reference in ot_match.finditer(context)]
    for ot in ot_reflist:
        for u in create_url(srcUrl, ot):
            urlItems.append(u)
            original_citation_text_list.append(ot)

    if len(urlItems) > 0:
        #print(srcUrl, urlItems)
        urlDict = zip(urlItems, original_citation_text_list)
        #print("UD", [x for x in urlDict])
        #print("URLDICT", urlDict)
        return urlDict
    else:
        return None

def get_tgt_title(url):
    urlGrp = url.split("/")
    if urlGrp[2] == "pl":
        try:
            tgtTitle = "Public Law {}-{}, {}".format(urlGrp[3], urlGrp[4] if len(urlGrp) >= 5 else "", urlGrp[5] if len(urlGrp) >= 6 else "").rstrip(", ").strip().strip("-")
            tgtTitle = tgtTitle
        except:
            tgtTitle = "ERROR"
    else:
        try:
            tgtTitle = "{} {} {}".format(urlGrp[3], urlGrp[2].upper(), urlGrp[4] if len(urlGrp) >= 5 else "").strip()
        except:
            tgtTitle = "ERROR"
    return tgtTitle
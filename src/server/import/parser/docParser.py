# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:39:35 2015

@author: smichel

# NOTE: notes refer to an older data set. Specific examples may not relate to the latest datafiles (which were released in March 2016, at time this note was written.)

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

import docInfo # Packaged library
from bs4 import BeautifulSoup as Soup # XML-parsing tool
import os 

class parser():

    def __init__(self, fp=None, db=None):
        ''' When parser() class object is called, the filepath is attached to it so additional functions can be performed without the user repeatedly inputting the filepath.'''
        self.fp = fp
        self.db = db
        if os.path.isdir(self.fp):
            print("Input appears to be a directory. It will be searched for XML files.")
            tmpfp = []
            for (filepath,dirs,files) in os.walk(self.fp):
                if not dirs:
                    for f in files:
                        if not filepath.endswith("/"):
                            path = "{}/{}".format(filepath, f)
                        else:
                            path = "{}{}".format(filepath, f)
                        tmpfp.append(path)
            self.fp = tmpfp
            
        elif os.path.isfile(self.fp):
            self.fp = [fp]
    
        else:
            print("Could not identify directory or file. Please check that input is correct and there are no typos.")
        
        if db == None:
            print("Database not supplied. Please set a database class object and pass the object to this class. It will be used to store all parsed data.")
        
    def extractSections(self):
        from unidecode import unidecode
        import docUtility as utility
        from dateutil.parser import parse as dateparse

        for f in self.fp:
            print("Locating section numbers from the file: {}".format(f))

            soup = Soup(open(f, "rb").read())
            srcDocType, docNumTag, urlTag, urlAttr, sectionTag, secNumTag, secValueTag, headingTag, headingAltTag, contextTags, citationTag, noteTag, verTag, originalDateTag, verDateTag = docInfo.get(soup)
            dataLists = {}

            source_ver = soup.find(verTag).text if verTag != "" and soup.find(verTag) else None
            original_date = soup.find(originalDateTag).text.split("of ")[-1].strip(", annual") if originalDateTag != "" and soup.find(originalDateTag) != None else None
            verDate = soup.find(verDateTag).text.lower().split("of ")[-1] if verDateTag != "" and soup.find(verDateTag) else None
            
            for section in soup.findAll(sectionTag):
                parents = [x.name for x in section.parents]
                if noteTag not in parents:                    
                    sec = '' # errors in XML creation can create broken section number tags, resulting in absent or white-spaced section numbers. So we use an empty string as default (instead of None) and see if the found string returns to it after being stripped of whitespace. We hope not.
                    try:
                        sec = section.find(secNumTag)
                        sec = "§ {}".format(unidecode(sec[secValueTag]))
                    except:
                        try:
                            sec = unidecode(section.find(secNumTag).text).replace("SS", "§").strip(" ").strip(".").split(" ")[-1]#.replace("Sec. ", "")
                            sec = sec.strip()
                        except:
                            pass
                    # slightly intimidating, but this block just ensures a unique dictionary for each section. In docDatabase.database.insertNodes() function, each section is pushed to database and THEN it's committed. This kind of chunking improves speed. 
                    if sec.strip() != '':
                        dataLists[sec] = {}
                        if section.find(headingTag):
                            dataLists[sec]["heading"] = "{} {}".format(sec, unidecode(section.find(headingTag).text).replace("  ", " "))
                        else:
                            dataLists[sec]["heading"] = "{} {}".format(sec, unidecode(section.find(headingAltTag).text).replace("  ", " "))
                        dataLists[sec]["url"] = "/us/{}/{}/{}".format(srcDocType, ''.join([x for x in unidecode(soup.find(docNumTag).text.strip("§")).split(" ") if x[0].isdigit()]), ' '.join([x for x in unidecode(section.find(secNumTag).text.strip().replace(" to ", "_to_")).replace(", ", "_to_").strip(".").replace("  ", " ").split(" ") if x[0].isdigit()]).strip(" "))
                        dataLists[sec]["node"] = "{} {} {}".format(dataLists[sec]["url"].split("/")[3], dataLists[sec]["url"].split("/")[2].upper(), dataLists[sec]["url"].split("/")[4])
                        dataLists[sec]["doctype"] = dataLists[sec]["url"].split("/")[2]
                        dataLists[sec]["xml"] = str(section)
                        dataLists[sec]["text"] = section.text
                        dataLists[sec]["l1"] = dataLists[sec]["url"].split("/")[2] if dataLists[sec]["url"].count("/") >= 2 else None
                        dataLists[sec]["l2"] = dataLists[sec]["url"].split("/")[3] if dataLists[sec]["url"].count("/") >= 3 else None
                        dataLists[sec]["l3"] = dataLists[sec]["url"].split("/")[4] if dataLists[sec]["url"].count("/") >= 4 else None
                        dataLists[sec]["l4"] = dataLists[sec]["url"].split("/")[5] if dataLists[sec]["url"].count("/") >= 5 else None    
                        dataLists[sec]["discovered_by"] = "SectionParse"
                        dataLists[sec]["source_ver"] = source_ver
                        dataLists[sec]["original_date"] = original_date
                        dataLists[sec]["ver_date"] = verDate
                        #dataLists[sec]["topics"] = extractTopics(section)

            utility.create_nodelists(dataLists, self.db) # node output occurs after the file's sections are all complete.

    def extractReferences(self, body=True, notes=False, citations=False, pretags=False, regex=True, customRegex=[], capture=["cfr", "usc"], outputs=["all"]):
        from unidecode import unidecode
        import docUtility as utility
        from dateutil.parser import parse as dateparse
        
        for f in self.fp:
            print("Locating references from the file: {}".format(f))

            soup = Soup(open(f, "rb").read())
            srcDocType, docNumTag, urlTag, urlAttr, sectionTag, secNumTag, secValueTag, headingTag, headingAltTag, contextTags, citationTag, noteTag, verTag, originalDateTag, verDateTag = docInfo.get(soup)            

            source_ver = soup.find(verTag).text if verTag != "" and soup.find(verTag) else None
            original_date = soup.find(originalDateTag).text.split("of ")[-1].strip(", annual") if originalDateTag != "" and soup.find(originalDateTag) != None else None
            verDate = soup.find(verDateTag).text.lower().split("of ")[-1] if verDateTag != "" and soup.find(verDateTag) else None

            for section in soup.findAll(sectionTag):        
    
                parentsList = [x.name for x in section.parents]
                if citationTag not in parentsList and noteTag not in parentsList:
                
                    data = {}
        
                    if unidecode(section.find(secNumTag).text) and unidecode(section.find(secNumTag).text).strip() != "":
                        #data["srcUrl"] = "/us/{}/{}/{}".format(srcDocType, ''.join([x for x in unidecode(soup.find(docNumTag).text.strip("§")).split(" ") if x[0].isdigit()]), ' '.join([x for x in unidecode(section.find(secNumTag).text.strip().replace(" to ", "_to_")).replace(", ", "_to_").strip(".").replace("  ", " ").split(" ") if x[0].isdigit()]).strip(" "))
                        data["srcUrl"] = "/us/{}/{}/{}".format(srcDocType, ''.join([x for x in unidecode(soup.find(docNumTag).text.strip("§").strip()).split(" ") if x[0].strip().isdigit()]), ' '.join([x for x in unidecode(section.find(secNumTag).text.strip().replace(" to ", "_to_")).replace(", ", "_to_").strip(".").replace("  ", " ").split(" ") if x[0].strip().isdigit()]).strip(" "))
            
                        try:
                            sec = section.find(secNumTag)
                            sec = "§ {}".format(unidecode(sec[secValueTag]))
                        except:
                            sec = unidecode(section.find(secNumTag).text).replace("SS", "§").strip(" ").strip(".").split(" ")[-1]#.replace("Sec. ", "")
                            sec = sec.strip()
                        
                        #print(section.find(headingTag))
            
                        if section.find(headingTag):
                            data["srcHeading"] = "{} {}".format(sec, unidecode(section.find(headingTag).text).replace("  ", " "))
                        else:
                            try:
                                data["srcHeading"] = "{} {}".format(sec, unidecode(section.find(headingAltTag).text).replace("  ", " "))
                            except:
                                data["srcHeading"] = None
                        if data["srcHeading"] and "§" not in data["srcHeading"]:
                            data["srcHeading"] = "§ {}".format(data["srcHeading"])
                            
                        data["srcTitle"] = "{} {} {}".format(data["srcUrl"].split("/")[3], data["srcUrl"].split("/")[2].upper(), data["srcUrl"].split("/")[4])
                        data["srcDoctype"] = srcDocType
                        data["location"] = "In-text"
                        data["source_ver"] = source_ver
                        data["original_date"] = original_date
                        data["source_date"] = verDate
                        
                        # Basic functionality: look for references in the body of text  
                        if body:
                            for tag in contextTags:
                                context_list = section.findAll(tag)
                                
                                for text in context_list:
                                    parentsList = [x.name for x in text.parents]
                                    if citationTag not in parentsList and noteTag not in parentsList and not any(tag2 in parentsList for tag2 in contextTags):
                                        data["context"] = unidecode(''.join(t for t in text.find_all(text=True) if t.parent.name != "sup")).replace("  ", " ").replace("--", " -- ").replace("SS", "§").strip().replace("\n", "\\n").replace("\\n", "\\\\n") # do something with \n in the text, maybe?
                
                                        if pretags:
                                            urlList = text.findAll(urlTag)
    
                                            if urlList:
                                                for url in urlList:
                                                    try:
                                                        data["original_citation_text"] = unidecode(url.text)
                                                        utility.create_citation_datapoint(data, url, capture, self.db)
                                                    except:
                                                        pass
                                            
                                        if regex:
                                            urlList = utility.get_regex_matches(data["context"], data["srcUrl"], data["location"], customRegex)
                                            if urlList:                                                
                                                #print("THIS", [x for x in urlList])
                                                utility.create_citation_datapoint(data, urlList, capture, self.db)
                                                
                                                                
                        # Optional parameter: check for known specific notes citations section and extract its references
                        # This is functionally identical to the basic functionality, but uses citation tags instead of context tags
                        # THESE BEHAVIORS SHOULD CREATE AN EXTERNAL FUNCTION THAT IS CALLED BY THIS (xml_parse_new) FUNCTION!
                        if notes:
                            if srcDocType == "cfr":
                                data["location"] = "Authority"
                            else:
                                data["location"] = "Notes"
                            notes_list = section.findAll(noteTag)
                            
                            for note in notes_list:
                                data["context"] = unidecode(note.get_text()).replace("SS", "§") # do something with \n in the text, maybe?
            
                                if pretags:
                                    urlList = text.findAll(urlTag)

                                    if urlList:
                                        for url in urlList:
                                            try:
                                                data["original_citation_text"] = unidecode(url.text)
                                                utility.create_citation_datapoint(data, url, capture, self.db)
                                            except:
                                                pass
                            
                                if regex:
                                    urlList = utility.get_regex_matches(data["context"], data["srcUrl"], data["location"], customRegex)
                                    if urlList:
                                        utility.create_citation_datapoint(data, urlList, capture, self.db)
                        if citations:
                            data["location"] = "Citation"
                            citations_list = section.findAll(citationTag)
                            
                            for text in citations_list:
                                data["context"] = unidecode(text.get_text()).replace("SS", "§") # do something with \n in the text, maybe?
                                
                                if pretags:
                                    urlList = text.findAll(urlTag)

                                    if urlList:
                                        for url in urlList:
                                            try:
                                                data["original_citation_text"] = unidecode(url.text)
                                                utility.create_citation_datapoint(data, url, capture)
                                            except:
                                                pass
                            
                                if regex:
                                    urlList = utility.get_regex_matches(data["context"], data["srcUrl"], data["location"], customRegex)
                                    if urlList:
                                        utility.create_citation_datapoint(data, urlList, capture, self.db)
    def extractTopics(self, section):
        # do some HLT/NLP stuff here to begin topic extraction stuff
        # also add "topics" to the output databases
        pass
    
    def extractMetrics(self, db):
        import docUtility as utility
        import igraph

        # get a complete edgelist based on the data in the database        
        data = db.retrieveEdges()

        # make the nodelist; ensure nodes are uniquely identified
        nodeList = []
        set(nodeList.extend(d) for d in data)
        nodeList = list(set(nodeList))
        
        # instantiate a directed graph
        G = igraph.Graph(directed=True)        
        
        # add nodes (because we need to give non-built-in names), then add edges
        G.add_vertices(nodeList)
        G.add_edges(data)

        # compute node metrics
        G.vs["deg"] = G.degree() 
        G.vs["bc"] = G.betweenness(directed=True)
        G.vs["cc"] = G.closeness()
        G.vs["dc"] = G.density()
        G.vs["pr"] = G.pagerank()
        
        # compute edge metrics
        G.es["bc"] = G.edge_betweenness(directed=True)
      
        utility.create_node_metric(list([v.attributes() for v in G.vs]), db=self.db)
        #print(list([e for e in G.es]))
        #utility.create_edge_metric(list([e.attributes() for e in G.es]), db=self.db)
        
    def autoparse(self, createdb=False, getNodelist=False, getReferences=False, pretags=False, regex=True, customRegex = [], citations=False, notes=False, capture=["all"], outputs=["all"]):
        if createdb:
            from docDatabase import database
            try:
                database().run()
            except:
                print("Database failed to create. Please ensure:\n  1) you have postgres installed;\n  2) you have updated the configuration settings in docDatabase.py;\n  3) the database doesn't already exist.\n")
                import sys
                sys.exit()
            
        if not getNodelist and not getReferences:
            print("\nWARNING: You have not instructed the parser to identify nodelists or references. You must include one or all of the following arguments to your autoparse() call:\n  getSections=True\n  getReferences=True\n")
            import sys
            sys.exit()

        if not pretags and not regex:
            print("\nWARNING: You have not instructed the parser to use the pretags (explicitly-defined references) or regex (pattern matching) to identify references in the text. You must include one or all of the following arguments to your autoparse() call:\n  pretags=True\n  regex=True\n")
            import sys
            sys.exit()

        if getNodelist:
            self.extractSections()

        if getReferences:
            self.extractReferences(notes=notes, citations=citations, pretags=pretags, regex=regex, customRegex=customRegex, capture=capture, outputs=outputs)
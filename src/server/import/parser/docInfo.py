# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:39:35 2015

@author: smichel
"""

def get(soup, docType=None):

    other = False

    # CFR criteria
    if docType == "cfr" or soup.find("cfrdoc"):
        docType = "cfr"
        docNumTag = "titlenum"#soup.find("titlenum").text.replace("Title ", "")
        urlTag = ""
        urlAttr = ""
        sectionTag = "section"
        secNumTag = "sectno"
        secValueTag = ""
        headingTag = "subject"
        headingAltTag = "reserved"
        contextTags = ["p"]
        citationTag = "cita"
        noteTag = "auth"
        verTag = ""
        originalDateTag = "amddate"
        verDateTag = "date"

    # USC criteria
    elif docType == "usc" or soup.find("docnumber"):
        docType = "usc"
        docNumTag = "docnumber"
        urlTag = "ref"
        urlAttr = "href"
        sectionTag = "section"
        secNumTag = "num"
        secValueTag = "value"
        headingTag = "heading"
        headingAltTag = ""
        contextTags = ["chapeau", "clause", "content", "item", "p", "subclause", "subitem", "subparagraph", "subsection"]
        citationTag = "sourcecredit"
        noteTag = "note"
        verTag = "docpublicationname"
        originalDateTag = ""
        verDateTag = "dcterms:created"
        

    # HR criteria
    elif docType == "hr" or soup.find("legis-num"):
        docType = "hr"
        docNumTag = "legis-num"
        urlTag = "external-xref"
        urlAttr = "parsable-cite"
        sectionTag = "section"
        secNumTag = "enum"
        secValueTag = ""
        headingTag = ""
        headingAltTag = ""
        contextTags = ["text"]
        citationTag = ""
        noteTag = ""
        verTag = ""
        originalDateTag = ""
        verDateTag = "dc:date"
          
    # Public Law criteria
    elif docType == "pl" or soup.find("legis-num"):
        docType = "hr"
        docNumTag = "legis-num"
        urlTag = "external-xref"
        urlAttr = "parsable-cite"
        sectionTag = "section"
        secNumTag = "enum"
        secValueTag = ""
        headingTag = ""
        headingAltTag = ""
        contextTags = ["text"]
        citationTag = ""
        noteTag = ""
        verTag = ""
        originalDateTag = ""
        verDateTag = "dc:date"


    # Other criteria
    else:
        print("Unrecognized document type. Looking for available tags...")
        other == True

    if other == False:
        # use the following to produce the title number (docNum): [x for x in soup.find(docNumTag).text.split(" ") if x[0].isdigit()][0]
        return docType, docNumTag, urlTag, urlAttr, sectionTag, secNumTag, secValueTag, headingTag, headingAltTag, contextTags, citationTag, noteTag, verTag, originalDateTag, verDateTag
    else:
        try: 
            docTags = soup.tags
            print("The following tags exist in this document. You can manually specify which tags to use by passing the tags you want for each category (docType, docNumTag, sectionTag, contextTag, citationTag).")
            print(docTags)
			
        except:
            print("Cannot find any tags in this document. \nYou can try again by running this program with the flag RegEx=True.")
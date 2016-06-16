# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:39:35 2015

@author: smichel
"""

###############################
######### THE HOOD ############
###############################

import time

class pgDatabase():    
    def __init__(self, host, dbname, user, password, initial_dbname='postgres'):
        import psycopg2

        self.host = host
        self.desired_dbname = dbname
        self.user = user
        self.password = password
        self.initial_dbname = initial_dbname
        
        try: # try to connect to desired db. If fails, print a warning
            self.conn = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}'".format(self.host, self.desired_dbname, self.user, self.password))
            self.cur = self.conn.cursor()
        except:
            pass#print("WARNING: Please double-check input parameters are correct for database access. Perhaps try to create the database using autocreate()")
        
    def createDB(self, createDB):
        if createDB == True:
            import psycopg2
            # first connect to default database info to create a new database
            self.conntemp = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}'".format(self.host, self.initial_dbname, self.user, self.password))
            self.curtemp = self.conntemp.cursor()
            self.conntemp.autocommit = True
            
            # create the database
            self.curtemp.execute("""CREATE DATABASE {} WITH ENCODING 'UTF-8'""".format(self.desired_dbname))
            self.conntemp.close()
            
            # after closing the connection, reopen with new database
            self.conn = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}'".format(self.host, self.desired_dbname, self.user, self.password))
            self.cur = self.conn.cursor()
        
    def createTables(self, tables):
        #conn = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}'".format(host, desired_dbname, user, password))
        #cur = conn.cursor()
        #cur.execute("CREATE EXTENSION hstore;")

        if any(x in ["all", "nodes"] for x in tables):
            self.cur.execute("""CREATE TABLE nodes (
              id serial,
              node varchar PRIMARY KEY,
              heading varchar,
              url varchar,
              Doctype varchar,
              Text varchar,
              XML varchar,
              L1 varchar,
              L2 varchar,
              L3 varchar,
              L4 varchar,
              discovered_by varchar,
              source_ver varchar,
              original_date varchar,
              ver_date varchar
              );""")

        if any(x in ["all", "edges"] for x in tables):
            print("EDGE TABLE CREATED")
            self.cur.execute("""CREATE TABLE edges (
                id serial, 
                source varchar,
                Source_Heading varchar,
                target varchar,
                Source_url varchar,
                Target_url varchar,
                Target_url_broad varchar,
                Context varchar,
                Original_Citation_Text varchar,
                location varchar,
                Source_Doctype varchar,
                Target_Doctype varchar,
                source_ver varchar,
                original_date varchar, 
                source_date varchar
                ) WITH OIDS ;""")
                
        if any(x in ["all", "node_metrics"] for x in tables):
            self.cur.execute("""CREATE TABLE node_metrics (
              id serial,
              node varchar PRIMARY KEY,
              degree int,
              betweenness float,
              closeness float,
              pagerank float          
              );""")
        '''  
        self.cur.execute("""CREATE TABLE edge_metrics (
          id serial,
          source varchar,
          target int,
          betweenness float     
          );""")
        '''
        self.conn.commit()
    
    def insertNodes(self, dataLists):# node, heading, url, doctype, text, xml, l1, l2, l3, l4):
        #conn = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}'".format(host, desired_dbname, user, password))     
        #cur = conn.cursor()       

        for d in sorted(dataLists.keys(), key=lambda x_y: x_y):
            if dataLists[d]["original_date"] != None:
                dataLists[d]["original_date"] = dataLists[d]["original_date"]
            if dataLists[d]["ver_date"] != None:
                dataLists[d]["ver_date"] = dataLists[d]["ver_date"]
            self.cur.execute("SELECT node FROM nodes WHERE node = %s", (dataLists[d]["node"],))
            exists = self.cur.fetchone()
            if not exists:
                self.cur.execute("INSERT into nodes (node, heading, url, doctype, text, xml, l1, l2, l3, l4, discovered_by, source_ver, original_date, ver_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dataLists[d]["node"], dataLists[d]["heading"], dataLists[d]["url"], dataLists[d]["doctype"], dataLists[d]["text"], dataLists[d]["xml"], dataLists[d]["l1"], dataLists[d]["l2"], dataLists[d]["l3"], dataLists[d]["l4"], dataLists[d]["discovered_by"], dataLists[d]["source_ver"], dataLists[d]["original_date"], dataLists[d]["ver_date"]))#(node, heading, url, doctype, text, xml, l1, l2, l3, l4))
        self.conn.commit()

    def insertNodeMetric(self, dataLists):
        for d in sorted(dataLists, key=lambda k: k["name"]):
            self.cur.execute("INSERT into node_metrics (node, degree, betweenness, closeness, pagerank) VALUES (%s, %s, %s, %s, %s)", (d["name"], d["deg"], d["bc"], d["cc"], d["pr"]))
        self.conn.commit()  

    def insertEdgeMetric(self, dataLists):
        ''' DOES NOT CURRENTLY WORK '''
        for d in dataLists:
            self.cur.execute("INSERT into edge_metrics (source, target, betweenness) VALUES (%s, %s, %s, %s, %s)", (d["source"], d["target"], d["betweenness"]))
        self.conn.commit()  

    def updateNodes(self):# node, heading, url, doctype, text, xml, l1, l2, l3, l4):

        # collect all source nodes and push info to nodes table if not exists
        dataList = None
        self.cur.execute("SELECT DISTINCT source, source_heading, source_url, source_doctype, location, source_ver, original_date, source_date FROM edges")
        dataList = set(self.cur.fetchall())

        if dataList:
            for d in dataList:
                self.cur.execute("SELECT node FROM nodes WHERE node = %s", (d[0],))
                exists = self.cur.fetchone()
                if not exists:
                    l1 = d[2].split("/")[2] if d[2].count("/") >= 2 else None
                    l2 = d[2].split("/")[3] if d[2].count("/") >= 3 else None
                    l3 = d[2].split("/")[4] if d[2].count("/") >= 4 else None
                    l4 = d[2].split("/")[5] if d[2].count("/") >= 5 else None

                    self.cur.execute("INSERT into nodes (node, heading, url, doctype, text, xml, l1, l2, l3, l4, discovered_by, source_ver, original_date, ver_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (d[0], d[1], d[2], d[3], None, None, l1, l2, l3, l4, d[4], d[5], d[6], d[7]))
            self.conn.commit()

        # collect all target nodes and repeat
        dataList = None
        self.cur.execute("SELECT DISTINCT target, target_url, target_doctype, location, source_ver, original_date, source_date FROM edges")
        dataList = set(self.cur.fetchall())

        if dataList:
            for d in dataList:
                self.cur.execute("SELECT node FROM nodes WHERE node = %s", (d[0],))
                exists = self.cur.fetchone()
                if not exists:
                    l1 = d[1].split("/")[2] if d[1].count("/") >= 2 else None
                    l2 = d[1].split("/")[3] if d[1].count("/") >= 3 else None
                    l3 = d[1].split("/")[4] if d[1].count("/") >= 4 else None
                    l4 = d[1].split("/")[5] if d[1].count("/") >= 5 else None

                    self.cur.execute("INSERT into nodes (node, heading, url, doctype, text, xml, l1, l2, l3, l4, discovered_by, source_ver, original_date, ver_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (d[0], None, d[1], d[2], None, None, l1, l2, l3, l4, d[3], d[4], d[5], d[6]))
            self.conn.commit()

    def checkNodeExists(self, node):
        #conn = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}'".format(host, desired_dbname, user, password))     
        #cur = conn.cursor() 
        self.cur.execute("SELECT node FROM nodes WHERE node = %s", (node,))
        exists = self.cur.fetchone()
        if not exists:
            return False
        else:
            return True

    def insertEdge(self, dataList):#srcTitle, srcHeading, tgtTitle, srcUrl, tgtUrl, tgtUrlBroad, context, original_citation_text, location, srcDoctype, tgtDoctype, source_ver, original_date, source_date):
        dataLists = {}
        dataLists["src"] = {"node":dataList["srcTitle"], "heading":dataList["srcHeading"], "url":dataList["srcUrl"], "doctype":dataList["srcDoctype"], "text":None, "xml":None, "l1":dataList["srcUrl"].split("/")[2] if dataList["srcUrl"].count("/") >= 2 else None, "l2":dataList["srcUrl"].split("/")[3] if dataList["srcUrl"].count("/") >= 3 else None, "l3":dataList["srcUrl"].split("/")[4] if dataList["srcUrl"].count("/") >= 4 else None, "l4":dataList["srcUrl"].split("/")[5] if dataList["srcUrl"].count("/") >= 5 else None, "discovered_by":dataList["location"], "source_ver":dataList["source_ver"], "original_date":dataList["original_date"], "source_date":dataList["source_date"]}
        for n in dataList["targets"]:
            self.cur.execute("INSERT into edges (source, source_heading, target, source_url, target_url, target_url_broad, context, original_citation_text, location, source_doctype, target_doctype, source_ver, original_date, source_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dataList["srcTitle"], dataList["srcHeading"], dataList["targets"][n]["tgtTitle"], dataList["srcUrl"], dataList["targets"][n]["tgtUrl"], dataList["targets"][n]["tgtUrlBroad"], dataList["context"], dataList["targets"][n]["original_citation_text"], dataList["location"], dataList["srcDoctype"], dataList["targets"][n]["tgtDoctype"], dataList["source_ver"], dataList["original_date"], dataList["source_date"]))
            dataLists[str(n)] = {"node":dataList["targets"][n]["tgtTitle"], "heading":None, "url":dataList["targets"][n]["tgtUrl"], "doctype":dataList["targets"][n]["tgtDoctype"], "text":None, "xml":None, "l1":dataList["targets"][n]["tgtUrl"].split("/")[2] if dataList["targets"][n]["tgtUrl"].count("/") >= 2 else None, "l2":dataList["targets"][n]["tgtUrl"].split("/")[3] if dataList["targets"][n]["tgtUrl"].count("/") >= 3 else None, "l3":dataList["targets"][n]["tgtUrl"].split("/")[4] if dataList["targets"][n]["tgtUrl"].count("/") >= 4 else None, "l4":dataList["targets"][n]["tgtUrl"].split("/")[5] if dataList["targets"][n]["tgtUrl"].count("/") >= 5 else None, "discovered_by":dataList["location"], "source_ver":dataList["source_ver"], "original_date":dataList["original_date"], "source_date":dataList["source_date"]}
            
        self.conn.commit()

    def retrieveEdges(self, node=None, fuzzy=False):
        if node == None:
            self.cur.execute("""SELECT source, target FROM edges""")
            data = self.cur.fetchall()

            return data

        else:
            if fuzzy==True:
                node = '%{}%'.format(node)
            data = []
            self.cur.execute("""SELECT source, target FROM edges WHERE source LIKE %s""", (node,))
            data.extend(self.cur.fetchall())
            self.cur.execute("""SELECT source, target FROM edges WHERE target LIKE %s""", (node,))
            data.extend(self.cur.fetchall())
            return data

        
    def autocreate(self, createDB=True, tables=["all"]):
        print("Creating Database")
        t_start = time.time()        

        self.createDB(createDB)
        print("Creating Tables")
        self.createTables(tables)

        print("Done! Elapsed time was {} minutes\n".format((time.time() - t_start)/60))
            
class mongoDatabase():
    def __init__(self, host, desired_dbname, user, password):
        import pymongo
        self.desired_dbname = desired_dbname
        #self.client = pymongo.MongoClient("mongodb://{}:27017".format(host))
        self.client = pymongo.MongoClient("mongodb://{}:{}@{}/{}".format(user, password, host, desired_dbname))

    def createDB(self):
        print("bada bing, bada boom")
        
    def createTables(self):
        self.client[self.desired_dbname].create_collection("nodes")
        self.client[self.desired_dbname]["nodes"].create_index("node", unique=True)
        
        self.client[self.desired_dbname].create_collection("edges")
        
        self.client[self.desired_dbname].create_collection("node_metrics")
        self.client[self.desired_dbname]["node_metrics"].create_index("node", unique=True)
        
        #self.client[self.desired_dbname].create_collection("edge_metrics")
    
    def insertNodes(self, dataLists):# node, heading, url, doctype, text, xml, l1, l2, l3, l4):
        try:
            self.client[self.desired_dbname]["nodes"].insert_many(dataLists.values)
        except:
            pass
    
    def insertNodeMetric(self, dataLists):
        for d in dataLists:
            self.client[self.desired_dbname]["node_metrics"].insert_many(d)

    def insertEdgeMetric(self, dataLists):
        ''' DOES NOT CURRENTLY WORK '''
        for d in dataLists:
            self.client[self.desired_dbname]["edge_metrics"].insert_many(d)
    
    def checkNodeExists(self, node):
        return not not self.client[self.desired_dbname]["nodes"].find({"node": node}).limit(1)

    def updateNodes(self):
        '''Checks each record's "source" and "target" nodes to see if they exist in the "nodes" collection. 
        Any "source" or "target" that does not exist in the "nodes" collection must be added to it.
        It must also contain the appropriate heading, url, doctype, location, source_ver, original_date, and ver_date values. 
        e.g.    source nodes will use: src_heading, srcUrl, srcDoctype, location, source_ver, original_date, and ver_date values
                target nodes will use: None, tgtUrl, tgtDoctype, location, source_ver, original_date, and ver_date values'''        
        
        # collect all source nodes and push info to nodes table if not exists
        dataList = None
        data = self.client[self.desired_dbname]["edges"].distinct("source")
        dataList = list()

        if dataList:
            for d in dataList:
                exists = not not self.client[self.desired_dbname]["nodes"].find({"node": d["source"]}).limit(1)
                print(exists)
                if not exists:
                    d["l1"] = d[2].split("/")[2] if d[2].count("/") >= 2 else None
                    d["l2"] = d[2].split("/")[3] if d[2].count("/") >= 3 else None
                    d["l3"] = d[2].split("/")[4] if d[2].count("/") >= 4 else None
                    d["l4"] = d[2].split("/")[5] if d[2].count("/") >= 5 else None

                    self.client[self.desired_dbname]["nodes"].insert_one(d.values)

        # collect all target nodes and repeat
        dataList = None

    def insertEdge(self, dataList):#srcTitle, srcHeading, tgtTitle, srcUrl, tgtUrl, tgtUrlBroad, context, original_citation_text, location, srcDoctype, tgtDoctype, source_ver, original_date, source_date):

        dataList["src"] = {"node":dataList["srcTitle"], "heading":dataList["srcHeading"], "url":dataList["srcUrl"], "doctype":dataList["srcDoctype"], "text":None, "xml":None, "l1":dataList["srcUrl"].split("/")[2] if dataList["srcUrl"].count("/") >= 2 else None, "l2":dataList["srcUrl"].split("/")[3] if dataList["srcUrl"].count("/") >= 3 else None, "l3":dataList["srcUrl"].split("/")[4] if dataList["srcUrl"].count("/") >= 4 else None, "l4":dataList["srcUrl"].split("/")[5] if dataList["srcUrl"].count("/") >= 5 else None, "discovered_by":dataList["location"], "source_ver":dataList["source_ver"], "original_date":dataList["original_date"], "source_date":dataList["source_date"]}
        edges = []
        for n in dataList["targets"]:
            edges.append({
                "source": dataList["srcTitle"],
                "source_heading": dataList["srcHeading"],
                "target": dataList["targets"][n]["tgtTitle"],
                "source_url": dataList["srcUrl"],
                "target_url": dataList["targets"][n]["tgtUrl"],
                "target_url_broad": dataList["targets"][n]["tgtUrlBroad"],
                "context": dataList["context"],
                "original_citation_text": dataList["targets"][n]["original_citation_text"],
                "location": dataList["location"],
                "source_doctype": dataList["srcDoctype"],
                "target_doctype": dataList["targets"][n]["tgtDoctype"],
                "source_ver": dataList["source_ver"],
                "original_date": dataList["original_date"],
                "source_date": dataList["source_date"],
                })
            dataList[str(n)] = {"node":dataList["targets"][n]["tgtTitle"], "heading":None, "url":dataList["targets"][n]["tgtUrl"], "doctype":dataList["targets"][n]["tgtDoctype"], "text":None, "xml":None, "l1":dataList["targets"][n]["tgtUrl"].split("/")[2] if dataList["targets"][n]["tgtUrl"].count("/") >= 2 else None, "l2":dataList["targets"][n]["tgtUrl"].split("/")[3] if dataList["targets"][n]["tgtUrl"].count("/") >= 3 else None, "l3":dataList["targets"][n]["tgtUrl"].split("/")[4] if dataList["targets"][n]["tgtUrl"].count("/") >= 4 else None, "l4":dataList["targets"][n]["tgtUrl"].split("/")[5] if dataList["targets"][n]["tgtUrl"].count("/") >= 5 else None, "discovered_by":dataList["location"], "source_ver":dataList["source_ver"], "original_date":dataList["original_date"], "source_date":dataList["source_date"]}

        self.client[self.desired_dbname]["edges"].insert_many(edges)
        self.insertNodes(dataList)

    def testGrab(self):
        print(self.client[self.desired_dbname]["nodes"].find_one({}))
        
    def autocreate(self):
        print("Creating Database")
        t_start = time.time()        

        self.createDB()
        print("Creating Tables")
        self.createTables()
        
        print("Done! Elapsed time was {} minutes\n".format((time.time() - t_start)/60))
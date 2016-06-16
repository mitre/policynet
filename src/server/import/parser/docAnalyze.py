# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 11:08:22 2015

@author: SMICHEL
"""

### Set desired document analysis here. Input a list of items to get more than one. 

docTypes = ["cfr", "usc"]

def getEdges(docTypes):
    import csv
    csv.field_size_limit(2147483647)
    for docType in docTypes:
        print(docType)
        with open("../output/edgelists/{}-edgelist.csv".format(docType.lower()), "r") as csvfile:
            datareader = csv.reader(csvfile)
            count = 0
            for row in datareader:
                if row[9].lower() in docTypes:
                    yield (row[0], row[2])
                    count += 1
                elif count < 2:
                    continue
                else:
                    return

def makeGraph(fp, edgeList):
    import igraph
    g = igraph.Graph(directed = True)
    #g = igraph.Graph.as_directed(g)

    for edge in edgeList:
        #print(edge)
        for node in edge:
            try:
                g.vs.find(node)
            except:
                g.add_vertex(node)
            #print("   ", node)

    print("Adding edges")
    g.add_edges(edgeList)

    igraph.Graph.write_pickle(g, fname=fp)    

    print(g.summary())

def getGraph(fp):
    import igraph
    g = igraph.Graph.Read_Pickle(fp)
    g = g.simplify(multiple=True)
    #g = igraph.Graph.as_undirected(g)
    #g = igraph.Graph.as_directed(g)
    print(g.summary())
    #print(g.get_edgelist())

#edgeList = list(getEdges(docTypes))

#makeGraph(fp="../data/graphs/cfr_usc.pickle", edgeList=edgeList)

#getGraph(fp="../data/graphs/cfr.pickle")

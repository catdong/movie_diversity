"""
FILE: GraphExample.py
----------------------
An example of how to use the MovieGraph NetworkX graph and accompanying
graphDict.

graphDict is a dictionary from actor, director and movie names to node IDs in
the NetworkX graph.  keys for actors and directors are just their names (i.e.
"James Cameron" or "Tom Hanks") while keys for movies are the concatenation of
their title AND release year (i.e. "Avatar2009").  This is so that movie remakes
can have unique keys.

The graph is a tripartite NetworkX graph where each node represents either a
movie, actor, director or actor-director.  Each node has an accompanying
"type" field which is either "ACTOR", "DIRECTOR", "ACTOR-DIRECTOR" or "MOVIE".

Each node also has metadata fields which contain additional information.

Each person node has a "name", "gender" and "race" field.

Each movie has a variety of fields such as "title", "gross", and others.  See
ReadMovieGraph.py for a complete list.
----------------------
"""

import ReadMovieGraph


graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()

# Print out graph information (see NetworkX documentation for more)
print "%i nodes" % graph.number_of_nodes()
print "%i edges" % graph.number_of_edges()

# Find node IDs for movies, actors and directors in graphDict
avatarNodeId = graphDict["Avatar2009"]
tomNodeId = graphDict["Tom Hanks"]
stevenNodeId = graphDict["Steven Spielberg"]
oliviaNodeId = graphDict["Olivia Munn"]

print "Avatar (2009) is node %i" % avatarNodeId
print "Tom Hanks is node %i" % tomNodeId
print "Steven Spielberg is node %i" % stevenNodeId
print "Olivia Munn is node %i" % oliviaNodeId
print "\n\n"

# Find the type of a node (MOVIE, ACTOR, ACTOR-DIRECTOR or DIRECTOR)
print "Avatar is a %s" % graph.node[avatarNodeId]["type"]
print "Tom Hanks is an %s" % graph.node[tomNodeId]["type"]
print "Steven Spielberg is a %s" % graph.node[stevenNodeId]["type"]
print  "Olivia Munn is an %s" % graph.node[oliviaNodeId]["type"]
print "\n\n"

# Get metadata from a node
print "%s made $%.2f" % (graph.node[avatarNodeId]["title"],
	graph.node[avatarNodeId]["gross"])

print "%s is a %s %s" % (graph.node[tomNodeId]["name"],
	graph.node[tomNodeId]["race"], graph.node[tomNodeId]["gender"])

print "%s is a %s %s" % (graph.node[stevenNodeId]["name"],
	graph.node[stevenNodeId]["race"], graph.node[stevenNodeId]["gender"])

print "%s is a %s %s" % (graph.node[oliviaNodeId]["name"],
	graph.node[oliviaNodeId]["race"], graph.node[oliviaNodeId]["gender"])
print "\n\n"

# Get a node's edges
tomActorMovies = []
tomDirectorMovies = []
for i in graph.neighbors(tomNodeId):
	if graph.node[i]["directorName"] == "Tom Hanks":
		tomDirectorMovies.append(graph.node[i]["title"])
	if "Tom Hanks" in graph.node[i]["actorNames"]:
		tomActorMovies.append(graph.node[i]["title"])
print "Tom Hanks was an actor in: %s" % tomActorMovies
print "Tom Hanks directed: %s" % tomDirectorMovies

oliviaMovies = []
for i in graph.neighbors(oliviaNodeId):
	oliviaMovies.append(graph.node[i]["title"])
print "Olivia Munn was an actor in: %s" % oliviaMovies




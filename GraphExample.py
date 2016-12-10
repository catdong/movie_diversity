"""
FILE: GraphExample.py
----------------------
An example of how to use the MovieGraph NetworkX graph and accompanying
graphDict, as well as how to calculate diversity scores.

graphDict is a dictionary from actor, director and movie names to node IDs in
the NetworkX graph.  keys for actors and directors are just their names (i.e.
"James Cameron" or "Tom Hanks") while keys for movies are the concatenation of
their title AND release year (i.e. "Avatar2009").  This is so that movie remakes
can have unique keys.

The graph is a tripartite NetworkX directed graph where each node represents
either a movie, actor, director, or actor-director.  Each node has an
accompanying "type" field which is either "ACTOR", "DIRECTOR", "ACTOR-DIRECTOR"
or "MOVIE".

Each node also has metadata fields which contain additional information.

Each person node has a "name", "gender" and "race" field.

Each movie has a variety of fields such as "title", "gross", and others.  See
ReadMovieGraph.py for a complete list.

Edges go from directors to movies and from movies to actors.  Therefore, for
actor-directors, there are two edges going to-from the person and their movie.
----------------------
"""
import DiversityScore
from dataset import ReadMovieGraph


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
# Also calculate their diversity scores
print "Avatar is a %s" % graph.node[avatarNodeId]["type"]
print "Diversity score: %f" % DiversityScore.scoreForMovie(graph, avatarNodeId)
print "Tom Hanks is an %s" % graph.node[tomNodeId]["type"]
print "Diversity score: %f" % DiversityScore.scoreForDirector(graph, tomNodeId)
print "Steven Spielberg is a %s" % graph.node[stevenNodeId]["type"]
print "Diversity score: %f" % DiversityScore.scoreForDirector(graph,
															stevenNodeId)
print  "Olivia Munn is an %s" % graph.node[oliviaNodeId]["type"]
print "Div. score: %f" % DiversityScore.scoreForActor(graph.node[oliviaNodeId])
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
# predecessors are nodes with edges TO a given node.  successors are nodes with
# edges FROM a given node.
tomActorMovies = [graph.node[i]["title"] for i in graph.predecessors(tomNodeId)]
tomDirMovies = [graph.node[i]["title"] for i in graph.successors(tomNodeId)]
print "Tom Hanks was an actor in: %s" % tomActorMovies
print "Tom Hanks directed: %s" % tomDirMovies

OlivMovies = [graph.node[i]["title"] for i in graph.predecessors(oliviaNodeId)]
print "Olivia Munn was an actor in: %s" % OlivMovies




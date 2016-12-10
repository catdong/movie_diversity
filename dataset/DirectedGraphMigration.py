from GraphConstants import NodeTypeActor, NodeTypeDirector, NodeTypeMovie
from GraphConstants import NodeTypeActorDirector, datasetFilename
from GraphConstants import graphFilename, graphDictFilename
import networkx as nx
import ReadMovieGraph

# This migration script converts the undirected movie graph to a directed graph
# where edges go from directors to movies and from movies to actors.

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()

directedGraph = nx.DiGraph()

# Copy over all nodes and metadata
directedGraph.add_nodes_from(graph)
for nodeId in graph.nodes():
	directedGraph.node[nodeId] = graph.node[nodeId]

# Iterate over each edge and add its directed equivalent(s) to our new DiGraph
for (node1, node2) in graph.edges():

	# Every edge has one endpoint on a movie (movie-actor or movie-director)
	movieNode = node1 if graph.node[node1]["type"] == NodeTypeMovie else node2
	nonMovieNode = node2 if movieNode == node1 else node1

	# Movie-actor edges should go FROM movie TO actor.  Movie-director edges
	# should go FROM director TO movie.  For ActorDirectors, we need to make TWO
	# edges; one FROM the person TO the movie, and one FROM the movie TO the
	# person.
	if graph.node[nonMovieNode]["type"] == NodeTypeActor:
		directedGraph.add_edge(movieNode, nonMovieNode)
	elif graph.node[nonMovieNode]["type"] == NodeTypeDirector:
		directedGraph.add_edge(nonMovieNode, movieNode)
	elif graph.node[nonMovieNode]["type"] == NodeTypeActorDirector:
		directedGraph.add_edge(nonMovieNode, movieNode)
		directedGraph.add_edge(movieNode, nonMovieNode)
	else:
		print("Error: unknown type %s" % graph.node[nonMovieNode]["type"])

nx.write_gpickle(directedGraph, graphFilename)
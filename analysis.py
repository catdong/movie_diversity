import networkx as nx
import itertools
import ReadMovieGraph
from networkx.algorithms import bipartite

def createActorActorGraph(graph, graphDict):
	aaGraph = nx.MultiGraph()
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	for mId in movieIds:
		movie = graph.node[mId]
		actorIds = [graphDict[actorName] for actorName in movie['actorNames']]
		for aId in actorIds:
			if aId not in aaGraph:
				aaGraph.add_node(aId, graph.node[aId])
		for actorId1, actorId2 in itertools.combinations(actorIds, 2):
			aaGraph.add_edge(actorId1, actorId2)
	return aaGraph

def createNullActorActorGraph(nullModel):
	aaGraph = nx.MultiGraph()
	movieIds = [nId for nId in nullModel if nullModel.node[nId]['type'] == 'MOVIE']
	for mId in movieIds:
		actorIds = nullModel.neighbors(mId)
		for aId in actorIds:
			if aId not in aaGraph:
				aaGraph.add_node(aId, nullModel.node[aId])
		for actorId1, actorId2 in itertools.combinations(actorIds, 2):
			aaGraph.add_edge(actorId1, actorId2)
	return aaGraph

def createActorActorGraph(graph):
	aaGraph = nx.MultiGraph()
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	for mid in movieIds:
		actorIds = graph.neighbors(mId)

def nullModel1(graph): 
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	movieDegrees = {mId: graph.degree(mId) - 1 for mId in movieIds}  # minus 1 for director
	actorIds = [nId for nId in graph if graph.node[nId]['type'] == 'ACTOR']
	actorDegrees = {aId: graph.degree(aId) for aId in actorIds}
	actorDirectorIds = [nId for nId in graph if graph.node[nId]['type'] == 'ACTOR-DIRECTOR']
	for adId in actorDirectorIds:
		actorDegrees[adId] = 0
		adMovieIds = graph.neighbors(adId)
		for movieId in adMovieIds:
			if graph.node[movieId]['directorName'] != graph.node[adId]['name']:
				actorDegrees[adId] += 1
	allActorIds = actorIds + actorDirectorIds
	actorDegrees = [v for k, v in actorDegrees.iteritems()]
	movieDegrees = [v for k, v in movieDegrees.iteritems()]
	nullModel = bipartite.configuration_model(movieDegrees, actorDegrees, create_using=nx.Graph())

	zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]

	for i in xrange(len(movieIds)):
		nullModel.node[zeroIds[i]].update(graph.node[movieIds[i]])
	for i in xrange(len(allActorIds)):
		nullModel.node[oneIds[i]].update(graph.node[allActorIds[i]])

	return nullModel

def assortativity(actorActorGraph, attribute, nodeSet=None):
	return nx.attribute_assortativity_coefficient(actorActorGraph, attribute, nodeSet)

def getValidNodes(graph, attribute):
	return [n for n in graph if graph.node[n]['type'] != 'DIRECTOR' and graph.node[n][attribute] is not None]

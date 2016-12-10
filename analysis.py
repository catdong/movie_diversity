import networkx as nx
import itertools
import ReadMovieGraph
from networkx.algorithms import bipartite
from random import shuffle
import community

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

# use when directed graph is implemented
# def createActorActorGraph(graph):
# 	aaGraph = nx.MultiGraph()
# 	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
# 	for mid in movieIds:
# 		actorIds = graph.successors(mId)
# 		for aId in actorIds:
# 			if aId not in aaGraph:
# 				aaGraph.add_node(aId, graph.node[aId])
# 		for actorId1, actorId2 in itertools.combinations(actorIds, 2):
# 			aaGraph.add_edge(actorId1, actorId2)
# 	return aaGraph


def movieActorNullModel(graph):  # aka null model 1
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
	actorIds += actorDirectorIds
	actorDegrees = [v for k, v in actorDegrees.iteritems()]
	movieDegrees = [v for k, v in movieDegrees.iteritems()]
	nullModel = bipartite.configuration_model(movieDegrees, actorDegrees, create_using=nx.Graph())

	zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]

	shuffle(movieIds)
	shuffle(actorIds)
	for i in xrange(len(movieIds)):
		nullModel.node[zeroIds[i]].update(graph.node[movieIds[i]])
	for i in xrange(len(actorIds)):
		nullModel.node[oneIds[i]].update(graph.node[actorIds[i]])

	return nullModel

def directorMovieNullModel(graph):
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	directorIds = [nId for nId in graph if graph.node[nId]['type'] == 'DIRECTOR']
	directorDegrees = {dId: graph.degree(dId) for dId in directorIds}
	actorDirectorIds = [nId for nId in graph if graph.node[nId]['type'] == 'ACTOR-DIRECTOR']
	for adId in actorDirectorIds:
		directorDegrees[adId] = 0
		adMovieIds = graph.neighbors(adId)
		for movieId in adMovieIds:
			if graph.node[movieId]['directorName'] == graph.node[adId]['name']:
				directorDegrees[adId] += 1
	directorIds += actorDirectorIds
	directorDegrees = [v for k, v in directorDegrees.iteritems()]
	movieDegrees = [1 for mId in movieIds]
	nullModel = bipartite.configuration_model(directorDegrees, movieDegrees, create_using=nx.Graph())
	zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]

	shuffle(directorIds)
	shuffle(movieIds)
	for i in xrange(len(directorIds)):
		nullModel.node[zeroIds[i]].update(graph.node[directorIds[i]])
	for i in xrange(len(movieIds)):
		nullModel.node[oneIds[i]].update(graph.node[movieIds[i]])

	return nullModel

def modularity(actorActorGraph):
	racePartition = {}
	blackWhitePartition = {}
	raceToInt = {
		'White': 0
		'Black': 1
		'Hispanic': 2
		'Multiracial': 3
		'Asian': 4
		'Asian/Indian': 5
		'Middle Eastern': 6
		'American Aborigine': 7
	}
	for nId in actorActorGraph():
		actorRace = actorActorGraph.node[nId]['race']
		if actorRace in raceToInt:
			racePartition[nId] = raceToInt[actorRace]
			blackWhitePartition[nId] = 0 if raceToInt[actorRace] == 0 else 1
		else:
			actorActorGraph.remove_node(nId)
	raceModularity = community.modularity(racePartition, actorActorGraph)
	blackWhiteModularity = community.modularity(blackWhitePartition, actorActorGraph)
	return raceModularity, blackWhiteModularity

def assortativity(actorActorGraph, attribute, nodeSet=None):
	return nx.attribute_assortativity_coefficient(actorActorGraph, attribute, nodeSet)

def getValidNodes(graph, attribute):
	return [n for n in graph if graph.node[n]['type'] != 'DIRECTOR' and graph.node[n][attribute] is not None]

import networkx as nx
import itertools
from dataset import ReadMovieGraph
from networkx.algorithms import bipartite
from random import shuffle
import community


def multiToWeightedGraph(multiGraph):
	weightedGraph = nx.Graph()
	for u, v in multiGraph.edges():
		if (u, v) not in weightedGraph.edges():
			weightedGraph.add_edge(u, v, weight=0)
		weightedGraph.edge[u][v]['weight'] += 1
	return weightedGraph

def getGraphWithoutNones(graph, attribute):
	graph = graph.copy()
	for nId in graph.nodes():
		if graph.node[nId]['type'] != 'MOVIE' and graph.node[nId][attribute] is None:
			graph.remove_node(nId)
	return graph

def getBlackWhiteGraph(graph):
	graph = graph.copy()
	for nId in graph.nodes():
		if graph.node[nId]['type'] != 'MOVIE':
			if graph.node[nId]['race'] is None:
				graph.remove_node(nId)
			else:
				race = graph.node[nId]['race']
				graph.node[nId]['race'] = 'White' if race == 'White' else 'Non-White'
	return graph


def actorActorGraph(graph):
	aaGraph = nx.MultiGraph()
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	for mId in movieIds:
		actorIds = graph.successors(mId)
		for aId in actorIds:
			if aId not in aaGraph:
				aaGraph.add_node(aId, graph.node[aId])
		for actorId1, actorId2 in itertools.combinations(actorIds, 2):
			aaGraph.add_edge(actorId1, actorId2)
	return aaGraph

def movieActorNullModel(graph):  # aka null model 1
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	movieDegrees = [graph.out_degree(mId) for mId in movieIds]
	actorIds = [nId for nId in graph if graph.node[nId]['type'] == 'ACTOR' or graph.node[nId]['type'] == 'ACTOR-DIRECTOR']
	actorDegrees = [graph.in_degree(aId) for aId in actorIds]
	
	nullModel = bipartite.configuration_model(movieDegrees, actorDegrees, create_using=nx.Graph())
	zeroIds = [nId for nId in nullModel if nullModel.node[nId]['bipartite'] == 0]
	oneIds = [nId for nId in nullModel if nullModel.node[nId]['bipartite'] == 1]

	shuffle(movieIds)
	shuffle(actorIds)
	for i in xrange(len(movieIds)):
		nullModel.node[zeroIds[i]].update(graph.node[movieIds[i]])
	for i in xrange(len(actorIds)):
		nullModel.node[oneIds[i]].update(graph.node[actorIds[i]])
	return nullModel

def directorMovieNullModel(graph):
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	movieDegrees = [1 for mId in movieIds]
	directorIds = [nId for nId in graph if graph.node[nId]['type'] == 'DIRECTOR' or graph.node[nId]['type'] == 'ACTOR-DIRECTOR']
	directorDegrees = [graph.out_degree(dId) for dId in directorIds]
	
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


def modularity(graph):
	aaGraph = actorActorGraph(graph)
	racePartition = {}
	blackWhitePartition = {}
	raceToInt = {
		'White': 0,
		'Black': 1,
		'Hispanic': 2,
		'Multiracial': 3,
		'Asian': 4,
		'Asian/Indian': 5,
		'Middle Eastern': 6,
		'American Aborigine': 7
	}
	for nId in aaGraph.nodes():
		actorRace = aaGraph.node[nId]['race']
		if actorRace in raceToInt:
			racePartition[nId] = raceToInt[actorRace]
			blackWhitePartition[nId] = 0 if raceToInt[actorRace] == 0 else 1
		else:
			aaGraph.remove_node(nId)
	aaGraph = multiToWeightedGraph(aaGraph)
	raceModularity = community.modularity(racePartition, aaGraph)
	blackWhiteModularity = community.modularity(blackWhitePartition, aaGraph)
	return raceModularity, blackWhiteModularity


def assortativity(graph, attribute, nodeSet=None):
	aaGraph = actorActorGraph(graph)
	return nx.attribute_assortativity_coefficient(aaGraph, attribute, nodeSet)

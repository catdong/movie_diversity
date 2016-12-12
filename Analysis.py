import networkx as nx
import itertools
from dataset import ReadMovieGraph
from networkx.algorithms import bipartite
from random import shuffle
import community
import DiversityScore as ds
import numpy as np

"""
FUNCTION: multiToWeightedGraph
---------------------------------
Parameters:
	graph - MultiGraph

Returns: an undirected Graph in which the 'weight' attribute
of an edge corresponds to the number times that edge appears
in the MultiGraph (needed to calculate modularity). 
Node attributes (excluding weight) are discarded.
---------------------------------
"""
def multiToWeightedGraph(multiGraph):
	weightedGraph = nx.Graph()
	for u, v in multiGraph.edges():
		if (u, v) not in weightedGraph.edges():
			weightedGraph.add_edge(u, v, weight=0)
		weightedGraph.edge[u][v]['weight'] += 1
	return weightedGraph

"""
FUNCTION: bipartiteToDirectedGraph
---------------------------------
Parameters:
	graph - bipartiteGraph

Returns: a DiGraph representation of the bipartiteGraph,
in which nodes whose 'bipartite' attribute is 0 point to nodes
whose 'bipartite' attribute is 1. All node attributes preserved.
---------------------------------
"""
def bipartiteToDirectedGraph(bipartiteGraph):
	directedGraph = nx.DiGraph()
	for u, v in bipartiteGraph.edges():
		if u not in directedGraph.nodes():
			directedGraph.add_node(u, bipartiteGraph.node[u])
		if v not in directedGraph.nodes():
			directedGraph.add_node(v, bipartiteGraph.node[v])

		if bipartiteGraph.node[u]['bipartite'] == 0:
			directedGraph.add_edge(u, v)
		else:
			directedGraph.add_edge(v, u)
	return directedGraph

"""
FUNCTION: multiToWeightedGraph
---------------------------------
Parameters:
	graph - graph containing actors
	graphDict - dict containing name->nodeId

Returns: Graph, graphDict in which all nodes have both race and gender data
---------------------------------
"""
def filterNoneActors(graph, graphDict):
	for nId in graph.nodes():
		node = graph.node[nId]
		if node['type'] == 'ACTOR':
			if node['race'] is None or node['gender'] is None:
				graphDict.pop(node["name"], None)
				graph.remove_node(nId)
		elif node['type'] == 'ACTOR-DIRECTOR':
			if node['race'] is None or node['gender'] is None:
				graph.remove_edges_from(graph.in_edges(nId))
				node['type'] = 'DIRECTOR'
	return (graph, graphDict)

"""
FUNCTION: getBlackWhiteGraph
---------------------------------
Parameters:
	graph - Graph containing actors

Returns: graph in which the 'race' attribute of all people nodes 
is either 'White' or 'Non-White' (None races are removed)
---------------------------------
"""
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

"""
FUNCTION: actorActorGraph
---------------------------------
Parameters:
	graph - DiGraph including movies and actors

Returns: MultiGraph of actor co-staring relationships.
All actor node attributes are preserverd.
---------------------------------
"""
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

"""
FUNCTION: movieActorNullModel
---------------------------------
Parameters:
	graph - DiGraph including movies and actors

Returns: DiGraph bipartite configuration model of movies and actors,
in which the edges between movies and actors have been shuffled,
but the degree of each node remains the same (almost...).
---------------------------------
"""
def movieActorNullModel(graph):
	nullModel = graph.copy()
	actorIds = [nId for nId in nullModel.nodes() if nullModel.node[nId]['type'] in ['ACTOR', 'ACTOR-DIRECTOR']]
	movieIds = [nId for nId in nullModel.nodes() if nullModel.node[nId]['type'] == 'MOVIE']
	for mId in movieIds:
		castSize = nullModel.out_degree(mId)
		nullModel.remove_edges_from(nullModel.out_edges(mId))
		randomCast = np.random.choice(actorIds, castSize, replace=False)
		nullModel.add_edges_from([(mId, aId) for aId in randomCast])

	# movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	# movieDegrees = [graph.out_degree(mId) for mId in movieIds]
	# sortedMovieIds = sorted(movieIds, key=lambda mId: graph.out_degree(mId))
	# actorIds = [nId for nId in graph if graph.node[nId]['type'] in ['ACTOR', 'ACTOR-DIRECTOR']]
	# actorDegrees = [graph.in_degree(aId) for aId in actorIds]
	# sortedActorIds = sorted(actorIds, key=lambda aId: graph.in_degree(aId))

	# nullModel = bipartite.configuration_model(movieDegrees, actorDegrees, create_using=nx.Graph())
	# zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	# sortedZeroIds = sorted(zeroIds, key=lambda nId: nullModel.degree(nId))
	# oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]
	# sortedOneIds = sorted(oneIds, key=lambda nId: nullModel.degree(nId))
	# for i in range(len(sortedZeroIds)):
	# 	nullModel.node[sortedZeroIds[i]].update(graph.node[sortedMovieIds[i]])
	# for i in range(len(sortedOneIds)):
	# 	nullModel.node[sortedOneIds[i]].update(graph.node[sortedActorIds[i]])
	# nullModel = bipartiteToDirectedGraph(nullModel)
	return nullModel

"""
FUNCTION: directorMovieNullModel
---------------------------------
Parameters:
	graph - DiGraph including directors and movies

Returns: DiGraph bipartite configuration model of directors and movies,
in which the edges between directors and movies have been shuffled,
but the degree of each node remains the same (almost...).
---------------------------------
"""
def directorMovieNullModel(graph):
	directorIds = [nId for nId in graph if graph.node[nId]['type'] == 'DIRECTOR' or graph.node[nId]['type'] == 'ACTOR-DIRECTOR']
	directorDegrees = [graph.out_degree(dId) for dId in directorIds]
	sortedDirectorDegrees = sorted(directorIds, key=lambda dId: graph.out_degree(dId))
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	movieDegrees = [1 for mId in movieIds]
	
	nullModel = bipartite.configuration_model(directorDegrees, movieDegrees, create_using=nx.Graph())
	zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	sortedZeroIds = sorted(zeroIds, key=lambda nId: nullModel.degree(nId))
	oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]
	for i in range(len(sortedZeroIds)):
		nullModel.node[sortedZeroIds[i]].update(graph.node[sortedDirectorDegrees[i]])
	for i in range(len(oneIds)):
		nullModel.node[oneIds[i]].update(graph.node[movieIds[i]])
	nullModel = bipartiteToDirectedGraph(nullModel)
	return nullModel

"""
FUNCTION: actorModularity
---------------------------------
Parameters:
	graph - DiGraph including movies and actors

Returns: modularity scores tuple (raceModularity, blackWhiteModularity, genderModularity)
---------------------------------
"""
def actorModularity(graph):
	aaGraph = actorActorGraph(graph)
	racePartition = {}
	blackWhitePartition = {}
	genderPartition = {}
	raceToInt = {
		'White': 0,
		'Black': 1,
		'Hispanic': 2,
		'Multiracial': 3,
		'Asian': 4,
		'Asian/Indian': 5,
		'Middle Eastern': 6,
		'American Aborigine': 7,
		'Other': 8
	}

	for nId in aaGraph.nodes():
		actorRace = aaGraph.node[nId]['race']
		actorGender = aaGraph.node[nId]['gender']
		if actorRace in raceToInt:
			racePartition[nId] = raceToInt[actorRace]
			blackWhitePartition[nId] = 0 if raceToInt[actorRace] == 0 else 1
		genderPartition[nId] = 0 if actorGender == 'Male' else 1

	aaGraph = multiToWeightedGraph(aaGraph)
	raceModularity = community.modularity(racePartition, aaGraph)
	blackWhiteModularity = community.modularity(blackWhitePartition, aaGraph)
	genderModularity = community.modularity(genderPartition, aaGraph)
	return (raceModularity, blackWhiteModularity, genderModularity)

"""
FUNCTION: actorAssortativity
---------------------------------
Parameters:
	graph - DiGraph including movies and actors

Returns: Assortativity coefficient tuple (raceAssortativity, blackWhiteAssortativity, genderAssortativity)
---------------------------------
"""
def actorAssortativity(graph):
	aaGraph = actorActorGraph(graph)
	raceAssortativity = nx.attribute_assortativity_coefficient(aaGraph, 'race')
	blackWhiteAAGraph = actorActorGraph(getBlackWhiteGraph(graph))
	blackWhiteAssortativity = nx.attribute_assortativity_coefficient(blackWhiteAAGraph, 'race')
	genderAssortativity = nx.attribute_assortativity_coefficient(aaGraph, 'gender')
	return (raceAssortativity, blackWhiteAssortativity, genderAssortativity)

"""
FUNCTION: actorDirectorAssortativityHeuristic
---------------------------------
Parameters:
	graph - tripartite DiGraph of directors, movies, and actors

Returns: Calculates the proportion of director-actor edges in which the director
and actor have the same race and proportion that have the same gender.
Returns a tuple of (proportionSameRace, proportionSameGender)
---------------------------------
"""
def actorDirectorAssortativityHeuristic(graph, directorMovieGraph, graphDict):
	numSameRaceEdges = 0
	numSameGenderEdges = 0
	totalEdges = 0
	for mId in directorMovieGraph.nodes():
		if directorMovieGraph.node[mId]['type'] == 'MOVIE':
			diredctorId = directorMovieGraph.predecessors(mId)[0]
			directorRace = directorMovieGraph.node[diredctorId]['race']
			if directorRace is None:
				continue
			directorGender = directorMovieGraph.node[diredctorId]['gender']
			actorIds = [graphDict[actorName] for actorName in directorMovieGraph.node[mId]['actorNames'] if actorName in graphDict]
			actorRaces = [graph.node[aId]['race'] for aId in actorIds if aId in graph.node and "race" in graph.node[aId]]
			actorGenders = [graph.node[aId]['gender'] for aId in actorIds if aId in graph.node and "gender" in graph.node[aId]]
			numSameRaceEdges += sum(1 for ar in actorRaces 
				if (ar == 'White' and directorRace == 'White') or (ar != 'White' and directorRace != 'White'))
			numSameGenderEdges += sum(1 for ag in actorGenders if ag == directorGender)
			totalEdges += len(actorIds)
	return (numSameRaceEdges / float(totalEdges), numSameGenderEdges / float(totalEdges))

"""
FUNCTION: diversityProfitCorrelation
---------------------------------
Parameters:
	graph - the tripartite NetworkX DiGraph continaing

Returns: tuple of (correlation coefficient for race, correlation coefficient for gender) 
"""
def diversityProfitCorrelation(graph, movieIds=None):
	raceScores = []
	genderScores = []
	profitRatios = []
	if not movieIds:
		movieIds = [nId for nId in graph.nodes() if graph.node[nId]["type"] == "MOVIE"]
	for mId in movieIds:
		if graph.node[mId]["type"] == "MOVIE":
			data = ds.profitStats(graph, mId)
			if data[0] != None and data[1] != None and data[2] != None: 
				raceScores.append(data[0])
				genderScores.append(data[1])
				profitRatios.append(data[2])

	correlations = np.corrcoef([raceScores, genderScores, profitRatios])

	return correlations[0,2], correlations[1,2]

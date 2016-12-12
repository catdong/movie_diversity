import networkx as nx
import itertools
from dataset import ReadMovieGraph
from networkx.algorithms import bipartite
from random import shuffle
import community

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

Returns: Graph in which all nodes have both race and gender data
---------------------------------
"""
def filterNoneActors(graph):
	for nId in graph.nodes():
		if graph.node[nId]['type'] == 'ACTOR':
			if graph.node[nId]['race'] is None or graph.node[nId]['gender'] is None:
				graph.remove_node(nId)
		elif graph.node[nId]['type'] == 'ACTOR-DIRECTOR':
			if graph.node[nId]['race'] is None or graph.node[nId]['gender'] is None:
				graph.remove_edges_from(graph.in_edges(nId))
				graph.node[nId]['type'] = 'DIRECTOR'
	return graph

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
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	movieDegrees = [graph.out_degree(mId) for mId in movieIds]
	sortedMovieIds = sorted(movieIds, key=lambda mId: graph.out_degree(mId))
	actorIds = [nId for nId in graph if graph.node[nId]['type'] in ['ACTOR', 'ACTOR-DIRECTOR']]
	actorDegrees = [graph.in_degree(aId) for aId in actorIds]
	sortedActorIds = sorted(actorIds, key=lambda aId: graph.in_degree(aId))

	nullModel = bipartite.configuration_model(movieDegrees, actorDegrees, create_using=nx.Graph())
	zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	sortedZeroIds = sorted(zeroIds, key=lambda nId: nullModel.degree(nId))
	oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]
	sortedZeroIds = sorted(zeroIds, key=lambda nId: nullModel.degree(nId))
	for i in range(len(zeroIds)):
		nullModel.node[zeroIds[i]].update(graph.node[movieIds[i]])
	for i in range(len(oneIds)):
		nullModel.node[oneIds[i]].update(graph.node[actorIds[i]])
	nullModel = bipartiteToDirectedGraph(nullModel)
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
	movieIds = [nId for nId in graph if graph.node[nId]['type'] == 'MOVIE']
	movieDegrees = [1 for mId in movieIds]
	
	nullModel = bipartite.configuration_model(directorDegrees, movieDegrees, create_using=nx.Graph())
	zeroIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 0]
	sortedZeroIds = sorted(zeroIds, key=lambda nId: nullModel.degree(nId))
	oneIds = [id for id in nullModel if nullModel.node[id]['bipartite'] == 1]
	sortedZeroIds = sorted(zeroIds, key=lambda nId: nullModel.degree(nId))
	for i in range(len(zeroIds)):
		nullModel.node[zeroIds[i]].update(graph.node[directorIds[i]])
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
def actorDirectorAssortativityHeuristic(graph):
	numSameRaceEdges = 0
	numSameGenderEdges = 0
	totalEdges = 0
	for aId in graph.nodes():
		if graph.node[aId]['type'] != 'MOVIE':
			actorRace = graph.node[aId]['race']
			actorGender = graph.node[aId]['gender']
			actorMovies = graph.predecessors(aId)
			actorDirectors = [graph.predecessors(mId)[0] for mId in actorMovies]
			totalEdges += len(actorDirectors)
			directorRaces = [graph.node[dId]['race'] for dId in actorDirectors]
			directorGenders = [graph.node[dId]['gender'] for dId in actorDirectors]
			numSameRaceEdges += sum(1 for dr in directorRaces 
				if (dr == 'White' and actorRace == 'White') or (dr != 'White' and actorRace != 'White'))
			numSameGenderEdges += sum(1 for dg in directorGenders if dg == actorGender)
	return (numSameRaceEdges / float(totalEdges), numSameGenderEdges / float(totalEdges))

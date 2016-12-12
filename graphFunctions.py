import DiversityScore as ds
import Analysis as ana
import numpy as np

def avgDirectorRacialDiversityScore(graph, movieIds):
	scores = []
	for dId in graph.nodes():
		if graph.node[dId]['type'] == 'DIRECTOR' or graph.node[dId]['type'] == 'ACTOR-DIRECTOR':
			score = ds.racialScoreForDirector(graph, dId)
			if score is not None:
				scores.append(score)
	return [np.mean(scores)]

def avgDirectorGenderDiversityScore(graph, movieIds):
	scores = []
	for dId in graph.nodes():
		if graph.node[dId]['type'] == 'DIRECTOR' or graph.node[dId]['type'] == 'ACTOR-DIRECTOR':
			score = ds.genderScoreForDirector(graph, dId)
			if score is not None:
				scores.append(score)
	return [np.mean(scores)]

def avgMovieRacialDiversityScore(graph, movieIds):
	scores = []
	for mId in graph.nodes():
		if graph.node[mId]['type'] == 'MOVIE':
			score = ds.racialScoreForMovie(graph, mId)
			if score is not None:
				scores.append(score)
	return [np.mean(scores)]

def avgMovieGenderDiversityScore(graph, movieIds):
	scores = []
	for mId in graph.nodes():
		if graph.node[mId]['type'] == 'MOVIE':
			score = ds.genderScoreForMovie(graph, mId)
			if score is not None:
				scores.append(score)
	return [np.mean(scores)]

def actorModularity(graph, movieIds):
	raceModularity, blackWhiteModularity, genderModularity = ana.actorModularity(graph)
	return [blackWhiteModularity, genderModularity]

def actorAssortativity(graph, movieIds):
	raceAssorativity, blackWhiteAssorativity, genderAssorativity = ana.actorAssortativity(graph)
	return [blackWhiteAssorativity, genderAssorativity]

def actorDirectorAssortativity(graph, movieIds, graphDict):
	return ana.actorDirectorAssortativityHeuristic(graph, ana.directorMovieNullModel(graph), graphDict)

def racialDiversityScoreProfitCorrelation(graph, movieIds):
	return ana.diversityProfitCorrelation(graph, movieIds)[0]

def genderDiversityScoreProfitCorrelation(graph, movieIds):
	return ana.diversityProfitCorrelation(graph, movieIds)[1]

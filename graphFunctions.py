import DiversityScore as ds
import Analysis as ana
import numpy as np

def avgDirectorRacialDiversityScore(graph, movieIds):
	scores = []
	for dId in graph.nodes():
		if graph.node[dId]['type'] == 'DIRECTOR' or graph.node[dId]['type'] == 'ACTOR-DIRECTOR':
			scores.append(ds.racialScoreForDirector(dId))
	return [np.mean(scores)]

def avgDirectorGenderDiversityScore(graph, movieIds):
	scores = []
	for dId in graph.nodes():
		if graph.node[dId]['type'] == 'DIRECTOR' or graph.node[dId]['type'] == 'ACTOR-DIRECTOR':
			scores.append(ds.genderScoreForDirector(dId))
	return [np.mean(scores)]

def avgMovieRacialDiversityScore(graph, movieIds):
	scores = []
	for mId in movieIds:
		scores.append(racialScoreForMovie(graph, mId))
	return [np.mean(scores)]

def avgMovieGenderDiversityScore(graph, movieIds):
	scores = []
	for mId in movieIds:
		scores.append(GenderScoreForMovie(graph, mId))
	return [np.mean(scores)]

def actorModularity(graph, movieIds):
	raceModularity, blackWhiteModularity, genderModularity = ana.actorModularity(graph)
	return [blackWhiteModularity, genderModularity]

def actorAssorativity(graph, movieIds):
	raceAssorativity, blackWhiteAssorativity, genderAssorativity = ana.actorAssortativity(graph)
	return [blackWhiteAssorativity, genderAssorativity]

def actorDirectorAssortativity(graph, movieIds):
	return ana.actorDirectorAssortativityHeuristic(graph, directorMovieNullModel, graphDict)

def racialDiversityScoreProfitCorrelation(graph, movieIds):
	return diversityProfitCorrelation(graph, movieIds)[0]

def genderDiversityScoreProfitCorrelation(graph, movieIds):
	return diversityProfitCorrelation(graph, movieIds)[1]

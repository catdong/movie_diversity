import DiversityScore as ds
import Analysis as ana
import numpy as np

def avgDirectorRacialDiversityScore(graph, movieIds):
	scores = []
	for dId in graph.nodes():
		if graph.node[dId]['type'] == 'DIRECTOR' or graph.node[dId]['type'] == 'ACTOR-DIRECTOR':
			scores.append(ds.racialScoreForDirector(dId))
	return np.mean(scores)

def avgDirectorGenderDiversityScore(graph, movieIds):
	scores = []
	for dId in graph.nodes():
		if graph.node[dId]['type'] == 'DIRECTOR' or graph.node[dId]['type'] == 'ACTOR-DIRECTOR':
			scores.append(ds.genderScoreForDirector(dId))
	return np.mean(scores)

def avgMovieRacialDiversityScore(graph, movieIds):
	scores = []
	for mId in movieIds:
		scores.append(racialScoreForMovie(graph, mId))
	return np.mean(scores)

def avgMovieGenderDiversityScore(graph, movieIds):
	scores = []
	for mId in movieIds:
		scores.append(GenderScoreForMovie(graph, mId))
	return np.mean(scores)
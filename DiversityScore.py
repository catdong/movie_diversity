"""
FUNCTIONS: racialScoreForDirector and genderScoreForDirector
---------------------------------
Parameters:
	graph - the NetworkX DiGraph to use to compute a diversity score
	nodeId - the nodeId of the director (or actor-director) for which to compute
				the diversity score.

Returns: the racial or gender diversity score for the given director in the given graph. 
The diversity score for a director is the average diversity score of all movies
they have directed (aka between 0 and 1).
---------------------------------
"""
def racialScoreForDirector(graph, nodeId):
	movieIds = graph.successors(nodeId)
	movieScores = [racialScoreForMovie(graph, i) for i in movieIds]
	return sum(movieScores) / float(len(movieScores))

def genderScoreForDirector(graph, nodeId):
	movieIds = graph.successors(nodeId)
	movieScores = [genderScoreForMovie(graph, i) for i in movieIds]
	return sum(movieScores) / float(len(movieScores))

"""
FUNCTIONS: racialScoreForMovie and genderScoreForMovie
------------------------
Parameters:
	graph - the NetworkX DiGraph to use to compute a diversity score
	nodeId - the nodeId of the movie for which to compute the diversity score.

Returns: the racial or gender diversity score for the given movie in the given graph.
The diversity score for a movie is the average diversity score of all actors in that
movie's cast (aka between 0 and 1). Or None if the size of the movie cast is 0.
------------------------
"""
def racialScoreForMovie(graph, nodeId):
	castIds = graph.successors(nodeId)
	numMinorities = sum(racialScoreForActor(graph.node[i]) for i in castIds)
	if len(castIds) == 0:
		return None
	return numMinorities / float(len(castIds))

def genderScoreForMovie(graph, nodeId):
	castIds = graph.successors(nodeId)
	numMinorities = sum(genderScoreForActor(graph.node[i]) for i in castIds)
	if len(castIds) == 0:
		return None
	return numMinorities / float(len(castIds))

"""
FUNCTION: racialScoreForActor and genderScoreForActor
---------------------
Parameters:
	actorDict - a dictionary of attributes for a particular actor, including
				name, gender and race.

Returns: the diversity score for the given actor/actress. 
Racial diversity: 1 if they are non-white, and 0 otherwise.
Gender diversity: 1 if they are female, and 0 otherwise.
---------------------
"""
def racialScoreForActor(actorDict):
	return int(actorDict["race"] != "White")

def genderScoreForActor(actorDict):
	return int(actorDict["gender"] == "Female")

"""
FUNCTION: directorStats
---------------------------------
Parameters:
	graph - the tripartite NetworkX DiGraph continaing

Returns: dicts
{
	numDirectors: int,
	avgRacialDiversityScore: float,
	avgGenderDiversityScore: float,
	numWhiteDirectors: int,
	numNonWhiteDirectors: int,
	numMaleDirectors: int,
	numFemaleDirectors: int,
}
---------------------------------
"""
def directorStats(graph):
	pass

"""
FUNCTION: movieStats
---------------------------------
Parameters:
	graph - the tripartite NetworkX DiGraph continaing

Returns: dicts
{
	numMovies: int,
	avgRacialDiversityScore: float,
	avgGenderDiversityScore: float,
	numAllWhiteMovies: int,
	numAllNonWhiteMovies: int,
	numAllMaleMovies: int,
	numAllFemaleMovies: int,
}
---------------------------------
"""
def movieStats(graph):
	pass

"""
FUNCTION: actorStats
---------------------------------
Parameters:
	graph - the tripartite NetworkX DiGraph continaing

Returns: dict 
{
	'numActors': int,

	'numWhite': int, 
	'numBlack': int,
	'numHispanic': int,
	'numMultiracial': int,
	'numAsian': int,
	'numAsianIndian': int,
	'numMiddleEastern': int,
	'numAmericanAborigine': int,
	'numNonWhite': int,

	'numMale': int,
	'numFemale': int,

	'avgNumMoviesForWhiteActor': float,
	'avgNumMoviesForNonWhiteActor': float,

	'avgNumMoviesForMaleActor': float,
	'avgNumMoviesForFemaleActor': float,
}
---------------------------------
"""
def actorStats(graph):
	pass
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
FUNCTIONS: racialScoreForActor and genderScoreForActor
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
	directorDict = collections.defaultdict()
	numDirectors = 0
	race_scores = []
	gender_scores = []
	numWhiteDirectors = 0
	numNonWhiteDirectors = 0
	numMaleDirectors = 0
	numFemaleDirectors = 0
	for node in graph.nodes():
		node_type = graph.node[node]["type"]
		if node_type == "DIRECTOR" or node_type == "ACTOR-DIRECTOR":
			race_scores.append(racialScoreForDirector(graph,node))
			gender_scores.append(genderScoreForDirector(graph,node))
			numDirectors += 1
			if graph.node[node]["gender"] == "Male":
				numMaleDirectors += 1
			if graph.node[node]["gender"] == "Female":
				numFemaleDirectors += 1
			if graph.node[node]["race"] == "White":
				numWhiteDirectors += 1
			else:
				numNonWhiteDirectors += 1

	directorDict["numDirectors"] = numDirectors
	directorDict["avgRacialDiversityScore"] = float(sum(race_scores)) / float(len(race_scores))
	directorDict["avgGenderDiversityScore"] = float(sum(gender_scores)) / float(len(race_scores))
	directorDict["numWhiteDirectors"] = numWhiteDirectors
	directorDict["numNonWhiteDirectors"] = numNonWhiteDirectors
	directorDict["numMaleDirectors"] = numMaleDirectors
	directorDict["numFemaleDirectors"] = numFemaleDirectors
	return directorDict

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
	numHalfFemaleMovies: int,
}
---------------------------------
"""
def movieStats(graph):
	movieDict = collections.defaultdict()
	numMovies = 0
	race_scores = []
	gender_scores = []
	numAllWhiteMovies = 0
	numAllNonWhiteMovies = 0
	numAllMaleMovies = 0
	numAllFemaleMovies = 0
	numHalfFemaleMovies = 0
	for node in graph.nodes():
		node_type = graph.node[node]["type"]
		if node_type == "MOVIE":
			race_score = racialScoreForMovie(graph,node)
			gender_score = genderScoreForMovie(graph,node)
			race_scores.append(race_score)
			gender_scores.append(gender_scores)
			if race_score == 0: # all white cast
				numAllWhiteMovies += 1
			else:
				numAllNonWhiteMovies += 1
			if gender_score == 0: # all male cast
				numAllMaleMovies += 1
			if gender_score == 1: # all female cast
				numAllFemaleMovies += 1
			if gender_score >= 0.5:
				numHalfFemaleMovies += 1
			numMovies += 1

	movieDict["numMovies"] = numMovies
	movieDict["avgRacialDiversityScore"] = float(sum(race_scores)) / float(len(race_scores))
	movieDict["avgGenderDiversityScore"] = float(sum(gender_scores)) / float(len(gender_scores))
	movieDict["numAllWhiteMovies"] = numAllWhiteMovies
	movieDict["numAllNonWhiteMovies"] = numAllNonWhiteMovies
	movieDict["numAllMaleMovies"] = numAllMaleMovies
	movieDict["numAllFemaleMovies"] = numAllFemaleMovies
	movieDict["numHalfFemaleMovies"] = numHalfFemaleMovies
	return movieDict

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
	actorDict = collections.defaultdict()

	numActors = 0
	numWhite = 0
	numBlack = 0
	numHispanic = 0
	numMultiracial = 0
	numAsian = 0
	numAsianIndian = 0
	numMiddleEastern = 0
	numAmericanAborigine = 0
	numNonWhite = 0
	
	numMale = 0
	numFemale = 0

	white_movies = []
	nonwhite_movies = []
	male_movies = []
	female_movies = []

	avgNumMoviesForWhiteActor = 0
	avgNumMoviesForNonWhiteActor = 0
	avgNumMoviesForMaleActor = 0
	avgNumMoviesForFemaleActor = 0

	for node in graph.nodes():
		node_type = graph.node[node]["type"]
		if node_type == "ACTOR" or node_type == "ACTOR-DIRECTOR":
			race = graph.node[node]["race"]
			gender = graph.node[node]["gender"]
			if race == "White":
				numWhite += 1
				white_movies.append(len(graph.predecessors(node)))
			else:
				numNonWhite += 1
				nonwhite_movies.append(len(graph.predecessors(node)))
			if race == "Black":
				numBlack += 1
			if race == "Hispanic":
				numHispanic += 1
			if race == "Multiracial":
				numMultiracial += 1
			if race == "Asian":
				numAsian += 1
			if race == "AsianIndian":
				numAsianIndian += 1
			if race == "MiddleEastern":
				numMiddleEastern += 1
			if race == "AmericanAborigine":
				numAmericanAborigine += 1
			if gender == "Male":
				numMale += 1 
				male_movies.append(len(graph.predecessors(node)))
			if gender == "Female":
				numFemale += 1
				female_movies.append(len(graph.predecessors(node)))
			numActors += 1

	actorDict["numActors"] = numActors
	actorDict["numWhite"] = numWhite
	actorDict["numNonWhite"] = numNonWhite
	actorDict["numBlack"] = numBlack
	actorDict["numHispanic"] = numHispanic
	actorDict["numMultiracial"] = numMultiracial
	actorDict["numAsian"] = numAsian
	actorDict["numAsianIndian"] = numAsianIndian
	actorDict["numMiddleEastern"] = numMiddleEastern
	actorDict["numAmericanAborigine"] = numAmericanAborigine
	actorDict["numMale"] = numMale
	actorDict["numFemale"] = numFemale
	actorDict["avgNumMoviesForWhiteActor"] = float(sum(white_movies)) / len(white_movies)
	actorDict['avgNumMoviesForNonWhiteActor'] = float(sum(nonwhite_movies)) / len(nonwhite_movies)
	actorDict['avgNumMoviesForMaleActor'] = float(sum(male_movies)) / len(male_movies)
	actorDict['avgNumMoviesForFemaleActor'] = float(sum(female_movies)) len(female_movies)
	return actorDict






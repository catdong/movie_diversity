"""
FUNCTION: scoreForDirector
---------------------------------
Parameters:
	graph - the NetworkX DiGraph to use to compute a diversity score
	nodeId - the nodeId of the director (or actor-director) for which to compute
				the diversity score.

Returns: the diversity score for the given director in the given graph.  The
diversity score for a director is the average diversity score of all movies
they have directed (aka between 0 and 1).
---------------------------------
"""
def scoreForDirector(graph, nodeId):
	movieIds = graph.successors(nodeId)
	movieScores = [scoreForMovie(graph, i) for i in movieIds]
	return sum(movieScores) / float(len(movieScores))

"""
FUNCTION: scoreForMovie
------------------------
Parameters:
	graph - the NetworkX DiGraph to use to compute a diversity score
	nodeId - the nodeId of the movie for which to compute the diversity score.

Returns: the diversity score for the given movie in the given graph.  The
diversity score for a movie is the average diversity score of all actors in that
movie's cast (aka between 0 and 1). Or None if the size of the movie cast is 0.
------------------------
"""
def scoreForMovie(graph, nodeId):
	castIds = graph.successors(nodeId)
	numMinorities = sum(scoreForActor(graph.node[i]) for i in castIds)
	if len(castIds) == 0:
		return None
	return numMinorities / float(len(castIds))

"""
FUNCTION: scoreForActor
---------------------
Parameters:
	actorDict - a dictionary of attributes for a particular actor, including
				name, gender and race.

Returns: the diversity score for the given actor/actress.  0 if they are a
minority, and 1 otherwise.  For the purposes of these calculations, a minority
is considered anyone who is not a white male.
---------------------
"""
def scoreForActor(actorDict):
	minority = (actorDict["race"] == "White" and actorDict["gender"] == "Male")
	return 0 if minority else 1
import csv
from GraphConstants import graphFilename, graphDictFilename
import networkx as nx


"""
FUNCTION: readMovieGraphFromFile
-----------------------------
Parameters: NA

Returns a (graph, graphDict) tuple where the graph is a tripartite NetworkX
graph of movies, directors and actors, and the graphDict is a map from movie,
director and actor names to their corresponding nodeID in the graph.  Each node
in the graph has metadata associated with it.  Specifically, each node has:

	- a "type" field which can be one of: "ACTOR", "DIRECTOR", "ACTOR-DIRECTOR", 
		"MOVIE"

	- a "metadata" field which is a dictionary containing attributes about that
	node.  This differs for people and movies:

		- Actors and Directors have "name", "gender" and "race" entries.

		- Movies have the following entries:

			inColor (bool): whether the movie was in color or not

			directorName (string): name of movie's director

			numReviewCritics (int): number of critics reviewing the movie 

			durationMinutes (int): length of movie in minutes

			directorFacebookLikes (int): number of Facebook likes director has

			actorNames (list of strings): list of at most 3 primary actor names

			actorsFacebookLikes (list of ints): matches actorNames length, where
				actorsFacebookLikes[i] is the number of Facebook likes
				actorNames[i] has.

			gross (int): gross income for the movie

			genres (list of strings): list of genres for this movie

			title (string): movie title

			numVotingUsers (int): number of users that voted on this movie

			castFacebookLikes (int): number of Facebook likes the whole cast has

			numPosterFaces (int): number of faces on the movie poster

			plotKeywords (list of strings): list of plot keywords

			imdbURL (string): url of this movie's IMDB page

			numReviewUsers (int): number of users who reviewed this movie

			language (string): the language this movie is in

			country (string): the country this movie was made in

			contentRating (string): the rating of this movie (e.g. "PG-13")

			budget (int): movie's budget

			releaseYear (int): year movie was released

			imdbScore (float): movie's score on IMDB

			aspectRatio (float): movie's aspect ratio (e.g. 1.67)

			movieFacebookLikes (int): number of Facebook likes this movie has
-----------------------------
"""
def readMovieGraphFromFile():
	graph = nx.read_gpickle(graphFilename)
	graphDict = readDictFromFile(graphDictFilename, True, valueDecodeFn=int)
	return graph, graphDict

"""
FUNCTION: readDictFromFile
---------------------------
Parameters:
	filename - the name of the file the dict is stored in
	discardFirstRow - whether to skip over the first row in the file
	keyDecodeFn - optional decode function that converts row[0] into the key to
					put in the decoded dict object we return.
	valueDecodeFn - optional decode function that converts row[1:] into the
					value to put in the decoded dict object we return.

Returns: the decoded dict object represented in the file with the given name.
---------------------------
"""
def readDictFromFile(filename, discardFirstRow, keyDecodeFn=None,
	valueDecodeFn=None):

	newDict = {}
	with open(filename, 'rb') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',')
		isFirstRow = True
		for row in csvreader:
			if isFirstRow and discardFirstRow:
				isFirstRow = False
				continue

			# Parse the key
			if not keyDecodeFn:
				key = row[0]
			else:
				key = keyDecodeFn(row[0])

			# Parse the value
			if not valueDecodeFn:
				value = row[1:]
			elif len(row) > 2:
				value = valueDecodeFn(row[1:])
			else:
				value = valueDecodeFn(row[1])

			newDict[key] = value

		return newDict


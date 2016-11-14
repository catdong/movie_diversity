from collections import Counter
import csv
from lxml import html
import requests
import snap


"""
CLASS: Movie
--------------
A class representing information about a single movie.  Contains information
such as title, release year, director, main actors, gross revenue, review
ratings, Facebook likes, and more.

Created from a single length-28 row in the Kaggle movies dataset.
--------------
"""
class Movie:

	def __init__(self, dataRow):
		numericCols = set([2, 3, 4, 7, 24, 5, 8, 12, 13, 15, 18, 22, 23, 25, 26,
						   27])

		# Removes trailing whitespace, escape characters, and ensures all
		# numerically-parsed cols are non-empty
		def cleanupRowEntry(args):
			i, entry = args
			entry = entry.replace("\xc2\xa0", " ").strip().decode('utf-8')
			if i in numericCols and len(dataRow[i]) == 0:
				return "0"
			else:
				return entry

		# Cleanup all data before parsing
		dataRow = map(cleanupRowEntry, enumerate(dataRow))

		self.inColor = dataRow[0] == "Color"
		self.directorName = dataRow[1]
		self.numReviewCritics = int(dataRow[2])
		self.durationMinutes = int(dataRow[3])
		self.directorFacebookLikes = int(dataRow[4])

		# Store as many actors as possible
		self.actorNames = list()
		self.actorsFacebookLikes = list()
		if len(dataRow[10]) > 0:
			self.actorNames.append(dataRow[10])
			self.actorsFacebookLikes.append(int(dataRow[7]))
		if len(dataRow[6]) > 0:
			self.actorNames.append(dataRow[6])
			self.actorsFacebookLikes.append(int(dataRow[24]))
		if len(dataRow[14]) > 0:
			self.actorNames.append(dataRow[14])
			self.actorsFacebookLikes.append(int(dataRow[5]))

		self.gross = int(dataRow[8])
		self.genres = dataRow[9].split("|")
		self.title = dataRow[11]
		self.numVotingUsers = int(dataRow[12])
		self.castFacebookLikes = int(dataRow[13])
		self.numPosterFaces = int(dataRow[15])
		self.plotKeywords = dataRow[16].split("|")
		self.imdbURL = dataRow[17]
		self.numReviewUsers = int(dataRow[18])
		self.language = dataRow[19]
		self.country = dataRow[20]
		self.contentRating = dataRow[21]
		self.budget = int(dataRow[22])
		self.releaseYear = int(dataRow[23])
		self.imdbScore = float(dataRow[25])
		self.aspectRatio = float(dataRow[26])
		self.movieFacebookLikes = int(dataRow[27])

	def __str__(self):
		desc = "-----'%s' (%i)-----\n" % (self.title, self.releaseYear)
		desc += "Color: %s\n"  % self.inColor
		desc += "Director: %s\n" % self.directorName
		desc += "Review Critics: %i\n" % self.numReviewCritics
		desc += "Duration (min): %i\n" % self.durationMinutes
		desc += "Director FB Likes: %i\n" % self.directorFacebookLikes
		desc += "Main actors: %s\n" % self.actorNames
		desc += "Actors FB Likes: %s\n" % self.actorsFacebookLikes
		desc += "Gross: %i\n" % self.gross
		desc += "Genres: %s\n" % self.genres
		desc += "Voting users: %i\n" % self.numVotingUsers
		desc += "Cast FB Likes: %i\n" % self.castFacebookLikes
		desc += "# Poster Faces: %i\n" % self.numPosterFaces
		desc += "Plot keywords: %s\n" % self.plotKeywords
		desc += "IMDB URL: %s\n" % self.imdbURL
		desc += "# Review Users: %i\n" % self.numReviewUsers
		desc += "Language: %s\n" % self.language
		desc += "Country: %s\n" % self.country
		desc += "Rating: %s\n" % self.contentRating
		desc += "Budget: %i\n" % self.budget
		desc += "IMDB Score: %f\n" % self.imdbScore
		desc += "Aspect ratio: %f\n" % self.aspectRatio
		desc += "Movie FB likes: %i\n" % self.movieFacebookLikes
		return desc

	"""
	FUNCTION: uniqueID
	-------------------
	Parameters: NA
	Returns: A unique identifier string for this movie.  This identifier is a
			concatenation of the title and release year, to guarantee that
			remakes of movies have unique identifiers from their originals.
	-------------------
	"""
	def uniqueID(self):
		return "%s%i" % (self.title, self.releaseYear)


"""
CLASS: Actor
-------------
A class representing information about a single actor.  Contains the actor's
name, gender, and race.
-------------
"""
class Actor:

	def __init__(self, name):
		self.name = name
		self.gender = None
		self.race = None

	def __str__(self):
		return "%s, Gender: %s, Race: %s" % (self.name, self.gender, self.race)

	"""
	FUNCTION: fetchRaceAndGender
	------------------------------
	Parameters: NA
	Returns: NA

	Attempts to fetch the race and gender of this actor from search.nndb.com.
	Synchronously fetches, and fills in the race and gender fields on completion
	with the results (either the race and gender, or None if they could not be
	found).
	------------------------------
	"""
	def fetchRaceAndGender(self):
		name = self.name.split()
		query = "+".join(name)
		url = "http://search.nndb.com/search/?type=unspecified&query=%s" % query
		searchPage = requests.get(url)
		searchTree = html.fromstring(searchPage.content)
		if len(name) > 1:
			condition = '[contains(.//text(), "%s")' % name[0]
			condition += ' and contains(.//text(), "%s")]' % name[1]
		else:
			condition = '[contains(.//text(), "%s")]' % name[0]
		personList = searchTree.xpath('//table')[3].xpath('./tr')[1]
		personList = personList.xpath('./td' + condition)
		if personList:
			personUrl = personList[0].xpath('.//a/@href')[0]
		else:
			print "Could not fetch info for %s" % self.name
			return

		personPage = requests.get(personUrl)
		personTree = html.fromstring(personPage.content)
		raceStr = '//p/b[text()="Race or Ethnicity:"]/following-sibling::text()'
		self.race = personTree.xpath(raceStr)[0].strip()
		genderStr = '//p/b[text()="Gender:"]/following-sibling::text()'
		self.gender = personTree.xpath(genderStr)[0].strip()
		print "Fetched race/gender for %s..." % self.name


"""
FUNCTION: parseMovieFile
-------------------------
Parameters:
	filename - the name of the Kaggle movie data file to parse

Returns: a tuple (movieMap, actorMap).  movieMap is a map from a movie
		unique ID to its Movie object.  Note that a movie's unique ID is just
		the concatenation of its title and release year, to avoid conflicts
		between movie remakes with the same name.

		actorMap is a map from an actor name to an Actor object.
-------------------------
"""
def parseMovieFile(filename):
	with open(filename, 'rb') as csvFile:
		csvFile = csv.reader(csvFile, delimiter=',')
		firstRow = False

		movieMap = {}
		actorMap = {}
		for row in csvFile:
			if not firstRow:
				firstRow = True
			else:
				newMovie = Movie(row)
				if not newMovie.uniqueID() in movieMap:
					movieMap[newMovie.uniqueID()] = newMovie
					for actorName in newMovie.actorNames:
						if not actorName in actorMap:
							newActor = Actor(actorName)
							newActor.fetchRaceAndGender()
							actorMap[actorName] = newActor

		return movieMap, actorMap

"""
FUNCTION: createGraphForMovies
-------------------------------
Parameters:
	movieMap - a map containing all the movies to add to the graph.  The map
				should be a map from unique movie IDs to Movie objects.
	actorMap - a map containing all the actors to add to the graph.  The map
				should be a map from actor names to Actor objects.

Returns: a tuple of (graph, movieNodeMap, actorNodeMap, movieInfoMap,
		actorInfoMap).  The graph is a	bipartite Snap.PY TUNGraph (undirected
		graph) where nodes are either movies or actors.  An edge indicates that
		an actor is in a given movie.

		The movieNodeMap is a map from movie unique IDs to their Node ID in the
		graph.

		The actorNodeMap is a map from actor names to their Node ID in the
		graph. 

		The movieInfoMap is a map from Node ID to Movie objects.

		The actorInfoMap is a map from Node ID to Actor objects.
-------------------------------
"""		
def createGraphForMovies(movieMap, actorMap):
	movieGraph = snap.TUNGraph.New()
	movieNodeMap = {}
	actorNodeMap = {}
	movieInfoMap = {}
	actorInfoMap = {}

	for movieID in movieMap:
		movie = movieMap[movieID]
		addMovieToGraph(movieGraph, movieNodeMap, actorNodeMap, movie)

		# Track metadata
		movieInfoMap[movieNodeMap[movieID]] = movie
		for actorName in movie.actorNames:
			if not actorName in actorInfoMap:
				actorInfoMap[actorNodeMap[actorName]] = actorMap[actorName]

	return (movieGraph, movieNodeMap, actorNodeMap, movieInfoMap, actorInfoMap)

"""
FUNCTION: addMovieToGraph
--------------------------
Parameters:
	graph - the graph to add the movie to.
	movieNodeMap - the map of movie unique IDs to graph Node IDs.  Updates this
					map to add info about the newly-added movie.
	actorNodeMap - the map of actor names to graph Node IDs.  Updates this map
				if needed to add info about the new movie's actors (may not
				change if actors are already in the graph for other movies).
	movie - the Movie object to add to the graph

Returns: NA

Adds the given movie info to the given graph.  Updates the movie node map to add
info about the new movie's node in the graph, and updates the actor node map if
needed to add info about the new movie's actors.  Note that the movie's actors
could already be in the graph from other movies, so actorNodeMap may not change.

Node IDs are added contiguously to the graph starting at 0.
--------------------------
"""
def addMovieToGraph(graph, movieNodeMap, actorNodeMap, movie):	
	# Add a node for the movie
	nextNodeID = graph.GetNodes()
	graph.AddNode(nextNodeID)
	movieNodeMap[movie.uniqueID()] = nextNodeID

	# Add nodes for the main actors if needed, plus edges
	for actorName in movie.actorNames:
		if not actorName in actorNodeMap:
			nextNodeID = graph.GetNodes()
			graph.AddNode(nextNodeID)
			actorNodeMap[actorName] = nextNodeID

		graph.AddEdge(movieNodeMap[movie.uniqueID()], actorNodeMap[actorName])

"""
FUNCTION: createMovieGraph
---------------------------
Parameters: NA
Returns: a tuple of (graph, movieNodeMap, actorNodeMap, movieInfoMap,
		actorInfoMap) created from data from "movieData.csv".  The graph is a
		bipartite Snap.PY TUNGraph (undirected graph) where nodes are either
		movies or actors.  An edge indicates that an actor is in a given movie.

		The movieNodeMap is a map from movie unique IDs to their Node ID in the
		graph.

		The actorNodeMap is a map from actor names to their Node ID in the
		graph. 

		The movieInfoMap is a map from Node ID to Movie objects.

		The actorInfoMap is a map from Node ID to Actor objects.
---------------------------
"""
def createMovieGraph():
	movieMap, actorMap = parseMovieFile("movie_metadata.csv")
	return createGraphForMovies(movieMap, actorMap)


createMovieGraph()

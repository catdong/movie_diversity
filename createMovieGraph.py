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

	"""
	CLASS METHOD: decode
	----------------------
	Parameters:
		encoding - the encoding for a Movie object

	Returns: the decoded Movie object
	----------------------
	"""
	@classmethod
	def decode(cls, encoding):
		return cls(encoding)

	"""
	METHOD: init
	--------------
	Parameters:
		dataRow - an array of information from the Kaggle movies dataset
				containing information about a single movie.  Should be len 28.

	Returns: a Movie object storing all the information given in the dataRow.
	--------------
	"""
	def __init__(self, dataRow):
		numericCols = set([2, 3, 4, 7, 24, 5, 8, 12, 13, 15, 18, 22, 23, 25, 26,
						   27])

		# Removes trailing whitespace, escape characters, and non-ASCII chars,
		# and ensures all numerically-parsed cols are non-empty
		def cleanupRowEntry(args):
			i, entry = args
			entry = entry.replace("\xc2\xa0", " ").strip()
			entry = ''.join([i if ord(i) < 128 else '-' for i in entry])
			if i in numericCols and len(dataRow[i]) == 0:
				return "0"
			else:
				return entry

		# Cleanup all data before parsing
		dataRow = map(cleanupRowEntry, enumerate(dataRow))
		self.dataRow = dataRow

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

	"""
	METHOD: str
	----------------
	Parameters: NA

	Returns: A readable string description of this Movie object.
	----------------
	"""
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
	FUNCTION: encode
	-----------------
	Parameters: NA

	Returns: an array representation of this Movie object.  If you pass this as
			a parameter to Movie.decode, the Movie object will be decoded.
	-----------------
	"""
	def encode(self):
		return self.dataRow


"""
CLASS: Actor
-------------
A class representing information about a single actor.  Contains the actor's
name, gender, and race.
-------------
"""
class Actor:

	"""
	CLASS METHOD: decode
	----------------------
	Parameters:
		encoding - the encoding of an Actor object

	Returns: the decoded Actor object
	----------------------
	"""
	@classmethod
	def decode(cls, encoding):
		newObj = cls(encoding[0])

		if encoding[1]:
			newObj.race = encoding[1]
		if encoding[2]:
			newObj.gender = encoding[2]

		return newObj

	"""
	METHOD: init
	-------------
	Parameters: NA

	Returns: a new Actor object with the given name, and no gender or race.
	-------------
	"""
	def __init__(self, name):
		self.name = name
		self.gender = None
		self.race = None

	"""
	METHOD: str
	-------------
	Parameters: NA

	Returns: a readable string description of this Actor object.
	-------------
	"""
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
		print "Fetching race/gender for %s..." % self.name
		name = self.name.split()
		query = "+".join(name)
		url = "http://search.nndb.com/search/?type=unspecified&query=%s" % query
		searchPage = requests.get(url)
		searchTree = html.fromstring(searchPage.content)
		condition = '[contains(.//text(), "%s")' % name[0]
		if len(name) > 1:
			condition += ' and contains(.//text(), "%s")]' % name[1]
		else:
			condition += ']'
		personList = searchTree.xpath('//table')[3].xpath('./tr')
		if len(personList) > 1:
			personList = personList[1].xpath('./td' + condition)
		else:
			personList = None
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
		print "Fetched race/gender for %s... (%s, %s)" % (self.name, self.race, self.gender)

	"""
	METHOD: encode
	----------------
	Parameters: NA

	Returns: an array representation of this Actor object.  If you pass this as
			a parameter to Actor.decode, the Actor object will be decoded.
	----------------
	"""
	def encode(self):
		return [self.name, self.race, self.gender]


"""
FUNCTION: parseMovieFile
-------------------------
Parameters:
	filename - the name of the Kaggle movie data file to parse
	fetchRaceAndGender - whether to fetch each actor's race and gender from NNDB

Returns: a tuple (movieMap, actorMap).  movieMap is a map from a movie
		unique ID to its Movie object.  Note that a movie's unique ID is just
		the concatenation of its title and release year, to avoid conflicts
		between movie remakes with the same name.

		actorMap is a map from an actor name to an Actor object.
-------------------------
"""
def parseMovieFile(filename, fetchRaceAndGender=True):
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
							if fetchRaceAndGender:
								newActor.fetchRaceAndGender()
							actorMap[actorName] = newActor

		return movieMap, actorMap

"""
FUNCTION: createGraphForMovieInfo
-------------------------------
Parameters:
	movieMap - a map containing all the movies to add to the graph.  The map
				should be a map from unique movie IDs to Movie objects.
	actorMap - a map containing all the actors to add to the graph.  The map
				should be a map from actor names to Actor objects.

Returns: a tuple of (graph, movieNodeMap, actorNodeMap, movieInfoMap,
		actorInfoMap).  The graph is a bipartite Snap.PY TUNGraph (undirected
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
def createGraphForMovieInfo(movieMap, actorMap):
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



##### MAIN PROGRAM #####
# Functions you should care about:
#
# createMovieGraph - creates a TUNGraph from movie_metadata.csv and writes out
# all the necessary data components (graph itself, maps, etc.) to file.
#
# readMovieGraphFromFile - reads previously-created graph data component files
# and rehydrates the TUNGraph object and all necessary dictionaries.
#
########################



"""
FUNCTION: createMovieGraph
---------------------------
Parameters: NA

Returns: NA

Creates a movie SNAP graph, and saves it, along with all associated information
dictionaries, to files in the current directory.  Files saved include:

graph-snapgraph.txt - created by SNAP storing all graph edge info
graph-movienodemap.csv - stores movie unique ID -> node ID
graph-actornodemap.csv - stores actor name -> node ID
graph-movieinfomap.csv - stores node ID -> encoded Movie object
graph-actorinfomap.csv - stores node ID -> encoded Actor object

In each, the map keys are row[0] and the values are the rest of the row.
---------------------------
"""
def createMovieGraph():
	movieMap, actorMap = parseMovieFile("movie_metadata.csv",
		fetchRaceAndGender=True)
	graphInfo = createGraphForMovieInfo(movieMap, actorMap)
	graph, movieNodeMap, actorNodeMap, movieInfoMap, actorInfoMap = graphInfo

	# Save to files
	snap.SaveEdgeList(graph, "graph-snapgraph.txt", "Tab-separated edge list")
	saveDictToFile(movieNodeMap, "graph-movienodemap",
		firstRow=["Movie", "NodeID"])
	saveDictToFile(actorNodeMap, "graph-actornodemap",
		firstRow=["Actor", "NodeID"])

	firstRow = ['NodeID', 'color', 'director_name', 'num_critic_for_reviews',
				'duration', 'director_facebook_likes', 'actor_3_facebook_likes',
				'actor_2_name', 'actor_1_facebook_likes', 'gross', 'genres',
				'actor_1_name', 'movie_title', 'num_voted_users',
				'cast_total_facebook_likes', 'actor_3_name',
				'facenumber_in_poster', 'plot_keywords', 'movie_imdb_link',
				'num_user_for_reviews', 'language', 'country', 'content_rating',
				'budget', 'title_year', 'actor_2_facebook_likes', 'imdb_score',
				'aspect_ratio', 'movie_facebook_likes']

	saveDictToFile(movieInfoMap, "graph-movieinfomap", encodeFn=Movie.encode,
		firstRow=firstRow)
	saveDictToFile(actorInfoMap, "graph-actorinfomap", encodeFn=Actor.encode,
		firstRow=["NodeID", "Name", "Race", "Gender"])

"""
FUNCTION: saveDictToFile
-------------------------
Parameters:
	dictToSave - the dict to save to file.
	filename - the name of the file in which to store 'dictToSave'.
	encodeFn - an optional encoding function to call on each dictionary value
				before saving it to file.  MUST return an array.
	firstRow - the first row to output to file, if any (aka a header row)

Returns: NA

Saves the given dictionary as a CSV file with the given filename.
-------------------------
"""
def saveDictToFile(dictToSave, filename, encodeFn=None, firstRow=None):
	with open(filename + '.csv', 'wb') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',')
		if firstRow:
			csvwriter.writerow(firstRow)
		for key in dictToSave:
			value = dictToSave[key]
			if encodeFn:
				row = [key]
				row.extend(encodeFn(value))
				csvwriter.writerow(row)
			else:
				csvwriter.writerow([key, value])

"""
FUNCTION: readMovieGraphFromFile
---------------------------------
Parameters: NA

Returns: a tuple of (graph, movieNodeMap, actorNodeMap, movieInfoMap,
		actorInfoMap), decoded from the given filenames.  The graph is a
		bipartite Snap.PY TUNGraph (undirected graph) where nodes are either
		movies or actors.  An edge indicates that an actor is in a given movie.

		The movieNodeMap is a map from movie unique IDs to their Node ID in the
		graph.

		The actorNodeMap is a map from actor names to their Node ID in the
		graph. 

		The movieInfoMap is a map from Node ID to Movie objects.

		The actorInfoMap is a map from Node ID to Actor objects.
---------------------------------
"""
def readMovieGraphFromFile():
	graph = snap.LoadEdgeList(snap.PUNGraph, "graph-snapgraph.txt", 0, 1)
	movieNodeMap = readDictFromFile("graph-movienodemap.csv", True,
		valueDecodeFn=int)
	actorNodeMap = readDictFromFile("graph-actornodemap.csv", True,
		valueDecodeFn=int)
	movieInfoMap = readDictFromFile("graph-movieinfomap.csv", True,
		keyDecodeFn=int, valueDecodeFn=Movie.decode)
	actorInfoMap = readDictFromFile("graph-actorinfomap.csv", True,
		keyDecodeFn=int, valueDecodeFn=Actor.decode)
	return (graph, movieNodeMap, actorNodeMap, movieInfoMap, actorInfoMap)

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


createMovieGraph()
graphInfo = readMovieGraphFromFile()
graph, movieNodeMap, actorNodeMap, movieInfoMap, actorInfoMap = graphInfo
print "%i nodes in the graph" % graph.GetNodes()
print movieInfoMap[movieNodeMap["Avatar2009"]]
print actorInfoMap[actorNodeMap["Morgan Freeman"]]

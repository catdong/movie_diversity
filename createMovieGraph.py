import csv
import grequests
from lxml import html
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
CLASS: Person
-------------
A class representing information about a single person (actor/director).
Contains the person's name, gender, and race.
-------------
"""
class Person:

	"""
	CLASS METHOD: decode
	----------------------
	Parameters:
		encoding - the encoding of a Person object

	Returns: the decoded Person object
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

	Returns: a new Person object with the given name, and no gender or race.
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

	Returns: a readable string description of this object.
	-------------
	"""
	def __str__(self):
		return "%s, Gender: %s, Race: %s" % (self.name, self.gender, self.race)

	"""
	CLASS METHOD: fetchRaceAndGenderFor
	-----------------------------------
	Parameters:
		people - the array of Person objects to attempt to fetch the race and
				gender for.

	Returns: NA

	Attempts to fetch race/gender info from NNDB for all of the provided Person
	objects.  Fetches information in parallel, and if it finds info for a Person
	it updates their race and gender fields.
	-----------------------------------
	"""
	@classmethod
	def fetchRaceAndGenderFor(cls, people):
		peopleCopy = list(people)

		# Get the search page for each person
		urls = list()
		for person in peopleCopy:
			url = "http://search.nndb.com/search/?type=unspecified&query="
			url += "+".join(person.name.split())
			urls.append(url)
		requests = [grequests.get(url) for url in urls]
		responses = grequests.map(requests)

		# Get the profile pages from each search page
		urls = []
		notFoundIndices = set()
		for i in range(len(responses)):
			response = responses[i]
			if not response:
				notFoundIndices.add(i)
				continue

			name = peopleCopy[i].name.split()
			if len(name) == 0:
				notFoundIndices.add(i)
				continue

			searchTree = html.fromstring(response.content)
			condition = '[contains(.//text(), "%s")' % name[0]
			if len(name) > 1:
				condition += ' and contains(.//text(), "%s")' % name[1]
			condition += ']'

			personList = searchTree.xpath('//table')[3].xpath('./tr')
			if len(personList) <= 1:
				notFoundIndices.add(i)
				continue

			personList = personList[1].xpath('./td' + condition)

			if not personList or len(personList[0].xpath('.//a/@href')) == 0:
				notFoundIndices.add(i)
				continue

			urls.append(personList[0].xpath('.//a/@href')[0])

		# remove the people that we couldn't find info for
		for i in sorted(list(notFoundIndices), reverse=True):
			del peopleCopy[i]

		requests = [grequests.get(url) for url in urls]
		responses = grequests.map(requests)

		# Go through responses and scrape race and gender info
		for i in range(len(responses)):
			response = responses[i]
			person = peopleCopy[i]

			personTree = html.fromstring(response.content)

			raceStr = '//p/b[text()="Race or Ethnicity:"]'
			raceStr += '/following-sibling::text()'
			if len(personTree.xpath(raceStr)) == 0:
				print "%s" % personTree
			else:
				person.race = personTree.xpath(raceStr)[0].strip()

			genderStr = '//p/b[text()="Gender:"]/following-sibling::text()'
			if len(personTree.xpath(genderStr)) == 0:
				print "%s" % personTree
			else:
				person.gender = personTree.xpath(genderStr)[0].strip()

	"""
	METHOD: encode
	----------------
	Parameters: NA

	Returns: an array representation of this object.  If you pass this as
			a parameter to Person.decode, the object will be decoded.
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

Returns: a tuple (movieMap, actorMap, directorMap).  movieMap is a map from a
		movie unique ID to its Movie object.  Note that a movie's unique ID is
		the concatenation of its title and release year, to avoid conflicts
		between movie remakes with the same name.

		actorMap is a map from an actor name to a Person object.

		directorMap is a map from a director name to a Person object.

Reads in the given graph file and stores all its info in the returned graphs.
Also fetches race/gender info for all referenced directors and actors.
-------------------------
"""
def parseMovieFile(filename, fetchRaceAndGender=True):
	with open(filename, 'rb') as csvFile:
		csvFile = csv.reader(csvFile, delimiter=',')
		firstRow = False

		movieMap = {}
		actorMap = {}
		directorMap = {}

		for row in csvFile:
			if not firstRow:
				firstRow = True
			else:
				newMovie = Movie(row)
				if not newMovie.uniqueID() in movieMap:

					# Add the movie
					movieMap[newMovie.uniqueID()] = newMovie

					for actorName in newMovie.actorNames:
						if not actorName in actorMap:
							actorMap[actorName] = Person(actorName)

					# Add the director if needed
					if not newMovie.directorName in directorMap:
						director = Person(newMovie.directorName)
						directorMap[director.name] = director

		if fetchRaceAndGender:
			allPeople = actorMap.values()
			allPeople.extend(directorMap.values())

			FETCH_BLOCK_SIZE = 200

			# Calculate the number of fetches we make
			numFetches = len(allPeople) / FETCH_BLOCK_SIZE
			if len(allPeople) % FETCH_BLOCK_SIZE > 0:
				numFetches += 1

			# Perform each fetch for race/gender info
			for i in range(numFetches):
				startIndex = i*FETCH_BLOCK_SIZE
				endIndex = min((i+1)*FETCH_BLOCK_SIZE, len(allPeople))
				Person.fetchRaceAndGenderFor(allPeople[startIndex : endIndex])
				print "Fetched %i of %i" % (endIndex, len(allPeople))

		return movieMap, actorMap, directorMap

"""
FUNCTION: createGraphForMovieInfo
-------------------------------
Parameters:
	movieMap - a map containing all the movies to add to the graph.  The map
				should be a map from unique movie IDs to Movie objects.
	actorMap - a map containing all the actors to add to the graph.  The map
				should be a map from actor names to Person objects.
	directorMap - a map containing all the directors to add to the graph.  The
				map should be a map from director names to Person objects.

Returns: a tuple of (graph, movieNodeMap, actorNodeMap, directorNodeMap,
		movieInfoMap, actorInfoMap, directorInfoMap).  The graph is a tripartite
		Snap.PY TUNGraph (undirected graph) where nodes are either movies,
		actors or directors.  An edge indicates a relationship (either actor or
		director) to a movie.

		The movieNodeMap is a map from movie unique IDs to their Node ID in the
		graph.

		The actorNodeMap is a map from actor names to their Node ID in the
		graph. 

		The directorNodeMap is a map from director names to their Node ID in the
		graph.

		The movieInfoMap is a map from Node ID to Movie objects.

		The actorInfoMap is a map from Node ID to Person objects.

		The directorInfoMap is a map from Node ID to Person objects.
-------------------------------
"""		
def createGraphForMovieInfo(movieMap, actorMap, directorMap):
	movieGraph = snap.TUNGraph.New()
	movieNodeMap = {}
	actorNodeMap = {}
	movieInfoMap = {}
	actorInfoMap = {}
	directorNodeMap = {}
	directorInfoMap = {}

	for movieID in movieMap:
		movie = movieMap[movieID]
		addMovieToGraph(movieGraph, movieNodeMap, movieInfoMap, movie)

		movieNodeID = movieNodeMap[movieID]
		actors = [actorMap[name] for name in movie.actorNames]
		addActorsToGraph(movieGraph, actorNodeMap, actorInfoMap, actors,
			movieNodeID)
		addDirectorToGraph(movieGraph, directorNodeMap, directorInfoMap, 
			directorMap[movie.directorName], movieNodeID)

	return (movieGraph, movieNodeMap, actorNodeMap, directorNodeMap,
		movieInfoMap, actorInfoMap, directorInfoMap)

"""
FUNCTION: addMovieToGraph
--------------------------
Parameters:
	graph - the graph to add the movie to.
	movieNodeMap - the map of movie unique IDs to graph Node IDs.  Updates this
					map to add info about the newly-added movie.
	movieInfoMap - the map of Node IDs to Movie objects.  Updates this map to
					add info about the newly-added movie.
	movie - the Movie object to add to the graph

Returns: NA

Adds the given movie info to the given graph.  Updates the movie node map to add
info about the new movie's node in the graph.

Node IDs are added contiguously to the graph starting at 0.
--------------------------
"""
def addMovieToGraph(graph, movieNodeMap, movieInfoMap, movie):
	nextNodeID = graph.GetNodes()
	graph.AddNode(nextNodeID)
	movieNodeMap[movie.uniqueID()] = nextNodeID
	movieInfoMap[nextNodeID] = movie

"""
FUNCTION: addActorsToGraph
--------------------------
Parameters:
	graph - the graph to add the movie to.
	actorNodeMap - the map of actor names to graph Node IDs.  Updates this
					map if needed to add info about the newly-added actors.
	actorInfoMap - the map of Node IDs to Person objects.  Updates this map if
					needed to add info about the newly-added actors.
	actors - the Person objects to add to the graph
	movieNodeID - the Node ID of the movie to connect to these actors

Returns: NA

Adds the given actors to the graph with edges to their movie, and updates the
data maps.  Note that nodes might not be added, and the maps might not be
updated, if the actor was already added.

Node IDs are added contiguously to the graph starting at 0.
--------------------------
"""
def addActorsToGraph(graph, actorNodeMap, actorInfoMap, actors, movieNodeID):
	# Add nodes for the main actors if needed, plus edges
	for actor in actors:
		if not actor.name in actorNodeMap:
			nextNodeID = graph.GetNodes()
			graph.AddNode(nextNodeID)
			actorNodeMap[actor.name] = nextNodeID
			actorInfoMap[nextNodeID] = actor

		graph.AddEdge(movieNodeID, actorNodeMap[actor.name])

"""
FUNCTION addDirectorToGraph
----------------------------
Parameters:
	graph - the graph to add the movie to.
	directorNodeMap - the map of director names to graph Node IDs.  Updates
					this map if needed to add info about the new director.
	directorInfoMap - the map of Node IDs to Person objects.  Updates this map
					if needed to add info about the newly-added director.
	director - the Person object to add to the graph
	movieNodeID - the Node ID of the movie to connect to this director

Returns: NA

Adds the given director to the graph with an edge to their movie, and updates
the data maps.  Note that a node might not be added, and the maps might not be
updated, if the director was already added.

Node IDs are added contiguously to the graph starting at 0.
----------------------------
"""
def addDirectorToGraph(graph, directorNodeMap, directorInfoMap, director,
	movieNodeID):

	# Add node for the director if needed, plus edge
	if not director.name in directorNodeMap:
		nextNodeID = graph.GetNodes()
		graph.AddNode(nextNodeID)
		directorNodeMap[director.name] = nextNodeID
		directorInfoMap[nextNodeID] = director

	graph.AddEdge(movieNodeID, directorNodeMap[director.name])



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
graph-directornodemap.csv - stores director name -> node ID
graph-movieinfomap.csv - stores node ID -> encoded Movie object
graph-actorinfomap.csv - stores node ID -> encoded Person object
graph-directorinfomap.csv - stores node ID -> encoded Person object

In each, the map keys are row[0] and the values are the rest of the row.
---------------------------
"""
def createMovieGraph():
	movieMap, actorMap, directorMap = parseMovieFile("movie_metadata.csv",
		fetchRaceAndGender=True)
	graphInfo = createGraphForMovieInfo(movieMap, actorMap, directorMap)
	(graph, movieNodeMap, actorNodeMap, directorNodeMap, movieInfoMap,
		actorInfoMap, directorInfoMap) = graphInfo

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

	saveDictToFile(directorNodeMap, "graph-directornodemap",
		firstRow=["Director", "NodeID"])
	saveDictToFile(movieInfoMap, "graph-movieinfomap", encodeFn=Movie.encode,
		firstRow=firstRow)
	saveDictToFile(actorInfoMap, "graph-actorinfomap", encodeFn=Person.encode,
		firstRow=["NodeID", "Name", "Race", "Gender"])
	saveDictToFile(directorInfoMap, "graph-directorinfomap",
		encodeFn=Person.encode, firstRow=["NodeID", "Name", "Race", "Gender"])

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

Returns: a tuple of (graph, movieNodeMap, actorNodeMap, directorNodeMap,
		movieInfoMap, actorInfoMap, directorInfoMap), decoded from file.  The
		graph is a tripartite Snap.PY TUNGraph (undirected graph) where nodes
		are movies, actors or directors.  An edge indicates that a person was
		involved (either actor or director) with a given movie.

		The movieNodeMap is a map from movie unique IDs to their Node ID in the
		graph.

		The actorNodeMap is a map from actor names to their Node ID in the
		graph. 

		The directorNodeMap is a map from director names to their Node ID in the
		graph.

		The movieInfoMap is a map from Node ID to Movie objects.

		The actorInfoMap is a map from Node ID to Person objects.

		The directorInfoMap is a map from Node ID to Person objects.
---------------------------------
"""
def readMovieGraphFromFile():
	graph = snap.LoadEdgeList(snap.PUNGraph, "graph-snapgraph.txt", 0, 1)
	movieNodeMap = readDictFromFile("graph-movienodemap.csv", True,
		valueDecodeFn=int)
	actorNodeMap = readDictFromFile("graph-actornodemap.csv", True,
		valueDecodeFn=int)
	directorNodeMap = readDictFromFile("graph-directornodemap.csv", True,
		valueDecodeFn=int)
	movieInfoMap = readDictFromFile("graph-movieinfomap.csv", True,
		keyDecodeFn=int, valueDecodeFn=Movie.decode)
	actorInfoMap = readDictFromFile("graph-actorinfomap.csv", True,
		keyDecodeFn=int, valueDecodeFn=Person.decode)
	directorInfoMap = readDictFromFile("graph-directorinfomap.csv", True,
		keyDecodeFn=int, valueDecodeFn=Person.decode)

	return (graph, movieNodeMap, actorNodeMap, directorNodeMap, movieInfoMap,
		actorInfoMap, directorInfoMap)

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


# Should be 4919 Movies, 6255 Actors, 2399 Directors
debug = False
if debug:
	createMovieGraph()
	graphInfo = readMovieGraphFromFile()
	(graph, movieNodeMap, actorNodeMap, directorNodeMap, movieInfoMap,
		actorInfoMap, directorInfoMap) = graphInfo
	print "%i nodes in the graph" % graph.GetNodes()
	print "%i movies, %i actors, %i directors" % (len(movieNodeMap),
		len(actorNodeMap), len(directorNodeMap))

	print movieInfoMap[movieNodeMap["Avatar2009"]]
	print actorInfoMap[actorNodeMap["Morgan Freeman"]]
	print directorInfoMap[directorNodeMap["James Cameron"]]
	print "Brad Pitt was in the following movies:\n"
	for id in graph.GetNI(actorNodeMap["Brad Pitt"]).GetOutEdges():
		print movieInfoMap[id].title

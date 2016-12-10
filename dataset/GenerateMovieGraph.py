import csv
from GraphConstants import NodeTypeActor, NodeTypeDirector, NodeTypeMovie
from GraphConstants import NodeTypeActorDirector, datasetFilename
from GraphConstants import graphFilename, graphDictFilename
import grequests
from lxml import html
import networkx as nx
import sexmachine.detector as gender
import unicodedata
import utils

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
			entry = entry.decode('unicode-escape')
			entry = unicodedata.normalize('NFKD', entry).encode('ascii', 'ignore')
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
	METHOD: toDict
	----------------
	Parameters: NA

	Returns: A dictionary representation of this movie, with key/value pairs for
	every stored piece of information.
	----------------
	"""
	def toDict(self):
		movieDict = {}
		movieDict["inColor"] = self.inColor
		movieDict["directorName"] = self.directorName
		movieDict["numReviewCritics"] = self.numReviewCritics
		movieDict["durationMinutes"] = self.durationMinutes
		movieDict["directorFacebookLikes"] = self.directorFacebookLikes
		movieDict["actorNames"] = self.actorNames
		movieDict["actorsFacebookLikes"] = self.actorsFacebookLikes
		movieDict["gross"] = self.gross
		movieDict["genres"] = self.genres
		movieDict["title"] = self.title
		movieDict["numVotingUsers"] = self.numVotingUsers
		movieDict["castFacebookLikes"] = self.castFacebookLikes
		movieDict["numPosterFaces"] = self.numPosterFaces
		movieDict["plotKeywords"] = self.plotKeywords
		movieDict["imdbURL"] = self.imdbURL
		movieDict["numReviewUsers"] = self.numReviewUsers
		movieDict["language"] = self.language
		movieDict["country"] = self.country
		movieDict["contentRating"] = self.contentRating
		movieDict["budget"] = self.budget
		movieDict["releaseYear"] = self.releaseYear
		movieDict["imdbScore"] = self.imdbScore
		movieDict["aspectRatio"] = self.aspectRatio
		movieDict["movieFacebookLikes"] = self.movieFacebookLikes
		return movieDict

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
CLASS: Person
-------------
A class representing information about a single person (actor/director).
Contains the person's name, gender, and race.
-------------
"""
class Person:

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
	METHOD: toDict
	----------------
	Parameters: NA

	Returns: A dictionary representation of this movie, with key/value pairs for
	every stored piece of information.
	----------------
	"""
	def toDict(self):
		personDict = {}
		personDict["name"] = self.name
		personDict["gender"] = self.gender
		personDict["race"] = self.race
		return personDict

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
				if newMovie.country != 'USA':
					continue

				if not newMovie.uniqueID() in movieMap:
					# Add the movie
					movieMap[newMovie.uniqueID()] = newMovie

					# Get additional actors from IMDB
					cast = utils.getCast(newMovie.imdbURL, newMovie.actorNames)
					newMovie.actorNames = cast

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

Returns: a tuple of (graph, graphDict).  The graph is a tripartite NetworkX
		directed graph where nodes are either movies, actors or directors.
		An edge indicates a relationship (either actor or director or both)
		to a movie. Edges go from directors to movies and from movies to actors.

		The graphDict is a map from movie, actor and director names to their
		NodeIDs in the graph.  Note that while the keys for actors and directors
		are their names (e.g. "Tom Hanks"), the keys for movies are the
		concatenation of their title and release year (e.g. "Avatar2009") so
		that movie remakes are uniquely keyed.
-------------------------------
"""		
def createGraphForMovieInfo(movieMap, actorMap, directorMap):
	graph = nx.DiGraph()
	graphDict = {}

	for movieID in movieMap:
		movie = movieMap[movieID]
		addMovieToGraph(graph, graphDict, movie)

		movieNodeID = graphDict[movieID]
		actors = [actorMap[name] for name in movie.actorNames]
		addActorsToGraph(graph, graphDict, actors, movieNodeID)
		addDirectorToGraph(graph, graphDict, directorMap[movie.directorName],
			movieNodeID)

	return graph, graphDict

"""
FUNCTION: addMovieToGraph
--------------------------
Parameters:
	graph - the graph to add the movie to.
	graphDict - the map of movie, actor and director names to graph Node IDs.
				Updates this map to add info about the newly-added movie.
	movie - the Movie object to add to the graph

Returns: NA

Adds the given movie info to the given graph by making a new node and adding the
movie metadata to that node.  Updates the graphDict to add a mapping from this
movie's unique ID to its Node ID.

Node IDs are added contiguously to the graph starting at 0.
--------------------------
"""
def addMovieToGraph(graph, graphDict, movie):
	nextNodeID = graph.number_of_nodes()
	graph.add_node(nextNodeID, type="MOVIE")
	movieDict = movie.toDict()
	for key in movieDict:
		graph.node[nextNodeID][key] = movieDict[key]

	graphDict[movie.uniqueID()] = nextNodeID
	

"""
FUNCTION: addActorsToGraph
--------------------------
Parameters:
	graph - the graph to add the movie to.
	graphDict - the map of movie, actor and director names to graph Node IDs.
				Updates this map to add info about new actors.
	actors - the Person objects to add to the graph
	movieNodeID - the Node ID of the movie to connect to these actors

Returns: NA

Adds the given actors to the graph with edges from their movie, and updates the
graphDict to record the new actors' node IDs.  Note that nodes might not be
added, and the map might not be updated, if the actor was already added,
*either as an actor or as a director*. Also adds Person metadata to any new
nodes (or updates it if an actor is also a director).

Node IDs are added contiguously to the graph starting at 0.
--------------------------
"""
def addActorsToGraph(graph, graphDict, actors, movieNodeID):
	for actor in actors:
		# If we've never seen this actor before, add it to our graph
		if not actor.name in graphDict:
			nextNodeID = graph.number_of_nodes()
			graph.add_node(nextNodeID, type=NodeTypeActor)
			actorDict = actor.toDict()
			for key in actorDict:
				graph.node[nextNodeID][key] = actorDict[key]

			graphDict[actor.name] = nextNodeID

		# Otherwise, if we've seen this person before as a DIRECTOR, change its
		# type to both actor & director
		elif graph.node[graphDict[actor.name]]["type"] == NodeTypeDirector:
			graph.node[graphDict[actor.name]]["type"] = NodeTypeActorDirector

		# Add an edge from the movie to this actor
		graph.add_edge(movieNodeID, graphDict[actor.name])

"""
FUNCTION: addDirectorToGraph
--------------------------
Parameters:
	graph - the graph to add the movie to.
	graphDict - the map of movie, actor and director names to graph Node IDs.
				Updates this map to add info about the director, if needed.
	director - the Person object to add to the graph
	movieNodeID - the Node ID of the movie to connect to this director

Returns: NA

Adds the given director to the graph with an edge to their movie, and updates
the graphDict to record their node ID.  Note that a node might not be added,
and the map might not be updated, if the director was already added, *either as
an actor or director*.  Also adds Person metadata to any new node (or updates it
if a director is also an actor).

Node IDs are added contiguously to the graph starting at 0.
--------------------------
"""
def addDirectorToGraph(graph, graphDict, director, movieNodeID):
	# If we've never seen this director before, add it to our graph
	if not director.name in graphDict:
		nextNodeID = graph.number_of_nodes()
		graph.add_node(nextNodeID, type=NodeTypeDirector)
		directorDict = director.toDict()
		for key in directorDict:
			graph.node[nextNodeID][key] = directorDict[key]

		graphDict[director.name] = nextNodeID

	# Otherwise, if we've seen this person before as an ACTOR, change its type
	# to both actor & director
	elif graph.node[graphDict[director.name]]["type"] == NodeTypeActor:
		graph.node[graphDict[director.name]]["type"] = NodeTypeActorDirector

	# Add an edge from the director to this movie
	graph.add_edge(graphDict[director.name], movieNodeID)

"""
FUNCTION: createMovieGraph
---------------------------
Parameters: NA

Returns: NA

Creates a movie NetworkX graph and saves it to file, along with a map from
actor, director and movie names to node IDs in that graph.  Uses SexMachine to
fill in as many unknown person genders as it can, after fetching gender/race
info from the web.  Files saved include:

graph file - created by NetworkX storing all nodes + edges and metadata
graph dict csv file - stores actor, director and movie names -> node ID (NOTE:
	in this file, the map keys are row[0] and the values are row[1])
---------------------------
"""
def createMovieGraph():
	movieMap, actorMap, directorMap = parseMovieFile(datasetFilename,
		fetchRaceAndGender=False)
	graph, graphDict = createGraphForMovieInfo(movieMap, actorMap, directorMap)

	# Fill in unknown genders with SexMachine
	genderDetector = gender.Detector(unknown_value=None)

	for nodeId in graph.nodes():
		node = graph.node[nodeId]
		nodeType = node["type"]
		if nodeType != "MOVIE" and not node["gender"] and node["name"] != "":

			firstName = graph.node[nodeId]["name"].split()[0]
			predictedGender = genderDetector.get_gender(firstName)

			# Fill in only genders we're certain about
			if predictedGender == "male" or predictedGender == "female":
				node["gender"] = predictedGender.capitalize()

	# Save to files
	nx.write_gpickle(graph, graphFilename)
	saveDictToFile(graphDict, graphDictFilename, firstRow=["Name", "NodeID"])

"""
FUNCTION: saveDictToFile
-------------------------
Parameters:
	dictToSave - the dict to save to file.
	filename - the name of the file in which to store 'dictToSave' (MUST BE CSV)
	firstRow - the first row to output to file, if any (aka a header row).
				Defaults to nothing.

Returns: NA

Saves the given dictionary as the given CSV filename.
-------------------------
"""
def saveDictToFile(dictToSave, filename, firstRow=None):
	with open(filename, 'wb') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',')
		if firstRow:
			csvwriter.writerow(firstRow)
		for key in dictToSave:
			value = dictToSave[key]
			csvwriter.writerow([key, value])


if __name__ == "__main__":
	createMovieGraph()
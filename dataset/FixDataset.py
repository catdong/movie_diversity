import csv
from GenerateMovieGraph import Person
from ReadMovieGraph import readMovieGraphFromFile
import sexmachine.detector as gender
from GraphConstants import graphFilename
import progressbar
import networkx as nx

def countWithoutGender(g):
	noneCount = 0
	personCount = 0
	for nodeId in g.nodes():
		if g.node[nodeId]["type"] != "MOVIE":
			personCount += 1
			if g.node[nodeId]["gender"] == None:
				noneCount += 1

	print "People without genders: %i" % noneCount
	print "Total people: %i" % personCount




graph, graphDict = readMovieGraphFromFile()
allPeople = list()

for nodeId in graph.nodes():
	node = graph.node[nodeId]
	if node["type"] == "MOVIE": continue

	allPeople.append(Person(node["name"]))

	node["gender"] = None
	node["race"] = None


FETCH_BLOCK_SIZE = 200

# Calculate the number of fetches we make
numFetches = len(allPeople) / FETCH_BLOCK_SIZE
if len(allPeople) % FETCH_BLOCK_SIZE > 0:
	numFetches += 1

# Perform each fetch for race/gender info
bar = progressbar.ProgressBar()
for i in bar(range(numFetches)):
	startIndex = i*FETCH_BLOCK_SIZE
	endIndex = min((i+1)*FETCH_BLOCK_SIZE, len(allPeople))
	fetchBlock = allPeople[startIndex : endIndex]
	Person.fetchRaceAndGenderFor(fetchBlock)
	
# Fill in the new data in our graph
for person in allPeople:
	graph.node[graphDict[person.name]]["race"] = person.race
	graph.node[graphDict[person.name]]["gender"] = person.gender

countWithoutGender(graph)

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

countWithoutGender(graph)

shouldContinue = raw_input("Save to file? ") == "YES"
if shouldContinue:
	shouldContinue = raw_input("Are you sure? ") == "YES"
	if shouldContinue:
		nx.write_gpickle(graph, graphFilename)





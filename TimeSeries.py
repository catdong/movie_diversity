from collections import Counter
from SexMachineGraph import generateSexMachineGraph


graph, graphDict = generateSexMachineGraph()

timeSeriesDict = {}
timeSeriesDict["1910s"] = Counter()
timeSeriesDict["1920s"] = Counter()
timeSeriesDict["1930s"] = Counter()
timeSeriesDict["1940s"] = Counter()
timeSeriesDict["1950s"] = Counter()
timeSeriesDict["1960s"] = Counter()
timeSeriesDict["1970s"] = Counter()
timeSeriesDict["1980s"] = Counter()
timeSeriesDict["1990s"] = Counter()
timeSeriesDict["2000s"] = Counter()
timeSeriesDict["2005s"] = Counter()
timeSeriesDict["2010s"] = Counter()
timeSeriesDict["2015s"] = Counter()

def addMovie(movieNode, key):
	actors = [graph.node[graphDict[actorName]] for actorName in movieNode["actorNames"]]
	for actor in actors:
		if actor["gender"] != None:
			timeSeriesDict[key][actor["gender"]] += 1

movieNodes = [graph.node[nodeId] for nodeId in graph.nodes() if graph.node[nodeId]["type"] == "MOVIE"]
for node in movieNodes:
	if node["releaseYear"] < 1920:
		addMovie(node, "1910s")
	elif node["releaseYear"] < 1930:
		addMovie(node, "1920s")
	elif node["releaseYear"] < 1940:
		addMovie(node, "1930s")
	elif node["releaseYear"] < 1950:
		addMovie(node, "1940s")
	elif node["releaseYear"] < 1960:
		addMovie(node, "1950s")
	elif node["releaseYear"] < 1970:
		addMovie(node, "1960s")
	elif node["releaseYear"] < 1980:
		addMovie(node, "1970s")
	elif node["releaseYear"] < 1990:
		addMovie(node, "1980s")
	elif node["releaseYear"] < 2000:
		addMovie(node, "1990s")
	elif node["releaseYear"] < 2005:
		addMovie(node, "2000s")
	elif node["releaseYear"] < 2010:
		addMovie(node, "2005s")
	elif node["releaseYear"] < 2015:
		addMovie(node, "2010s")
	else:
		addMovie(node, "2015s")

# Print results
print timeSeriesDict["1910s"]
print timeSeriesDict["1920s"]
print timeSeriesDict["1930s"]
print timeSeriesDict["1940s"]
print timeSeriesDict["1950s"]
print timeSeriesDict["1960s"]
print timeSeriesDict["1970s"]
print timeSeriesDict["1980s"]
print timeSeriesDict["1990s"]
print timeSeriesDict["2000s"]
print timeSeriesDict["2005s"]
print timeSeriesDict["2010s"]
print timeSeriesDict["2015s"]


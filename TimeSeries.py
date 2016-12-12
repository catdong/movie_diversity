from Analysis import filterNoneActors
from collections import defaultdict
from dataset import ReadMovieGraph
from graphFunctions import avgDirectorGenderDiversityScore as dGDiv
from graphFunctions import avgDirectorRacialDiversityScore as dRDiv
from graphFunctions import avgMovieGenderDiversityScore as mGDiv
from graphFunctions import avgMovieRacialDiversityScore as mRDiv
from matplotlib import pyplot
import networkx as nx

"""
FUNCTION: timeSeries
---------------------
Parameters:
	graph - the NetworkX DiGraph to do the time series on
	timeSeriesFunc - a function that should take the current state of the graph
					at a given period in time, along with the movie nodeIDs that
					were added since the last time step, and return the y value
					to graph for that time step.
	title - the title of the graph
	yLabel - the label for the y axis
	legendLabels - an array of labels for each plot
"""
def timeSeries(graph, timeSeriesFunc, title, yLabel, legendLabels):

	# Categorize movie nodes by release year
	movieBuckets = defaultdict(list)
	for nodeId in graph.nodes():
		node = graph.node[nodeId]
		if node["type"] == "MOVIE":
			movieBuckets[node["releaseYear"]].append(nodeId)

	# Get a sorted list of all the years for which we have movies
	years = movieBuckets.keys()
	years.sort()
	
	yValues = [[] for i in legendLabels] if legendLabels else [[]]

	# Step through each year and build up our graph and data over time
	timeSeriesGraph = nx.DiGraph()
	for year in years:
		timeSeriesGraph = generateNextTimeStep(timeSeriesGraph, graph, 
												movieBuckets[year], year)
		stepYValues = timeSeriesFunc(timeSeriesGraph, movieBuckets[year])
		for i, y in enumerate(stepYValues):
			yValues[i].append(y)

	for i, ys in enumerate(yValues):
		pyplot.plot(years, ys, label=legendLabels[i] if legendLabels else "")
	pyplot.xlabel("Year")
	pyplot.ylabel(yLabel)
	pyplot.title(title)
	pyplot.legend()
	pyplot.axis([years[0], years[-1], -1 if min(yValues) < 0 else 0, 1])
	pyplot.show()

"""
FUNCTION: generateNextTimeStep
------------------------------
Parameters:
	timeSeriesGraph - the current iteration of the time series graph to build on
	graph - the complete graph
	releasedMovieIds - the movies released during this time step
	year - the year for which we should add nodes from graph to timeSeriesGraph

Returns: the timeSeriesGraph updated to include all nodes/edges up to and
including the given year.  Assumes that timeSeriesGraph has all nodes/edges up
to but *not including* the given year.
------------------------------
"""
def generateNextTimeStep(timeSeriesGraph, graph, releasedMovieIds, year):
	for movieId in releasedMovieIds:
		directorId = graph.predecessors(movieId)[0]

		timeSeriesGraph.add_node(movieId)
		timeSeriesGraph.node[movieId] = graph.node[movieId]

		timeSeriesGraph.add_node(directorId)
		timeSeriesGraph.node[directorId] = graph.node[directorId]

		timeSeriesGraph.add_edge(directorId, movieId)

		# Add all actors in that movie
		for actorId in graph.successors(movieId):
			timeSeriesGraph.add_node(actorId)
			timeSeriesGraph.node[actorId] = graph.node[actorId]
			timeSeriesGraph.add_edge(movieId, actorId)

	return timeSeriesGraph

"""
FUNCTION: filterGraph
-----------------------
Parameters:
	graph - the graph to filter
	graphDict - a dict from names -> node ids for the given graph

Returns: (graph, graphDict) cleaned up by removing all actors without
race/gender info, and any movies that have not been released yet or that were
released before 1980.
-----------------------
"""
def filterGraph(graph, graphDict):
	graph, graphDict = filterNoneActors(graph, graphDict)

	# Remove all movies yet to be released
	for nodeId in graph.nodes():
		node = graph.node[nodeId]
		if node['type'] == 'MOVIE' and node['releaseYear'] < 1980:
			graphDict.pop("%s%i" % (node["title"], node["releaseYear"]), None)
			graph.remove_node(nodeId)

	# Remove all people no longer involved in any movies
	for nodeId in graph.nodes():
		node = graph.node[nodeId]
		if node['type'] != 'MOVIE' and graph.degree(nodeId) == 0:
			graphDict.pop(node["name"], None)
			graph.remove_node(nodeId)

	return graph, graphDict

"""
FUNCTION: graphTimeSeries
--------------------------
Parameters:
	timeSeriesFunc - the function that generates data points for the time series
						given a graph and list of movies at a time step.
	title - the title of the graph
	yLabel - the y-axis label of the graph
	legendLabels - an array of labels for each plot

Returns: NA

Graphs a time series graph for the movie graph using the given time series
function.
--------------------------
"""
def graphTimeSeries(timeSeriesFunc, title, yLabel, legendLabels=None):
	graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()
	graph, graphDict = filterGraph(graph, graphDict)
	g = timeSeries(graph, timeSeriesFunc, title, yLabel, legendLabels)

def combine(graph, graphDict):
	return [dGDiv(graph, graphDict), dRDiv(graph, graphDict),
			mGDiv(graph, graphDict), mRDiv(graph, graphDict)]

if __name__ == "__main__":
	graphTimeSeries(combine, "Hollywood Diversity Over Time", "Diversity Score",
					["Director gender", "Director racial", "Movie gender", "Movie racial"])
	#graphTimeSeries(dGDiv, "Director Gender Diversity Score", "Gender Diversity Score")
	#graphTimeSeries(dRDiv, "Director Racial Diversity Score", "Racial Diversity Score")
	#graphTimeSeries(mGDiv, "Movie Gender Diversity Score", "Gender Diversity Score")
	#graphTimeSeries(mRDiv, "Movie Racial Diversity Score", "Racial Diversity Score")



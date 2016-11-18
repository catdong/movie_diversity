import ReadMovieGraph
import sexmachine.detector as gender

"""
FUNCTION: generateSexMachineGraph
----------------------------------
Parameters: NA

Returns: (graph, graphDict) tuple with an updated NetworkX graph where the
SexMachine module fills in as many unknown person genders as it can.  (In tests,
fills in 3804 unknown genders with high certainty).
----------------------------------
"""
def generateSexMachineGraph():
	genderDetector = gender.Detector(unknown_value=None)
	graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()

	# Loop over all people that are missing genders
	for nodeId in graph.nodes():
		node = graph.node[nodeId]
		if node["type"] != "MOVIE" and not node["gender"] and node["name"] != "":

			firstName = graph.node[nodeId]["name"].split()[0]
			predictedGender = genderDetector.get_gender(firstName)

			# Fill in only genders we're certain about
			if predictedGender == "male" or predictedGender == "female":
				node["gender"] = predictedGender.capitalize()

	return graph, graphDict


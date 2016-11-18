

# Actor-Actor Graph


import ReadMovieGraph
import networkx as nx

#Counter({None: 4906, 'White': 3052, 'Black': 282, 
#'Hispanic': 83, 'Multiracial': 60, 'Asian': 50, 
#'Asian/Indian': 39, 'Middle Eastern': 11, 'American Aborigine': 7, 'Other': 2})

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()

actor_nodes = []
white_actor_nodes = []
black_actor_nodes = []
hispanic_actor_nodes = []
multi_actor_nodes = []
asian_actor_nodes = []
indian_actor_nodes = []
meast_actor_nodes = []
aborigine_actor_nodes = []

other_actor_nodes = []

for node in graph.nodes():
	if graph.node[node]["type"] == "ACTOR" or graph.node[node]["type"] == "ACTOR-DIRECTOR":
		actor_nodes.append(node)
		if graph.node[node]["type"]["race"] == "White":
			white_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "Black":
			black_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "Hispanic":
			hispanic_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "Multiracial":
			multi_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "Asian":
			asian_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "Asian/Indian":
			indian_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "Middle Eastern":
			meast_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] == "American Aborigine":
			aborigine_actor_nodes.append(node)
		elif graph.node[node]["type"]["race"] is None or graph.node[node]["type"]["race"] == "Other":
			other_actor_nodes.append(node)

print actor_nodes

print(nx.attribute_assortativity_coefficient(graph,'metadata.race', actor_nodes))






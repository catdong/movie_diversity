import csv
import ReadMovieGraph
import networkx as nx

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()

actor_count = 0

# NODES
with open('nodes.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	writer.writerow(['Id', 'Label', 'Classification'])
	for node in graph.nodes():
		node_type = graph.node[node]["type"]
		if node_type == "ACTOR" or node_type == "ACTOR-DIRECTOR":
			actor_count += 1
		name = ''
		if node_type == "MOVIE":
			name = graph.node[node]["title"]
		else:
			name = graph.node[node]["name"]
		writer.writerow([name, name, node_type])

# EDGES 
with open('edges.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	writer.writerow(['Source', 'Target', 'Weight', 'Type'])
	for edge in graph.edges():
		source = graph.node[edge[0]]
		target = graph.node[edge[1]]
		source_name = ''
		target_name = ''
		if source["type"] == "MOVIE":
			source_name = source["title"]
		else:
			source_name = source["name"]
		if target["type"] == "MOVIE":
			target_name = target["title"]
		else:
			target_name = target["name"]
		if source_name != '' and target_name != '':
			writer.writerow([source_name, target_name, 1, 'Undirected'])

print actor_count


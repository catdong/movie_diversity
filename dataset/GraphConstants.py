# ------ CONSTANTS -------

# NodeType: the different values a node's "type" field can have in the graph.
NodeTypeActor = "ACTOR"
NodeTypeDirector = "DIRECTOR"
NodeTypeMovie = "MOVIE"
NodeTypeActorDirector = "ACTOR-DIRECTOR"

# Filenames
filepath = __file__[0:__file__.rfind("/") + 1]
datasetFilename = filepath + "movie_metadata.csv"
graphFilename = filepath + "graph.gpickle"
graphDictFilename = filepath + "graphdict.csv"
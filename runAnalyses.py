from dataset import ReadMovieGraph
import Analysis as ana
import DiversityScore as ds

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()
graph = ana.getGraphWithoutNones(graph)

# Statistics for the real network
# actorStats = ds.actorStats(graph)
# movieStats = ds.movieStats(graph)
# directorStats = ds.directorStats(graph)
# raceModularity, blackWhiteModularity, genderModularity = ana.actorModularity(graph)
# raceAssorativity, blackWhiteAssorativity, genderAssorativity = ana.actorAssortativity(graph)


# # Movie and actor statistics for the movie-actor null model
# movieActorNullModel = ana.movieActorNullModel(graph)
# movieStats = ds.movieStats(movieActorNullModel)
# raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline = ana.actorModularity(graph)
# raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline = ana.actorAssortativity(graph)

# Statistics for diversity scores

print ds.directorStats(graph)

print ds.movieStats(graph)

print ds.actorStats(graph)
from dataset import ReadMovieGraph
import Analysis as ana
import DiversityScore as ds

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()
graph, graphDict = ana.filterNoneActors(graph)

# Statistics for the real network
actorStats = ds.actorStats(graph)
movieStats = ds.movieStats(graph)
directorStats = ds.directorStats(graph, graph, graphDict)
raceModularity, blackWhiteModularity, genderModularity = ana.actorModularity(graph)
raceAssorativity, blackWhiteAssorativity, genderAssorativity = ana.actorAssortativity(graph)
proportionSameRace, proportionSameGender = ana.actorDirectorAssortativityHeuristic(graph, graph, graphDict)  # TODO: NEED SOMETHING TO COMPARE THIS TO!!

# Movie statistics for the movie-actor null model
movieActorNullModel = ana.movieActorNullModel(graph)
movieStatsBaseline = ds.movieStats(movieActorNullModel)
raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline = ana.actorModularity(movieActorNullModel)
raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline = ana.actorAssortativity(movieActorNullModel)

# Director statistics for the director-movie null model
directorMovieNullModel = ana.directorMovieNullModel(graph)
directorStatsBaseline = ds.directorStats(movieActorNullModel, graph, graphDict)
proportionSameRace, proportionSameGender = ana.actorDirectorAssortativityHeuristic(graph, directorMovieNullModel, graphDict)

# Box office correlation

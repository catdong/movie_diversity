from dataset import ReadMovieGraph
import Analysis as ana
import DiversityScore as ds

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()
# graph = ana.filterNoneActors(graph)

# Statistics for the real network
actorStats = ds.actorStats(graph)
print actorStats
movieStats = ds.movieStats(graph)
print movieStats
directorStats = ds.directorStats(graph)
print directorStats
raceModularity, blackWhiteModularity, genderModularity = ana.actorModularity(graph)
print raceModularity, blackWhiteModularity, genderModularity
raceAssorativity, blackWhiteAssorativity, genderAssorativity = ana.actorAssortativity(graph)
print raceAssorativity, blackWhiteAssorativity, genderAssorativity
proportionSameRace, proportionSameGender = ana.actorDirectorAssortativityHeuristic(graph)  # TODO: NEED SOMETHING TO COMPARE THIS TO!!
print proportionSameRace, proportionSameGender

# Movie statistics for the movie-actor null model
movieActorNullModel = ana.movieActorNullModel(graph)
movieStatsBaseline = ds.movieStats(movieActorNullModel)
print movieStatsBaseline
raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline = ana.actorModularity(movieActorNullModel)
print raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline
raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline = ana.actorAssortativity(movieActorNullModel)
print raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline

# Director statistics for the director-movie null model
directorMovieNullModel = ana.directorMovieNullModel(graph)
directorStatsBaseline = ds.directorStats(movieActorNullModel)
print directorStatsBaseline

# Box office correlation


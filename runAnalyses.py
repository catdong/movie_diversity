from dataset import ReadMovieGraph
import Analysis as ana
import DiversityScore as ds

graph, graphDict = ReadMovieGraph.readMovieGraphFromFile()
graph, graphDict = ana.filterNoneActors(graph, graphDict)

# Statistics for the real network
actorStats = ds.actorStats(graph)
print 'actorStats:', actorStats
print ''
movieStats = ds.movieStats(graph)
print 'movieStats:', movieStats
print ''
directorStats = ds.directorStats(graph, graph, graphDict)
print 'directorStats:', directorStats
print ''
raceModularity, blackWhiteModularity, genderModularity = ana.actorModularity(graph)
print 'raceModularity, blackWhiteModularity, genderModularity:', raceModularity, blackWhiteModularity, genderModularity
print ''
raceAssorativity, blackWhiteAssorativity, genderAssorativity = ana.actorAssortativity(graph)
print 'raceAssorativity, blackWhiteAssorativity, genderAssorativity:', raceAssorativity, blackWhiteAssorativity, genderAssorativity
print ''
proportionSameRace, proportionSameGender = ana.actorDirectorAssortativityHeuristic(graph, graph, graphDict)
print 'proportionSameRace, proportionSameGender:', proportionSameRace, proportionSameGender
print ''

# Movie statistics for the movie-actor null model
movieActorNullModel = ana.movieActorNullModel(graph)
movieStatsBaseline = ds.movieStats(movieActorNullModel)
print 'movieStatsBaseline:', movieStatsBaseline
print ''
raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline = ana.actorModularity(movieActorNullModel)
print 'raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline:', raceModularityBaseline, blackWhiteModularityBaseline, genderModularityBaseline
print ''
raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline = ana.actorAssortativity(movieActorNullModel)
print 'raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline:', raceAssorativityBaseline, blackWhiteAssorativityBaseline, genderAssorativityBaseline
print ''

# Director statistics for the director-movie null model
directorMovieNullModel = ana.directorMovieNullModel(graph)
directorStatsBaseline = ds.directorStats(movieActorNullModel, graph, graphDict)
print 'directorStatsBaseline:', directorStatsBaseline
print ''
proportionSameRace, proportionSameGender = ana.actorDirectorAssortativityHeuristic(graph, directorMovieNullModel, graphDict)
print 'proportionSameRace, proportionSameGender:', proportionSameRace, proportionSameGender
print ''

# Box office correlation
raceCorrelation, genderCorrelation = ana.diversityProfitCorrelation(graph)
print 'raceCorrelation, genderCorrelation:', raceCorrelation, genderCorrelation
print ''
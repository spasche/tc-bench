import pstats
p = pstats.Stats('prof_results')

#p.sort_stats('cumulative').print_stats(50)
p.sort_stats('time').print_stats()


def minimum_spanning_tree(gene_pool):
    # TSP_World.gen_gene_pool()
    #edges and length
    #full_map = (edges, length)


    edges = set(map(frozenset, list(permutations(GA_World.gene_pool, 2))))


    #make a set of all the pairs of points
    permutation_list = list(permutations(GA_World.gene_pool, 2))
    sett = set(map(frozenset, permutation_list))
    # print(sett)
    unfrozen = [list(x) for x in sett]
    print(unfrozen)
    unfrozen.sort(key=lambda x:x[0].id)
    # print(type(unfrozen[0][0].id))
    print(unfrozen)
    # print(unfrozen[0][0])
    # unfrozen_set = [list(x) for x in sett]
    # for x in unfrozen_set:
    #     print(x[0])
    print('=================')
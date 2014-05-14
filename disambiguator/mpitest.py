from mpi4py import MPI
from nltk.corpus import brown
import sys
from graph import Graph,merge_graphs
from nltk.tree import Tree, ParentedTree
from stat_parser import Parser
import cPickle as pickle
import xml.etree.ElementTree as ET

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_ranks = comm.Get_size() - 1 # I don't want to include the master node

corpora_to_load = ['parsed.xml']
for i in range(32):
    if i != 8 and i < 16:
        pass
        #corpora_to_load.append('parsed/parse'+str(i)+'.xml')

###############################################################################
# 
# MASTER NODE
# 
###############################################################################

if rank == 0:
    print "Welcome"
    query = sys.argv[1]

    try:
        trees = pickle.load(open("trees_cache"))
        print "Loaded from cache"
        jobs = [[] for i in range(num_ranks)]
        for j, job in enumerate(jobs):
            comm.send(job, dest=j+1, tag=11)

        for j, job in enumerate(jobs):
            comm.recv(source=j+1, tag=11)

    except:
        print "Loading from files"
        trees = []

        jobs = [corpora_to_load[i::num_ranks] for i in xrange(num_ranks)]

        for j, job in enumerate(jobs):
            comm.send(job, dest=j+1, tag=11)

        for j, job in enumerate(jobs):
            trees.extend(comm.recv(source=j+1, tag=11))

        pickle.dump(trees, open("trees_cache", "w"), pickle.HIGHEST_PROTOCOL)

    relevant_trees = []

    for tree in trees:
        if query in tree.leaves():
            relevant_trees.append(tree)

    print "Found", len(relevant_trees), "relevant sentences"

    for tree in relevant_trees:
        tree = ParentedTree.convert(tree)
    graphs = []
    for tree in relevant_trees:
        g = Graph(query)
        g.update(tree)
        graphs.append(g)
    

    print "Merging graphs"

    num_merges = num_ranks

    while len(graphs) > 1:
        jobs = [graphs[i::num_merges] for i in xrange(num_merges)]
        for j, job in enumerate(jobs):
            comm.send(job, dest=j+1, tag=11)

        new_graph_results = []
        for j, job in enumerate(jobs):
            result = comm.recv(source=j+1, tag=11)
            if result is not None:
                new_graph_results.append(result)

        graphs = new_graph_results

        num_merges /= 2

    graphs[0].print_relatedness_to_target_in_order()

    # print "Drawing graph (fake)"
    # new_graph.draw("new_graph_"+query)
    print "Getting senses"
    print graphs[0].get_senses_greedy()


###############################################################################
# 
# WORKER NODES
# 
###############################################################################

else:
    def depth_parse(cons):
        if cons.find('tok') is not None:
            token = cons.find('tok')
            return ParentedTree(token.get('cat'), [token.get('base')])
        else:
            children = []
            if len(cons.findall('cons')) == 0:
                raise Exception("Failed to parse")

            for child in cons.findall('cons'):
                children.append(depth_parse(child))
            return ParentedTree(cons.get('cat'), children)

    trees = []
    corpora_to_load = comm.recv(source=0, tag=11)
    for corpus in corpora_to_load:
        print "Parsing", corpus
        data = ET.parse(corpus)
        root = data.getroot()

        for sentence in root.findall('sentence'):
            try:
                parsed = depth_parse(sentence)
            except Exception:
                continue

            trees.append(parsed)
    comm.send(trees, dest=0, tag=11)
    del trees

    while True:
        graphs = comm.recv(source=0, tag=11)
        if not graphs:
            comm.send(None, dest=0, tag=11)
            break
        new_graph = merge_graphs(graphs)
        comm.send(new_graph, dest=0, tag=11)
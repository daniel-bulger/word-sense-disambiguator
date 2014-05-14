#!/usr/bin/env python

import pickle
import nltk
import unicodedata
from graph import Graph, merge_graphs
from multiprocessing import Process, Queue, cpu_count
from stat_parser import Parser

try:
    cache = open("token_cache").read()
    sentences = pickle.loads(cache)
    print "Tokens loaded from cache"
except:
    print "Loading corpus"
    data = open("data/extracted.txt").read()
    data = ''.join([i if ord(i) < 128 else '' for i in data])

    print "Tokenizing sentences"
    sentences = nltk.tokenize.sent_tokenize(data)
    open("token_cache", "w").write(pickle.dumps(sentences))

sentences = sentences[:500]

process_count = cpu_count()
# process_count = 1
# sentence_tasks = [sentences[i::process_count] for i in xrange(process_count)]

print "Using %d processes" % (process_count,)

parser = Parser()
parsed = parser.parse("This is a very long sentence.")

def delegate(task_queue, completed_queue):
    graph = Graph()
    parser = Parser()

    while True:
        try:
            sentence = task_queue.get(False)
        except:
            completed_queue.put(graph)
            print "My work here is done"
            return True
        print "Parsing sentence"
        parsed = parser.parse(sentence)
        print "Adding sentence to graph"
        # graph.update(parsed)
        print "Added"

processes = []
finished_graphs = []
task_queue = Queue()
completed_queue = Queue()

for sentence in sentences:
    task_queue.put(sentence)

for i in range(process_count):
    print "Delegating task %d" % (i,)
    process = Process(target=delegate, args=(task_queue, completed_queue))
    process.start()
    processes.append(process)

for i, process in enumerate(processes):
    finished_graphs.append(completed_queue.get())

for i, process in enumerate(processes):
    process.join()
    print "Process %d joined" % (i,)

print "All processes have rejoined"

finished_graph = merge_graphs(finished_graphs)
finished_graph.save()

test_words = (
    'table',
    'book',
    'run',
    'bagel',
    'fork',
    'shoe',
    'terrorism',
    'bomb',
)

for word in test_words:
    print finished_graph.partition('table')

# finished_graph.draw("output.png")
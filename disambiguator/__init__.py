import multiprocessing
from multiprocessing import Process
import nltk
from stat_parser import Parser
from graph import GraphGenerator

print "Loading corpus"
data = open("data/extracted.txt").read()
print "Tokenizing sentences"
sentences = nltk.tokenize.sent_tokenize(data)

thread_count = multiprocessing.cpu_count()
sentence_tasks = [sentences[i::thread_count] for i in xrange(thread_count)]

gg = GraphGenerator()

def delegate(task):
    for sentence in task:
        parser = Parser()
        parsed = parser.parse(sentence)
        gg.update_graph(parsed)

for task in sentence_tasks:
    p = Process(target=delegate, args=(task,))
    p.start()

for task in sentence_tasks:
    p.join()
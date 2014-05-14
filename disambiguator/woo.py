from graph import Graph

graph = Graph()
graph.load()

graph.draw('me.png')

test_words = (
    'set',
)

for word in test_words:
    try:
        print graph.partition(word)
    except:
        print "%s is not a word" % (word,)

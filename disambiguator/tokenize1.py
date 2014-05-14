from nltk import tokenize

data = open("data/extracted.txt").read()
data = ''.join([i if ord(i) < 128 else '' for i in data])

print "Tokenizing sentences"
sentences = tokenize.sent_tokenize(data)
sentences = sentences[:500]
sentences = "\n".join(sentences)
open("tokens", "w").write(sentences)

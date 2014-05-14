import subprocess
import nltk
num_cores = 32

# print "Loading corpus"
# data = open("data/extracted.txt").read()

# print "Tokenizing sentences"
# sentences = nltk.tokenize.sent_tokenize(data)

# jobs = [sentences[i::num_cores] for i in xrange(num_cores)]

for i in range(num_cores):
    # a = open("corpora/corpus"+str(i)+".txt", 'w').write("\n".join(job))
    # a.close()
    subprocess.Popen("../enju-2.4.2/mogura -xml < corpora/corpus"+str(i)+".txt > parsed/parse"+str(i)+".xml", shell=True)


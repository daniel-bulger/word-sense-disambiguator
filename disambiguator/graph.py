import networkx as nx
from nltk.tree import ParentedTree
import matplotlib.pyplot as plt
import thread
import math
import random
from random import choice
WORDS_PER_SENSE = 999 # shhhh
EXPERIMENTALLY_DETERMINED_CONSTANT_NUM_STEPS = 1000
EXPERIMENTALLY_DETERMINED_CONSTANT_TRAVERSAL_THRESHOLD = 1/float(12)

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w
   assert False, "OOOPS"

def get_distance_from_root(node):
	depth = 0
	current = node.parent()
	while(current):
		current = current.parent()
		depth += 1
	return depth
def get_distance(node1,node2):
	distance = 0
	while node1 != node2:
		if node1 == None or node2 == None:
			return -1
		depth1 = get_distance_from_root(node1)
		depth2 = get_distance_from_root(node2)
		if depth1 >= depth2:
			node1 = node1.parent()
			distance += 1
		if depth1 <= depth2:
			node2 = node2.parent()
			distance += 1
	return distance
def get_leaves(ptree):
	leaves = [] 
	for idx, child in enumerate(ptree): 
		if isinstance(child, ParentedTree): 
			leaves.extend(get_leaves(child)) 
		else: 
			leaves.append(ptree) 
	return leaves 
def merge_graphs(graphs):
	new_graph = Graph(graphs[0].target_word)
	for graph in graphs:
		for node in graph.nodes(data=True):
			if not node[0] in new_graph:
				new_graph.add_node(node[0],num=0,pos=node[1]["pos"])
			new_graph.node[node[0]]["num"] += node[1]["num"]
		for edge in graph.edges(data=True):
			e1 = edge[0]
			e2 = edge[1]
			if not (edge[0],edge[1]) in new_graph.edges():
				new_graph.add_edge(edge[0],edge[1],weight=0)
			new_graph.edge[edge[0]][edge[1]]["weight"] += edge[2]["weight"]
	return new_graph

class Graph(nx.Graph):
	def __init__(self,target_word):
		nx.Graph.__init__(self)
		self.cached_relatedness = None
		self.target_word = target_word
		self.add_node(target_word,num=0,is_target=1)

	def invalidate_cache(self):
		self.cached_relatedness = None
	def update(self,syntax_tree):
		ptree = ParentedTree.convert(syntax_tree)
		for leaf in get_leaves(ptree):
			word = leaf[0]
			if not word in self:
				self.add_node(word,num=0,pos=leaf.pos()[0][1])
			self.node[word]["num"] += 1
		central_leaf = None
		for leaf in get_leaves(ptree):
			if leaf[0] == self.target_word:
				central_leaf = leaf
				break
		if not central_leaf:
			print "Error: target word not in sentence"
		for leaf in get_leaves(ptree):
			word = leaf[0]
			if word == self.target_word:
				for other_leaf in get_leaves(ptree):
					other_word = other_leaf[0]
					if word == other_word:
						continue
					if not (word,other_word) in self.edges():
						self.add_edge(word,other_word,weight=0)
					self.edge[word][other_word]["weight"] += 1.0/math.sqrt(get_distance(leaf,other_leaf))
			else:
				for other_leaf in get_leaves(ptree):
					other_word = other_leaf[0]
					if word == other_word:
						continue
					if other_word == self.target_word:
						continue
					if not (word,other_word) in self.edges():
						self.add_edge(word,other_word,weight=0)
					self.edge[word][other_word]["weight"] += 1.0/math.pow(
						get_distance(leaf,other_leaf)*
						get_distance(leaf,central_leaf)*
						get_distance(other_leaf,central_leaf),1/3
						)
		self.invalidate_cache()
	def draw(self,filename = None):
		avg=sum([d["weight"] for (u,v,d) in self.edges(data=True) ])/float(self.number_of_edges())
		elarge=[(u,v) for (u,v,d) in self.edges(data=True) if d['weight'] >avg]
		pos=nx.spring_layout(self) # positions for all nodes
		for (u,v,d) in self.edges(data=True):
			nx.draw_networkx_edges(self,pos,edgelist=[(u,v)],width=d["weight"]) 
		nx.draw(self,pos,edgelist=[])  # networkx draw()
		if filename:
			plt.savefig(filename)  # pyplot draw()
		else:
			plt.show()
	def get_median_relatedness(self):
		if self.cached_relatedness != None:
			return self.cached_relatedness
		weights = []
		for edge in self.edges(data=True):
			if edge[0]==self.target_word or edge[1] == self.target_word:
				weights.append(edge[2]["weight"])
		median = 0
		if len(weights) % 2 == 0:
			median = (weights[len(weights)/2]+weights[len(weights)/2 + 1]) / 2.0
		else:
			median = weights[len(weights)/2]
		self.cached_relatedness = median
		return median
	def relatedness_to_target_word(self,word):
		return self.edge[word][self.target_word]["weight"]
	def get_normalization_factor(self,word1,word2):
		return math.sqrt(self.node[word1]["num"]*self.node[word2]["num"])
	def get_senses(self):
		# MaxMax algorithm (http://www.sussex.ac.uk/Users/drh21/78160368.CICLing.2013.preprint.pdf)
		new_graph = nx.DiGraph()
		for node in self.nodes():
			if node == self.target_word:
				continue
			new_graph.add_node(node,is_root=True)
		for node in self.nodes():
			if node == self.target_word:
				continue
			max_weight = 0
			max_neighbor = None
			for neighbor in self.neighbors(node):
				if neighbor == self.target_word:
					continue
				if self.edge[node][neighbor]["weight"]/self.get_normalization_factor(node,neighbor) > max_weight:
					max_weight = self.edge[node][neighbor]["weight"]/self.get_normalization_factor(node,neighbor)
					max_neighbor = neighbor
			if not max_neighbor:
				raise Exception("No neighbors found for "+node)
			new_graph.add_edge(max_neighbor,node)
		for node in new_graph.nodes(data=True):
			if node[1]["is_root"]:
				for descendant in nx.descendants(new_graph,node[0]):
					new_graph.node[descendant]["is_root"] = False
		senses = []
		for node in new_graph.nodes(data=True):
			if node[1]["is_root"]:
				senses.append([node[0]]+list(nx.descendants(new_graph,node[0])))
		for i in range(len(senses)):
			new_sense = []
			most_related = sorted(senses[i],key=self.relatedness_to_target_word,reverse=True)[:WORDS_PER_SENSE-1]

			senses[i] = most_related[:]
			#senses[i] = [word for word in senses[i] if self.node[word]["pos"] == "NN" ]

		return senses
	def get_senses_markov(self):
		current_node = choice(self.nodes())
		new_graph = nx.Graph()
		for i in range(EXPERIMENTALLY_DETERMINED_CONSTANT_NUM_STEPS * len(self.nodes())):
			# do magic
			next_node = weighted_choice([(n,self.edge[n][current_node]["weight"]) for n in self.neighbors(current_node)])
			if not (current_node,next_node) in new_graph.edges():
				new_graph.add_edge(current_node,next_node,weight=0)
			new_graph.edge[current_node][next_node]["weight"] += 1.0
			current_node = next_node
		for edge in new_graph.edges(data=True):
			if edge[2]["weight"] < EXPERIMENTALLY_DETERMINED_CONSTANT_TRAVERSAL_THRESHOLD * len(self.nodes()):
				new_graph.remove_edge(edge[0],edge[1])
		return nx.connected_components(new_graph)


	def save_to_file(self,filename):
		nx.write_gml(self,filename)

	def load_from_file(self,filename):
		self.__dict__.update(nx.read_gml(filename).__dict__)
		target = None
		for node in self.nodes(data=True):
			if "is_target" in node[1]:
				target = node[1]["label"]
				break
		if not target:
			raise Exception("Error: no target word found in graph")
		new_graph = Graph(target)
		for node in self.nodes(data=True):
			new_graph.add_node(str(node[1]["label"]), num=node[1]["num"])

		for edge in self.edges(data=True):
			new_graph.add_edge(str(self.node[edge[0]]["label"]),
							   str(self.node[edge[1]]["label"]),
							   weight=edge[2]["weight"])
		self.__dict__.update(new_graph.__dict__)
		self.target_word = target
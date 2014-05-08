import networkx as nx
from nltk.tree import ParentedTree
import matplotlib.pyplot as plt
import thread
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
	new_graph = Graph()
	for graph in graphs:
		for node in graph.nodes(data=True):
			if not node[0] in new_graph:
				new_graph.add_node(node[0],num=0)
			new_graph.node[node[0]]["num"] += node[1]["num"]
		for edge in graph.edges(data=True):
			e1 = edge[0]
			e2 = edge[1]
			if not (edge[0],edge[1]) in new_graph.edges():
				new_graph.add_edge(edge[0],edge[1],weight=0)
			new_graph.edge[edge[0]][edge[1]]["weight"] += edge[2]["weight"]
	return new_graph

class Graph(nx.Graph):
	def __init__(self):
		nx.Graph.__init__(self)
		self.cached_relatedness = None
		self.normalized = False
	def invalidate_cache(self):
		self.cached_relatedness = None
		self.normalized = False
	def update(self,syntax_tree):
		ptree = ParentedTree.convert(syntax_tree)
		for leaf in get_leaves(ptree):
			word = leaf[0]
			if not word in self:
				self.add_node(word,num=0)
			self.node[word]["num"] += 1
		for leaf in get_leaves(ptree):
			word = leaf[0]
			for other_leaf in get_leaves(ptree):
				other_word = other_leaf[0]
				if word == other_word:
					continue
				if not (word,other_word) in self.edges():
					self.add_edge(word,other_word,weight=0)
				self.edge[word][other_word]["weight"] += 1.0/get_distance(leaf,other_leaf)
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
	def normalize(self):
		if self.normalized:
			return
		for edge in self.edges(data=True):
			edge[2]["normalized_weight"] = edge[2]["weight"]/float(self.node[edge[0]]["num"]+self.node[edge[1]]["num"])
		self.normalized = True
	def ensure_normalized(self):
		if not self.normalized:
			self.normalize()
	def get_median_relatedness(self):
		if self.cached_relatedness != None:
			return self.cached_relatedness
		self.ensure_normalized()
		weights = []
		for edge in self.edges(data=True):
			weights.append(edge[2]["normalized_weight"])
		median = 0
		if len(weights) % 2 == 0:
			median = (weights[len(weights)/2]+weights[len(weights)/2 + 1]) / 2.0
		else:
			median = weights[len(weights)/2]
		self.cached_relatedness = median
		return median

	def _partition_helper(self,senses,central_word):
		# put similar things together
		# for current_sense in senses:
		# 	for word in current_sense:
		# 		for other_sense in senses:
		# 			if current_sense == other_sense:
		# 				continue
		# 			similarity_to_current_sense = 0.0


		# get the appropriate number of senses
		max_closeness = 0
		closeness_indices = (0,0)
		for i,sense1 in enumerate(senses):
			for j,sense2 in enumerate(senses):
				if i == j:
					continue
				closeness_to_center = 0.0
				for word in sense1+sense2:
					closeness_to_center += self.edge[word][central_word]["normalized_weight"]
				closeness_to_center /= float(len(sense1+sense2))
				closeness_to_each_other = 0.0
				for word1 in sense1:
					for word2 in sense2:
						if word2 in self.edge[word1]:
							closeness_to_each_other += self.edge[word1][word2]["normalized_weight"]
				closeness_to_each_other /= float(len(sense1)*len(sense2))
				if closeness_to_each_other > max_closeness:
					max_closeness = closeness_to_each_other
					closeness_indices = (i,j)
		print senses
		if self.get_median_relatedness() < max_closeness:
			new_sense = senses[closeness_indices[1]][:]
			senses[closeness_indices[0]].extend(new_sense)
			senses.pop(closeness_indices[1])
			return self._partition_helper(senses,central_word)
		return senses

	def get_senses(self,central_word):
		self.ensure_normalized()
		senses = [[node] for node in nx.Graph.neighbors(self,central_word) 
			if self.edge[node][central_word]["normalized_weight"] > self.get_median_relatedness()]
		return self._partition_helper(senses,central_word)

	def save_to_file(self,filename):
		nx.write_gml(self,filename)

	def load_from_file(self,filename):
		self.__dict__.update(nx.read_gml(filename).__dict__)

		new_graph = Graph()
		for node in self.nodes(data=True):
			new_graph.add_node(str(node[1]["label"]), num=node[1]["num"])

		for edge in self.edges(data=True):
			new_graph.add_edge(str(self.node[edge[0]]["label"]),
							   str(self.node[edge[1]]["label"]),
							   weight=edge[2]["weight"])
		self.__dict__.update(new_graph.__dict__)
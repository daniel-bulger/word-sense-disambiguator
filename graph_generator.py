import networkx as nx
from nltk.tree import ParentedTree
import matplotlib.pyplot as plt
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


class GraphGenerator:
	def __init__(self):
		self.graph = nx.Graph() # this graph can be added to
		self.finalized_graph = None # this graph can be used for word sense disambiguation
		self.locked = False
	def lock(self):
		while(self.locked):
			pass
		self.locked = True
	def unlock(self):
		self.locked = False
	def update_graph(self,syntax_tree):
		ptree = ParentedTree.convert(syntax_tree)
		for leaf in get_leaves(ptree):
			word = leaf[0]
			self.lock()
			if not word in self.graph:
				self.graph.add_node(word,num=0)
			self.graph.node[word]["num"] += 1
			self.unlock()
		for leaf in get_leaves(ptree):
			word = leaf[0]
			for other_leaf in get_leaves(ptree):
				other_word = other_leaf[0]
				if word == other_word:
					continue
				self.lock()
				if not (word,other_word) in self.graph.edges():
					self.graph.add_edge(word,other_word,weight=0)
				self.graph.edge[word][other_word]["weight"] += 1.0/get_distance(leaf,other_leaf)
				self.unlock()
	def draw_graph(self,filename):
		avg=sum([d["weight"] for (u,v,d) in self.graph.edges(data=True) ])/float(self.graph.number_of_edges())
		elarge=[(u,v) for (u,v,d) in self.graph.edges(data=True) if d['weight'] >avg]
		pos=nx.spring_layout(self.graph) # positions for all nodes
		for (u,v,d) in self.graph.edges(data=True):
			nx.draw_networkx_edges(self.graph,pos,edgelist=[(u,v)],width=d["weight"]) 
		nx.draw(self.graph,pos,edgelist=[])  # networkx draw()
		plt.savefig(filename)  # pyplot draw()
		plt.show()

	def save_graph(self):
		nx.write_gml(self.graph,"similarity_graph.gml")
	def load_graph(self):
		self.graph=nx.read_gml('similarity_graph.gml')
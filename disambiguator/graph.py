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
		self.lock = thread.allocate_lock()
	def update(self,syntax_tree):
		ptree = ParentedTree.convert(syntax_tree)
		for leaf in get_leaves(ptree):
			word = leaf[0]
			self.lock.acquire()
			if not word in self:
				self.add_node(word,num=0)
			self.node[word]["num"] += 1
			self.lock.release()
		for leaf in get_leaves(ptree):
			word = leaf[0]
			for other_leaf in get_leaves(ptree):
				other_word = other_leaf[0]
				if word == other_word:
					continue
				self.lock.acquire()
				if not (word,other_word) in self.edges():
					self.add_edge(word,other_word,weight=0)
				self.edge[word][other_word]["weight"] += 1.0/get_distance(leaf,other_leaf)
				self.lock.release()
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

	def save(self):
		nx.write_gml(self,"similarity_graph.gml")
	def load(self):
		self=nx.read_gml('similarity_graph.gml')
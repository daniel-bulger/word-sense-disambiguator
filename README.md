word-sense-disambiguator
========================

This project explores a new method of finding similarities between words for the purpose of word sense disambiguation (WSD). This method involves determining semantic similarity based on distance in syntax trees as opposed to a naïve word distance. The trees are obtained from an existing syntax tree generator. Once these similarities are determined, we use a quasi-clique method to partition the similarity graph into word sense pools.
	
Given a sentence or textual context and a specific word to be disambiguated, the system returns a list of sense pools, with the most relevant sense pool selected as the predicted meaning.
	
To determine the correctness of our results, we test two metrics: the validity of sense pool differentiation and the ability of the system to predict which sense pool applies to the given context.

![Flow Chart](https://measuring_cups.s3.amazonaws.com/wsd/WSD.png "System Architecture")

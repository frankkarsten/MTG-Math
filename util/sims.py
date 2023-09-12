import random
from util.geom import multivariate_hypgeom

def determine_Keep(deck, keep_fn, handsize = 7, hand = None, _deck=None, Keep_success_prob=0):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	"""
	if None == hand: hand = {}
	if None == _deck: _deck=dict(deck)
	if len(_deck):
		k = list(_deck.keys())[0]
		n = _deck[k]
		del _deck[k]
		if 'Other' == k:
			return determine_Keep(deck, keep_fn, handsize, hand, dict(_deck), Keep_success_prob)
		else:
			for count in range(0, n):
				hand[k]=count
				Keep_success_prob = determine_Keep(deck, keep_fn, handsize, dict(hand), dict(_deck), Keep_success_prob)
	else:
		nother = handsize
		for k in hand:
			nother -= hand[k]
		hand['Other']=nother
		if nother >= 0 and keep_fn(hand):
			Keep_success_prob += multivariate_hypgeom(deck, hand)
	return Keep_success_prob

def simulate_Keep(deck, keep_fn, handsize = 7):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	"""
	num_iterations = 10 ** 4#6
	count_good_hands = 0
	for _ in range(num_iterations):
		decklist = []
		for card in deck.keys():
			decklist += [card] * deck[card]
		random.shuffle(decklist)
		
		hand = {}
		for k in deck.keys(): hand[k] = 0
		
		for _ in range(handsize):
			hand[decklist.pop(0)] += 1
		
		if keep_fn(hand):
			count_good_hands += 1
	return count_good_hands/num_iterations

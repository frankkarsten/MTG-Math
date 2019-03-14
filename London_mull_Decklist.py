import random, sys

deck = {
	'Depths':3,
	'Hexmage':3,
	'Stage':3,
	'Wish':4,
	'Griselbrand':3,
	'Entomb':4,
	'LED':4,
	'Reanimate':8,
	'Discard':6,
	'Other':22
}

def can_keep(hand):
	"""
		Return true if the hand contains one of the two combos
	"""
	return (hand.get('Depths', 0) and hand.get('Stage', 0)) or \
	   (hand.get('Depths', 0) and hand.get('Hexmage', 0)) or \
	   (hand.get('Depths', 0) and hand.get('Wish', 0) and hand.get('LED', 0)) or \
	   (hand.get('Entomb', 0) and hand.get('LED', 0) and hand.get('Griselbrand', 0)) or \
	   (hand.get('Entomb', 0) and hand.get('Reanimate', 0)) or \
	   (hand.get('Griselbrand', 0) and hand.get('Discard', 0) and hand.get('Reanimate', 0)) or \
	   (hand.get('Entomb', 0) and hand.get('LED', 0) and hand.get('Wish', 0)) or \
	   (hand.get('Griselbrand', 0) and hand.get('LED', 0) and hand.get('Wish', 0)) or \
	   (hand.get('LED', 0) >= 2 and hand.get('Wish', 0)) or \
	   (hand.get('Stage', 0) and hand.get('Wish', 0) and hand.get('LED', 0)) or \
	   (hand.get('Hexmage', 0) and hand.get('Wish', 0)) or \
	   (hand.get('Entomb', 0) >= 2 and hand.get('LED', 0)) or \
	   (hand.get('Reanimate', 0) and hand.get('Griselbrand', 0) and hand.get('LED', 0)) 

def binom(n, k):
	"""	
	Parameters:
		n - Number of elements of the entire set
		k - Number of elements in the subset
	It should hold that 0 <= k <= n
	Returns - The binomial coefficient n choose k that represents the number of ways of picking k unordered outcomes from n possibilities
	"""
	answer = 1
	for i in range(1, min(k, n - k) + 1):
		answer = answer * (n + 1 - i) / i
	return int(answer)

def multivariate_hypgeom(deck, needed):
	"""	
	Parameters:
		deck - A dictionary of cardname : number of copies
		needed - A dictionary of cardname : number of copies
	It should hold that the cardname keys of deck and needed are identical
	Returns - the multivariate hypergeometric probability of drawing exactly the cards in 'needed' from 'deck' when drawing without replacement 
	"""
	answer = 1
	sum_deck = 0
	sum_needed = 0
	for card in deck.keys():
		answer *= binom(deck[card], needed.get(card, 0))
		sum_deck += deck[card]
		sum_needed += needed.get(card, 0)
	return answer / binom(sum_deck, sum_needed)

def determine_Combo(_deck, handsize = 7, hand = None, Combo_success_prob=0):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	"""
	if not hand: hand = {}
	if len(_deck):
		k = list(_deck.keys())[0]
		n = _deck[k]
		del _deck[k]
		if 'Other' == k:
			return determine_Combo(dict(_deck), handsize, hand, Combo_success_prob)
		else:
			for count in range(0, n):
				hand[k]=count
				Combo_success_prob = determine_Combo(dict(_deck), handsize, dict(hand), Combo_success_prob)
	else:
		nother = handsize
		for k in hand:
			nother -= hand[k]
		hand['Other']=nother
		if nother >= 0 and can_keep(hand):
			Combo_success_prob += multivariate_hypgeom(deck, hand)
	return Combo_success_prob

def simulate_Combo(handsize = 7):
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
		
		if can_keep(hand):
			count_good_hands += 1
	return count_good_hands/num_iterations

print("Starting calculations")
sys.stdout.flush()

Combo_success = determine_Combo(dict(deck))
Combo_failure = 1 - Combo_success
expected_hand_size = 0
print("\nLondon probability of opening hand guaranteeing an ISZ combo?")
for mulligans in range(4):
	print(f'When willing to mull down to {7 - mulligans}, probability is {(1 - (Combo_failure ** (mulligans + 1))) * 100:.2f}%.')
	if (mulligans < 3): 
		expected_hand_size += (7 - mulligans) * (Combo_failure ** mulligans) * Combo_success
	if (mulligans == 3):
		expected_hand_size += 4 * (Combo_failure ** 3)
print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))
sys.stdout.flush()
print('\nFor verification, simulation shows that the 7-card probability is: ' + str(round(100 * simulate_Combo(), 2))+"%")
sys.stdout.flush()

print("\nVancouver probability of opening hand guaranteeing an ISZ combo?")
Prob_no_Combo_so_far = 1
expected_hand_size = 0
for mulligans in range(4):
	if (mulligans < 3): 
		expected_hand_size += (7 - mulligans) * Prob_no_Combo_so_far * determine_Combo(dict(deck), 7 - mulligans)
	if (mulligans == 3):
		expected_hand_size += 4 * Prob_no_Combo_so_far
	Prob_no_Combo_so_far = Prob_no_Combo_so_far * (1 - determine_Combo(dict(deck), 7 - mulligans))
	print(f'When willing to mull down to {7-mulligans}, probability is {(1 - Prob_no_Combo_so_far) * 100:.2f}%.')
		
print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))

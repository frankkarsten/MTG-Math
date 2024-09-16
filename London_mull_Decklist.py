import random, sys
from util.sims import determine_Keep, simulate_Keep

def LondonVsVancouver(deck, keep_fn):

	print("Starting calculations")
	sys.stdout.flush()

	Keep_success = determine_Keep(deck, keep_fn=keep_fn)
	Keep_failure = 1 - Keep_success
	expected_hand_size = 0
	print("\nLondon probability of opening hand being a keep with the given function?")
	for mulligans in range(4):
		print(f'When willing to mull down to {7 - mulligans}, probability is {(1 - (Keep_failure ** (mulligans + 1))) * 100:.2f}%.')
		if (mulligans < 3): 
			expected_hand_size += (7 - mulligans) * (Keep_failure ** mulligans) * Keep_success
		if (mulligans == 3):
			expected_hand_size += 4 * (Keep_failure ** 3)
	print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))
	sys.stdout.flush()
	print('\nFor verification, simulation shows that the 7-card probability is: ' + str(round(100 * simulate_Keep(deck=deck, keep_fn=keep_fn), 2))+"%")
	sys.stdout.flush()

	print("\nVancouver probability of opening hand being a keep with the given function?")
	Prob_no_keep_so_far = 1
	expected_hand_size = 0
	for mulligans in range(4):
		if (mulligans < 3): 
			expected_hand_size += (7 - mulligans) * Prob_no_keep_so_far * determine_Keep(deck, keep_fn=keep_fn, handsize=7 - mulligans)
		if (mulligans == 3):
			expected_hand_size += 4 * Prob_no_keep_so_far
		Prob_no_keep_so_far = Prob_no_keep_so_far * (1 - determine_Keep(deck, keep_fn=keep_fn, handsize=7 - mulligans))
		print(f'When willing to mull down to {7-mulligans}, probability is {(1 - Prob_no_keep_so_far) * 100:.2f}%.')
			
	print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))


iceStationZebra = {
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

def ISZKeep(hand):
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

tron = {
	'Tower': 4,
	'Plant': 4,
	'Mine': 4,
	'Map': 4,
	'Karn': 8,
	'Chromatic': 8,
	'Scrying': 4,
	'Other': 24
}

def TronKeep(hand):
	NumberTronPieces = min(hand.get('Plant', 0), 1) + min(hand.get('Mine', 0), 1) + min(hand.get('Tower', 0), 1)
	return (hand.get('Karn', 0) and NumberTronPieces >= 3) or \
	   (hand.get('Karn', 0) and hand.get('Map', 0) and NumberTronPieces >=2) or \
	   (hand.get('Scrying', 0) and hand.get('Karn', 0) and hand.get('Chromatic', 0) and NumberTronPieces >= 2) 

LondonVsVancouver(deck=iceStationZebra, keep_fn=ISZKeep)
#LondonVsVancouver(deck=tron, keep_fn=TronKeep)

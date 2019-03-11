import random

deck = {
	'Tower': 4,
	'Plant': 4,
	'Mine': 4,
	'Map': 4,
	'Karn': 8,
	'Chromatic': 8,
	'Scrying': 4,
	'Other': 24
}

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
		answer *= binom(deck[card], needed[card])
		sum_deck += deck[card]
		sum_needed += needed[card]
	return answer / binom(sum_deck, sum_needed)

def determine_T3Karn(handsize = 7):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	Returns - a number that represents the probability of finding an opening hand that guarantees a turn-3 payoff card
	We keep if and only if our hand contains at least:
		- One of each Tron piece and a payoff card,
		- Two Tron pieces, an Expedition Map, and a payoff card,
		- Two Tron pieces, a Chromatic artifacts, a Sylvan Scrying, and a payoff card.
	"""
	Tron_success_prob = 0
	for Tower in [0, 1, 2, 3, 4]:
		for Plant in [0, 1, 2, 3, 4]:
			for Mine in [0, 1, 2, 3, 4]:
				for Map in [0, 1, 2, 3, 4]:
					for Karn in [1, 2, 3, 4]:
						for Chromatic in [0, 1, 2, 3]:
							for Scrying in [0, 1, 2, 3]:
								#Note that a payoff card is guaranteed because we started the list for Karn at 1
								NumberTronPieces = min(Plant, 1) + min(Mine, 1) + min(Tower, 1)
								keep_condition = NumberTronPieces >= 3 or (NumberTronPieces >= 2 and Map >=1) or (NumberTronPieces >= 2 and Chromatic >=1 and Scrying>=1)
								if Tower + Plant + Mine + Map + Karn + Chromatic + Scrying <= handsize and keep_condition:
									needed = {}
									needed['Tower'] = Tower
									needed['Plant'] = Plant
									needed['Mine'] = Mine
									needed['Karn'] = Karn
									needed['Map'] = Map
									needed['Chromatic'] = Chromatic
									needed['Scrying'] = Scrying
									needed['Other'] = handsize - Tower - Plant - Mine - Karn - Map - Chromatic - Scrying
									Tron_success_prob += multivariate_hypgeom(deck, needed)
	return Tron_success_prob

def simulate_T3Karn(handsize = 7):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	Returns - a number that approximates via simulation the probability of finding an opening hand that guarantees a turn-3 payoff card
	We keep if and only if our hand contains at least:
		- One of each Tron piece and a payoff card,
		- Two Tron pieces, an Expedition Map, and a payoff card,
		- Two Tron pieces, a Chromatic artifacts, a Sylvan Scrying, and a payoff card.
	"""
	num_iterations = 10 ** 6
	count_good_hands = 0
	for _ in range(num_iterations):
		decklist = []
		for card in deck.keys():
			decklist += [card] * deck[card]
		random.shuffle(decklist)
		
		hand = {
			'Tower': 0,
			'Plant': 0,
			'Mine': 0,
			'Map': 0,
			'Karn': 0,
			'Chromatic': 0,
			'Scrying': 0,
			'Other': 0
		}
		
		for _ in range(handsize):
			hand[decklist.pop(0)] += 1
		
		NumberTronPieces = min(hand['Plant'], 1) + min(hand['Mine'], 1) + min(hand['Tower'], 1)
		if hand['Karn'] >=1 and (NumberTronPieces >= 3 or (NumberTronPieces >= 2 and hand['Map']>=1) or (NumberTronPieces >= 2 and hand['Chromatic']>=1 and hand['Scrying']>=1)):
			count_good_hands += 1
	return count_good_hands/num_iterations

T3Karn_success = determine_T3Karn()
T3Karn_failure = 1 - T3Karn_success
expected_hand_size = 0
print("London probability of opening hand guaranteeing a turn-3 payoff card?")
for mulligans in range(4):
	print(f'When willing to mull down to {7 - mulligans}, probability is {(1 - (T3Karn_failure ** (mulligans + 1))) * 100:.2f}%.')
	if (mulligans < 3): 
		expected_hand_size += (7 - mulligans) * (T3Karn_failure ** mulligans) * T3Karn_success
	if (mulligans == 3):
		expected_hand_size += 4 * (T3Karn_failure ** 3)
print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))
print('\nFor verification, simulation shows that the 7-card probability is: ' + str(round(100 * simulate_T3Karn(), 2))+"%")

print("\nVancouver probability of opening hand guaranteeing a turn-3 payoff card?")
Prob_no_Tron_so_far = 1
expected_hand_size = 0
for mulligans in range(4):
	if (mulligans < 3): 
		expected_hand_size += (7 - mulligans) * Prob_no_Tron_so_far * determine_T3Karn(7 - mulligans)
	if (mulligans == 3):
		expected_hand_size += 4 * Prob_no_Tron_so_far
	Prob_no_Tron_so_far = Prob_no_Tron_so_far * (1 - determine_T3Karn(7 - mulligans))
	print(f'When willing to mull down to {7-mulligans}, probability is {(1 - Prob_no_Tron_so_far) * 100:.2f}%.')
		
print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))

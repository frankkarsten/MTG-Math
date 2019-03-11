import random

deck = {
	'ComboA': 8,
	'ComboB': 8,
	'Other': 24,
	'Land': 20
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

def determine_ComboHand(handsize = 7):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	Returns - a number that represents the probability of finding an opening hand with one of each combo piece and two lands
	"""
	Combo_Success_prob = 0
	for ComboA in [1, 2, 3, 4]:
		for ComboB in [1, 2, 3, 4]:
			for Land in [2, 3, 4, 5]:
				if ComboA + ComboB + Land <= handsize:
					needed = {}
					needed['ComboA'] = ComboA
					needed['ComboB'] = ComboB
					needed['Land'] = Land
					needed['Other'] = handsize - ComboA - ComboB - Land
					Combo_Success_prob += multivariate_hypgeom(deck, needed)
	return Combo_Success_prob

def determine_FAILComboHand(handsize = 7):
	return 1 - determine_ComboHand(handsize)
	
def simulate_ComboHand(handsize = 7):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	Returns - a number that approximates via simulation the probability of finding an opening hand with one of each combo piece and two lands
	"""
	num_iterations = 10 ** 5
	count_good_hands = 0
	for _ in range(num_iterations):
		decklist = []
		for card in deck.keys():
			decklist += [card] * deck[card]
		random.shuffle(decklist)
		
		hand = {
			'ComboA': 0,
			'ComboB': 0,
			'Other': 0,
			'Land': 0
		}
		
		for _ in range(handsize):
			hand[decklist.pop(0)] += 1
		
		if hand['ComboA'] >=1 and hand['ComboB']>=1 and hand['Land']>=2:
			count_good_hands += 1
	return count_good_hands/num_iterations

expected_hand_size = 0
print("London probability of opening hand with one of each combo piece and two lands?")
for mulligans in range(4):
	print(f'When willing to mull down to {7 - mulligans}, probability is {(1 - (determine_FAILComboHand() ** (mulligans + 1))) * 100:.2f}%.')
	if (mulligans < 3): 
		expected_hand_size += (7 - mulligans) * (determine_FAILComboHand() ** mulligans) * determine_ComboHand()
	if (mulligans == 3):
		expected_hand_size += 4 * (determine_FAILComboHand() ** 3)
print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))
print('\nFor verification, simulation shows that the 7-card probability is: ' + str(round(100 * simulate_ComboHand(), 2))+"%")

print("\nVancouver prob of opening hand with one of each combo piece and two lands?")
expected_hand_size = 0
for mulligans in range(4):
	Prob_prior_mulligans = 1
	for prior_mulls in range(mulligans):
		Prob_prior_mulligans *= determine_FAILComboHand(7 - prior_mulls)
	
	print(f'When willing to mull down to {7-mulligans}, probability is {(1 - Prob_prior_mulligans * determine_FAILComboHand(7 - mulligans)) * 100:.2f}%.')
	if (mulligans < 3): 
		expected_hand_size += (7 - mulligans) * Prob_prior_mulligans * determine_ComboHand(7 - mulligans)
	if (mulligans == 3):
		expected_hand_size += 4 * Prob_prior_mulligans
print("Expected hand size when keeping: " + str(round(expected_hand_size, 2)))


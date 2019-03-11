import random

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

def determine_KeepableHand(handsize = 7):
	"""	
	Parameters:
		handsize - Should only be used for Vancouver rule. Represents the number of cards you mulligan towards
	Returns - a number that represents the probability of finding an opening hand with one of each combo piece and two lands
	"""
	Keephand_prob = 0
	for Land in [2, 3]:
		for Spell in [2, 3, 4, 5]:
			if Land + Spell == handsize:
				needed = {}
				needed['Land'] = Land
				needed['Spell'] = Spell
				Keephand_prob += multivariate_hypgeom(deck, needed)
	return Keephand_prob

def determine_FAILKeepableHand(handsize = 7):
	return 1 - determine_KeepableHand(handsize)
	
max_mulligans = 2

print("London probability of keepable opening hand?")
optimal_lands = 16
optimal_prob = 0
for number_lands in range(16,30):
	deck = {
		'Land': number_lands,
		'Spell': 60 - number_lands
	}
	for mulligans in range(4):
		probability_keephand = 1 - (determine_FAILKeepableHand() ** (mulligans + 1))
		print(f'{number_lands} lands - When willing to mull down to {7 - mulligans}, probability is {probability_keephand * 100:.3f}%.')
		if (mulligans == max_mulligans) and probability_keephand > optimal_prob:
			optimal_prob = probability_keephand
			optimal_lands = number_lands
print("The optimal number of lands (max_mulls="+str(max_mulligans)+") is "+str(optimal_lands))

print("Vancouver probability of keepable opening hand?")
for number_lands in range(16,30):
	deck = {
		'Land': number_lands,
		'Spell': 60 - number_lands
	}
	Prob_prior_mulligans = 1
	for mulligans in range(4):
		probability_keephand = 1 - Prob_prior_mulligans * determine_FAILKeepableHand(7 - mulligans)
		print(f'{number_lands} lands - When willing to mull down to {7 - mulligans}, probability is {probability_keephand * 100:.3f}%.')
		if (mulligans == max_mulligans) and probability_keephand > optimal_prob:
			optimal_prob = probability_keephand
			optimal_lands = number_lands
		Prob_prior_mulligans *= determine_FAILKeepableHand(7 - mulligans)
print("The optimal number of lands (max_mulls="+str(max_mulligans)+") is "+str(optimal_lands))

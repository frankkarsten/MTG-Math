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

def determine_KeepableHand(handsize, mulltype):
	"""	
	Parameters:
		handsize - Represents the number of cards you mulligan towards. Should be 7, 6, 5, or 4.
		mulltype - Vancouver or London
	Returns - a number that represents the probability of finding an opening hand with 2-3 lands and 2+ spells
	Note: A prior version of this document didn't adequately consider how to put back cards after London mull
	"""
	number_mulls = 7 - handsize
	if (mulltype == 'London'):
		number_cards_to_draw = 7
		max_lands_for_keepable_hand = 3 + number_mulls
	if (mulltype == 'Vancouver'):
		number_cards_to_draw = handsize
		max_lands_for_keepable_hand = 3
	Keephand_prob = 0
	for Land in range (2, max_lands_for_keepable_hand + 1):
		for Spell in range(2, 5 + 1):
			if Land + Spell == number_cards_to_draw:
				needed = {}
				needed['Land'] = Land
				needed['Spell'] = Spell
				Keephand_prob += multivariate_hypgeom(deck, needed)
	return Keephand_prob

def determine_FAILKeepableHand(handsize, mulltype):
	return 1 - determine_KeepableHand(handsize, mulltype)
	
max_mulligans = 2

print("London probability of keepable opening hand?")
optimal_lands = 16
optimal_prob = 0
for number_lands in range(16,30):
	deck = {
		'Land': number_lands,
		'Spell': 60 - number_lands
	}
	Prob_prior_mulligans = 1
	for mulligans in range(4):
		probability_keephand = 1 - Prob_prior_mulligans * determine_FAILKeepableHand(7 - mulligans, 'London')
		print(f'{number_lands} lands - When willing to mull down to {7 - mulligans}, probability is {probability_keephand * 100:.3f}%.')
		if (mulligans == max_mulligans) and probability_keephand > optimal_prob:
			optimal_prob = probability_keephand
			optimal_lands = number_lands
		Prob_prior_mulligans *= determine_FAILKeepableHand(7 - mulligans, 'London')
print("The optimal number of lands (max_mulls="+str(max_mulligans)+") is "+str(optimal_lands))

optimal_lands = 16
optimal_prob = 0
print("Vancouver probability of keepable opening hand?")
for number_lands in range(16,30):
	deck = {
		'Land': number_lands,
		'Spell': 60 - number_lands
	}
	Prob_prior_mulligans = 1
	for mulligans in range(4):
		probability_keephand = 1 - Prob_prior_mulligans * determine_FAILKeepableHand(7 - mulligans, 'Vancouver')
		print(f'{number_lands} lands - When willing to mull down to {7 - mulligans}, probability is {probability_keephand * 100:.3f}%.')
		if (mulligans == max_mulligans) and probability_keephand > optimal_prob:
			optimal_prob = probability_keephand
			optimal_lands = number_lands
		Prob_prior_mulligans *= determine_FAILKeepableHand(7 - mulligans, 'Vancouver')
print("The optimal number of lands (max_mulls="+str(max_mulligans)+") is "+str(optimal_lands))

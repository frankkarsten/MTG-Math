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
	answer = 1.0
	sum_deck = 0
	sum_needed = 0
	for card in deck.keys():
		answer *= binom(deck[card], needed[card])
		sum_deck += deck[card]
		sum_needed += needed[card]
	return answer / binom(sum_deck, sum_needed)

deck = {
	'Angel': 12,
	'Demon': 2,
	'Dragon': 2,
	'Changeling': 39,
	'Other': 43
}

#hit_prob(x) will eventually contain the probability that you hit x creatures with Kaalia
hit_prob = [0, 0, 0, 0]

print("Here is the probability distribution!")

for Angel in range(deck['Angel'] +1):
	for Demon in range(deck['Demon'] +1):
		for Dragon in range(deck['Dragon'] +1):
			for Changeling in range(deck['Changeling'] +1):
				if Angel + Demon + Dragon + Changeling <= 6:
					needed = {}
					needed['Angel'] = Angel
					needed['Demon'] = Demon
					needed['Dragon'] = Dragon
					needed['Changeling'] = Changeling
					needed['Other'] = 6 - Angel - Demon - Dragon - Changeling
					occurence_prob = multivariate_hypgeom(deck, needed)
					Changeling_remaining = Changeling
					#Take Angel or, if there is none, a Changeling if possible
					number_Angel = min(Angel, 1)
					if (number_Angel == 0) and Changeling_remaining > 0:
						number_Angel = 1
						Changeling_remaining = Changeling_remaining - 1
					#Take Dragon or, if there is none, a Changeling if possible
					number_Dragon = min(Dragon, 1)
					if (number_Dragon == 0) and Changeling_remaining > 0:
						number_Dragon = 1
						Changeling_remaining = Changeling_remaining - 1
					#Take Demon or, if there is none, a Changeling if possible
					number_Demon = min(Demon, 1)
					if (number_Demon == 0) and Changeling_remaining > 0:
						number_Demon = 1
					#Add probability to corresponding total hits
					hit_prob[number_Angel + number_Dragon + number_Demon] += occurence_prob

expectation = 0

for number_hits in [0, 1, 2, 3]:
	print(str(number_hits), 'hit(s):', str(round(100 * hit_prob[number_hits], 2))+"%")
	expectation += number_hits * hit_prob[number_hits]
	
print('Expected value:' , str(round( expectation, 2)))

color_pairs = ['WU','WB','WR','WG','UB','UR','UG','BR','BG','RG']

#The following is the NeoNiv deck minus one Niv-Mizzet, which is on the stack

deck = {
	'WU': 4,
	'WB': 2,
	'WR': 1,
	'WG': 3,
	'UB': 2,
	'UR': 0,
	'UG': 2,
	'BR': 0,
	'BG': 1,
	'RG': 3,
	'Other': 41
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

def determine_hit_prob(number_hits):
	"""	
	Parameters:
		number_hits - Should be between 0 or 10. Represents the number of cards put into your hand with Niv.
	Returns - a number that represents the probability of hitting <number_hits> different guilds in your top 10.
	"""
	hit_prob = 0
	for WU in range(deck['WU'] +1):
		for WB in range(deck['WB'] +1):
			for WR in range(deck['WR'] +1):
				for WG in range(deck['WG'] +1):
					for UB in range(deck['UB'] +1):
						for UR in range(deck['UR'] +1):
							for UG in range(deck['UG'] +1):
								for BR in range(deck['BR'] +1):
									for BG in range(deck['BG'] +1):
										for RG in range(deck['RG'] +1):
											cards_so_far = WU + WB + WR + WG + UB + UR + UG + BR + BG + RG
											hits_so_far = min(WU, 1) + min(WB, 1) + min(WR,1) + min(WG, 1) + min(UB, 1)
											hits_so_far += min(UR, 1) + min(UG, 1) + min(BR,1) + min(BG, 1) + min(RG, 1)
											if (cards_so_far <= 10 and hits_so_far == number_hits):
												needed = {}
												needed['WU'] = WU
												needed['WB'] = WB
												needed['WR'] = WR
												needed['WG'] = WG
												needed['UB'] = UB
												needed['UR'] = UR
												needed['UG'] = UG
												needed['BR'] = BR
												needed['BG'] = BG
												needed['RG'] = RG
												needed['Other'] = 10 - cards_so_far
												hit_prob += multivariate_hypgeom(deck, needed)
	return hit_prob

expected_hits = 0
for number_hits in range(11):
	hit_prob = determine_hit_prob(number_hits)
	print(f'Probability of hitting {number_hits} cards: {hit_prob * 100:.2f}%.')
	expected_hits += number_hits * hit_prob
print(f'Expected number of hits: : {expected_hits:.2f}.')
print(f'Hitting 8 cards happens once per {1 / determine_hit_prob(8):.1f} games on average.')

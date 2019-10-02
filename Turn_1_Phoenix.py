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

def OnceUponProb(librarysize, hits):
	"""	
	Returns the probability of hitting with Once Upon a Time
	when you have librarysize (>= hits) cards in your deck
	and when you have hits in that deck
	"""	
	deck = {
		'Hits': hits,
		'Nonhits': librarysize - hits
	}
	Success_prob = 0
	for nr_seen in range(1, min(hits, 5)+ 1):
		needed = {
			'Hits': nr_seen,
			'Nonhits': 5 - nr_seen
		}
		Success_prob += multivariate_hypgeom(deck, needed)
	return Success_prob

def determine_ComboHand(handsize):
	"""	
	Returns the probability of drawing the right combination of cards
	for a turn-1 Arclight Phoenix (without mulligans)
	The parameter handsize should be 7 on the play and 8 on the draw
	"""
	Combo_Success_prob = 0
	
	for OnceUpon in [0, 1, 2, 3, 4]:
		for Phoenix in [0, 1, 2, 3, 4]:
			for Rosethorn in [0, 1, 2, 3, 4]:
				for Haggle in [0, 1, 2, 3, 4]:
					for GreenLand in [0, 1, 2, 3, 4, 5, 6]:
						
						#Check if this is a feasible hand
						if OnceUpon + Phoenix + Rosethorn + Haggle + GreenLand <= handsize:
						
							#Determine probability of drawing this hand
							needed = {}
							needed['Once Upon a Time'] = OnceUpon
							needed['Arclight Phoenix'] = Phoenix
							needed['Rosethorn Acolyte'] = Rosethorn
							needed['Haggle'] = Haggle
							needed['Green land'] = GreenLand
							needed['Other'] = handsize - ( OnceUpon + Phoenix + Rosethorn + Haggle + GreenLand)
							Hand_prob = multivariate_hypgeom(deck, needed)
							
							#See if the hand has all the pieces
							DoubleRosethornSuccess = True if (Rosethorn >= 2 and Phoenix >= 1 and Haggle >= 1 and GreenLand >= 1) else False
							SingleRosethornSuccess = True if (OnceUpon >= 1 and Rosethorn >= 1 and Phoenix >= 1 and Haggle >= 1 and GreenLand >= 1) else False
							if (DoubleRosethornSuccess or SingleRosethornSuccess):
								Combo_Success_prob += Hand_prob

							#See if the hand has one missing piece but also Once Upon a Time
							OnlyOneMissing = True if min(Phoenix, 1) + min(Rosethorn, 1) + min(Haggle, 1) + min(GreenLand, 1) == 3 else False
							if (OnlyOneMissing and Phoenix == 0 and OnceUpon > 0):
								Combo_Success_prob += Hand_prob * OnceUponProb(60 - handsize, 4)
							if (OnlyOneMissing and Rosethorn == 0 and OnceUpon > 0):
								Combo_Success_prob += Hand_prob * OnceUponProb(60 - handsize, 4)
							if (OnlyOneMissing and Haggle == 0 and OnceUpon > 0):
								Combo_Success_prob += Hand_prob * OnceUponProb(60 - handsize, 4)
							if (OnlyOneMissing and GreenLand == 0 and OnceUpon > 0):
								Combo_Success_prob += Hand_prob * OnceUponProb(60 - handsize, deck['Green land'] - GreenLand)
							
	return Combo_Success_prob

deck = {
	'Once Upon a Time': 4,
	'Arclight Phoenix': 4,
	'Rosethorn Acolyte': 4,
	'Haggle': 4,
	'Green land': 12,
	'Other': 32
}

print("Probability of opening hand with turn-1 Phoenix?")
print(f'Probability on the play is {determine_ComboHand(7) * 100:.2f}%.')
print(f'Probability on the draw is {determine_ComboHand(8) * 100:.2f}%.')
print(f"Average is {( determine_ComboHand(7) + determine_ComboHand(8) ) / 2 * 100:.2f}%.")

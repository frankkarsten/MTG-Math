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

#I will assume that we want to cast a Force without paying its mana cost on our opponent’s second turn.
#There are no mulligans. So then we have seen 8 cards.
handsize = 8

print("Probability of holding a Pitcher or another Force, conditional on holding Force")
print("=====")

for Force_deck in [2,4]:
	#Consider decks with 2 Forces as well as decks with 4 Forces
	for Pitcher_deck in range(23):
		#Consider decks with 0-22 pitchers (cards of the same color that you can 'pitch' to cast a Force)
		#Total number of cards in the deck is 60
		deck = {
			'Force': Force_deck,
			'Pitcher': Pitcher_deck,
			'Other': 60-4-Pitcher_deck
		}
		#Combo_Success_prob will sum up the probabilities for all combinations with >=1 Force and either >=2 Force or >=1 pitcher
		Combo_Success_prob = 0
		#Force_prob will sum up the probabilities for all combinations with >=1 Force
		Force_prob = 0
		for Force in range(1, Force_deck +1):
			#So if, e.g., we have Force_deck = 2 Forces in our deck, then this range is the set [1, 2]
			#Hence, the presence of at least one Force is guaranteed
			for Pitcher in range(Pitcher_deck +1):
				#So if, e.g., we have Pitcher_deck = 4 Pitchers in our deck, then this range is the set [0, 1, 2, 3, 4]
				if Force + Pitcher <= handsize:
					#We can't consider combinations with, say, 9 Pitchers as those would exceed the number of cards drawn
					needed = {}
					needed['Force'] = Force
					needed['Pitcher'] = Pitcher
					needed['Other'] = handsize - Force - Pitcher
					probability = multivariate_hypgeom(deck, needed)
					if Pitcher >= 1 or Force >= 2:
						#We have either a Pitcher or another Force to pay for the alternative cost
						Combo_Success_prob += probability
					#In any case, this was a combination of cards with at least one Force
					Force_prob += probability

		print(f'Deck with {Force_deck} Forces and {Pitcher_deck} pitchers; probability : {(Combo_Success_prob/Force_prob)* 100:.1f}%.')

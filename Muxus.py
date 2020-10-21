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

for ThreeManaGoblins in [9, 10, 11, 12, 13, 14, 15]:
	deck = {
		'OneDrop': 4,
		'TwoDrop': 8,
		'ThreeDrop': ThreeManaGoblins,
		'FourDrop': 5,
	}
	deck['Other'] = 59 - deck['OneDrop'] - deck['TwoDrop'] - deck['ThreeDrop'] - deck['FourDrop']

	ProbabilityToHitExactlyZeroCreatures = 0
	ProbabilityToHitExactlyOneCreature = 0
	ProbabilityToHitAtLeastTwoCreatures = 0
	ExpectedCreatures = 0
	ExpectedMana = 0

	for OneDrop in range(min(deck['OneDrop'], 7)):
		for TwoDrop in range(min(deck['TwoDrop'], 7)):
			for ThreeDrop in range(min(deck['ThreeDrop'], 7)):
				for FourDrop in range(min(deck['FourDrop'], 7)):
					for Other in range(min(deck['Other'], 7)):
						if OneDrop + TwoDrop + ThreeDrop + FourDrop + Other == 6:
							needed = {
								'OneDrop': OneDrop,
								'TwoDrop': TwoDrop,
								'ThreeDrop': ThreeDrop,
								'FourDrop': FourDrop,
								'Other': Other
							}
							Probability = multivariate_hypgeom(deck, needed)
							Creatures = OneDrop + TwoDrop + ThreeDrop + FourDrop
							if (Creatures == 0):
								ProbabilityToHitExactlyZeroCreatures += Probability
							if (Creatures == 1):
								ProbabilityToHitExactlyOneCreature += Probability
							if (Creatures >= 2):
								ProbabilityToHitAtLeastTwoCreatures += Probability
							ExpectedMana += Probability * (1 * OneDrop + 2 * TwoDrop + 3 * ThreeDrop + 4 * FourDrop)
							ExpectedCreatures += Probability * Creatures
							
	Creatures = deck['OneDrop'] + deck['TwoDrop'] + deck['ThreeDrop'] + deck['FourDrop']
	print('\nFor this '+str(Creatures)+'-creature deck, ProbabilityToHitExactlyZeroCreatures = ' + str(round(100 * ProbabilityToHitExactlyZeroCreatures, 1))+"%")
	print('\nFor this '+str(Creatures)+'-creature deck, ProbabilityToHitExactlyOneCreature = ' + str(round(100 * ProbabilityToHitExactlyOneCreature, 1))+"%")
	print('\nFor this '+str(Creatures)+'-creature deck, ProbabilityToHitAtLeastTwoCreatures = ' + str(round(100 * ProbabilityToHitAtLeastTwoCreatures, 1))+"%")
	print('\nFor this '+str(Creatures)+'-creature deck, Expected Creatures = ' + str(round(ExpectedCreatures, 2)))
	print('\nFor this '+str(Creatures)+'-creature deck, ExpectedMana = ' + str(round(ExpectedMana, 2)))
	
#Determine probability to hit both a haste lord and Krenko	
deck = {
	'OneDrop': 4,
	'TwoDrop': 8,
	'ThreeDrop': 8,
	'FourDrop': 4,
}
deck['Other'] = 59 - deck['OneDrop'] - deck['TwoDrop'] - deck['ThreeDrop'] - deck['FourDrop']

ProbabilityToWin = 0

for OneDrop in range(min(deck['OneDrop'], 7)):
	for TwoDrop in range(min(deck['TwoDrop'], 7)):
		for ThreeDrop in range(min(deck['ThreeDrop'], 7)):
			for FourDrop in range(min(deck['FourDrop'], 7)):
				for Other in range(min(deck['Other'], 7)):
					if OneDrop + TwoDrop + ThreeDrop + FourDrop + Other == 6:
						needed = {
							'OneDrop': OneDrop,
							'TwoDrop': TwoDrop,
							'ThreeDrop': ThreeDrop,
							'FourDrop': FourDrop,
							'Other': Other
						}
						Probability = multivariate_hypgeom(deck, needed)
						if (ThreeDrop > 0 and FourDrop > 0):
							ProbabilityToWin += Probability
						
Creatures = deck['OneDrop'] + deck['TwoDrop'] + deck['ThreeDrop'] + deck['FourDrop']
print('-'*10)
print('\nFor this '+str(Creatures)+'-creature deck, ProbabilityToWin = ' + str(round(100 * ProbabilityToWin, 1))+"%")

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


def determine_ComboHand(handsize):
	Combo_Success_prob = 0
	
	#First consider settings where you draw the perfect opener
	for Incinerator in [1, 2, 3, 4]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0, 1, 2, 3, 4, 5, 6]:
					for Land in [2, 3, 4, 5, 6]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in range(deck['Thunderous Wrath'] + 1):
								#If the sum of this cards is equal to handsize (7 on the play, 8 on the draw) it's a viable turn-1 hand
								#We need at least two burn spells total, so Bolt + Rift + Seal >= 2
								#We need at least one setup burn spell for turn one, so Seal + Rift >= 1
								#We need at least one three-damage burn spell, as double Seal doesn't do it, so Bolt + Rift >= 1
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == handsize and (Bolt + Rift + Seal >= 2 and Seal + Rift >= 1 and Bolt + Rift >= 1):
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									Combo_Success_prob += multivariate_hypgeom(deck, needed)
							
	#Next consider settings where you draw the Incinerator on turn 2 (on the play)
	for Incinerator in [0]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0, 1, 2, 3, 4, 5, 6]:
					for Land in [2, 3, 4, 5, 6]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in range(deck['Thunderous Wrath'] + 1):
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == handsize and (Bolt + Rift + Seal >= 2 and Seal + Rift >= 1 and Bolt + Rift >= 1):
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									Combo_Success_prob += multivariate_hypgeom(deck, needed) * deck['Chandras Incinerator'] / (60 - handsize)
	
	#Next consider settings where you draw the burn spell that you'd cast on turn 2 on turn 2 (on the play)
	#If you lead with Rift Bolt on turn one, then drawing Seal of Fire on turn two is also ok. But drawing Rift Bolt on turn 2 is too late
	#Note that the range for the Bolt variable is set to [0]
	for Incinerator in [1, 2, 3, 4]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0]:
					for Land in [2, 3, 4, 5, 6]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in range(deck['Thunderous Wrath'] + 1):
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == handsize and ( (Seal >= 1 and Rift == 0) or (Seal == 0 and Rift >= 1) ):
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									outs = deck['Other Burn'] + deck['Seal of Fire'] if Rift >= 1 else deck['Other Burn']
									Combo_Success_prob += multivariate_hypgeom(deck, needed) * outs / (60 - handsize)

	#Next consider settings where you draw the second land on turn 2 (on the play)
	#Note that the range for the Land variable is set to [1]
	for Incinerator in [1, 2, 3, 4]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0, 1, 2, 3, 4, 5, 6]:
					for Land in [1]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in range(deck['Thunderous Wrath'] + 1):
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == handsize and (Bolt + Rift + Seal >= 2 and Seal + Rift >= 1 and Bolt + Rift >= 1):
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									Combo_Success_prob += multivariate_hypgeom(deck, needed) * (deck['Land'] - 1) / (60 - handsize)
		
	#Finally consider settings where you don't have enough burn spells but miracle Thunderous Wrath on turn 2 to get there
	for Incinerator in [1, 2, 3, 4]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0, 1, 2, 3, 4, 5, 6]:
					for Land in [2, 3, 4, 5, 6]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in [0, 1]:
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == handsize and (Rift + Seal == 0 or (Seal + Rift == 1 and Bolt == 0)):
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									Combo_Success_prob += multivariate_hypgeom(deck, needed) * (deck['Thunderous Wrath'] - Thunder) / (60 - handsize)
		
	return Combo_Success_prob

deck = {
	'Chandras Incinerator': 4,
	'Seal of Fire': 4,
	'Rift Bolt': 4,
	'Other Burn': 12,
	'Land': 20,
	'Thunderous Wrath': 2,
	'Other Spell': 14
}


print(f'Probability to play turn-2 Incinerator on the play is {determine_ComboHand(7) * 100:.2f}%.')

Prob_Incinerator_And_Two_lands = 0
for Incinerator in [1, 2, 3, 4]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0, 1, 2, 3, 4, 5, 6]:
					for Land in [2, 3, 4, 5, 6]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in [0, 1, 2]:
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == 8:
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									Prob_Incinerator_And_Two_lands += multivariate_hypgeom(deck, needed)

print(f'P [draw at least 1 Incinerator and at least 2 lands in top 8 cards] is {Prob_Incinerator_And_Two_lands * 100:.1f}%.')
print('')

print(f'Suppose you draw at least 1 Incinerator and at least 2 lands in top 8 cards.')
print(f'Then probability you can play turn-2 Incininerator is {determine_ComboHand(7) / Prob_Incinerator_And_Two_lands * 100:.1f}%.')
print('')
print('----------------')
print('')

print(f'Probability to play turn-2 Incinerator on the draw is {determine_ComboHand(8) * 100:.1f}%.')

Prob_Incinerator_And_Two_lands = 0
for Incinerator in [1, 2, 3, 4]:
		for Seal in [0, 1, 2, 3, 4]:
			for Rift in [0, 1, 2, 3, 4]:
				for Bolt in [0, 1, 2, 3, 4, 5, 6]:
					for Land in [2, 3, 4, 5, 6]:
						for Spell in [0, 1, 2, 3, 4, 5, 6]:
							for Thunder in [0, 1, 2]:
								if Incinerator + Seal + Rift + Bolt + Land + Spell + Thunder == 9:
									needed = {}
									needed['Chandras Incinerator'] = Incinerator
									needed['Seal of Fire'] = Seal
									needed['Rift Bolt'] = Rift
									needed['Other Burn'] = Bolt
									needed['Land'] = Land
									needed['Other Spell'] = Spell
									needed['Thunderous Wrath'] = Thunder
									Prob_Incinerator_And_Two_lands += multivariate_hypgeom(deck, needed)

print(f'P [draw at least 1 Incinerator and at least 2 lands in top 9 cards] is {Prob_Incinerator_And_Two_lands * 100:.1f}%.')
print('')
print(f'Suppose you draw at least 1 Incinerator and at least 2 lands in top 9 cards.')
print(f'Then probability you can play turn-2 Incininerator is  {determine_ComboHand(8) / Prob_Incinerator_And_Two_lands * 100:.1f}%.')



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


print("We now describe the conditional probability of seeing at least one 7-drop when you draw at least one Ugin's Labyrinth.")
print('')

def conditional_probability(deck, nr_cards_to_draw):
	 #Determoine probability to see at least one Ugins Labyrinth

	 prob_at_least_one_lab = 0
	 for nr_labyrinth in [1, 2, 3, 4]:
		  for nr_seven_drop in range(deck['Seven drop'] + 1):
			  if nr_labyrinth + nr_seven_drop <= nr_cards_to_draw:
					 needed = {
						  	'Seven drop': nr_seven_drop,
						  	'Ugins Labyrinth': nr_labyrinth,
						  	'Other': nr_cards_to_draw - nr_seven_drop - nr_labyrinth
					 }
					 prob_at_least_one_lab += multivariate_hypgeom(deck, needed)

	 #Determine probability to see at least one Ugins Labyrinth AND at least one seven-drop

	 prob_sol_land = 0
	 for nr_labyrinth in [1, 2, 3, 4]:
		  for nr_seven_drop in range(1, deck['Seven drop'] + 1):
			  if nr_labyrinth + nr_seven_drop <= nr_cards_to_draw:
					 needed = {
						  	'Seven drop': nr_seven_drop,
						  	'Ugins Labyrinth': nr_labyrinth,
						  	'Other': nr_cards_to_draw - nr_seven_drop - nr_labyrinth
					 }
					 prob_sol_land += multivariate_hypgeom(deck, needed)

	 conditional_prob = prob_sol_land / prob_at_least_one_lab
	 return conditional_prob


for nr_seven_drops_in_deck in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:

	 deck = {
	 	'Seven drop': nr_seven_drops_in_deck,
	 	'Ugins Labyrinth': 4,
	 	'Other': 60 - 4 - nr_seven_drops_in_deck
	 }
	 
	 cond_prob_play = conditional_probability(deck, 7)
	 cond_prob_draw = conditional_probability(deck, 8)
	 
	 print(f'With {nr_seven_drops_in_deck} seven-drops: {cond_prob_play * 100:.1f}% on the play and {cond_prob_draw * 100:.1f}% on the draw.')

print('')
print("We now describe the conditional probability of seeing at least one 7-drop on the draw when you draw at least one Ugin's Labyrinth, considering Devourer of Destiny.")
print('')

def conditional_probability_Devourer(deck):
	 #Situation 1: Opening 7 contains Ugin's Lab
	 #Situation 2: Opening 7 does not contain Ugin's Lab nor Devourer but Ugin's Lab is eighth card
	 #Situation 3: Opening 7 does not contain Ugin's Lab but does contain at least one Devourer, which then finds Ugin's Lab

	prob_at_least_one_lab = 0
	prob_sol_land = 0

	#Situation 1
	for nr_labyrinth in [1, 2, 3, 4]:
		  for nr_devourer in [0, 1, 2, 3, 4]:
			  for nr_seven_drop in range(deck['Seven drop'] + 1):
				  if nr_labyrinth + nr_seven_drop + nr_devourer <= 7:
						 needed = {
							  	'Seven drop': nr_seven_drop,
							    'Devourer': nr_devourer,
							  	'Ugins Labyrinth': nr_labyrinth,
							  	'Other': 7 - nr_seven_drop - nr_labyrinth
						 }
						 opening_hand_prob = multivariate_hypgeom(deck, needed)
						 prob_at_least_one_lab += opening_hand_prob
						 if nr_seven_drop + nr_devourer >= 1:
							 prob_sol_land += opening_hand_prob
						 else:
							 #We might topdeck a seven-drop on turn one
							 prob_sol_land += opening_hand_prob * (deck['Devourer'] + deck['Seven drop']) / 53

	 #Situation 2
	for nr_labyrinth in [0]:
		  for nr_devourer in [0]:
			  for nr_seven_drop in range(deck['Seven drop'] + 1):
				  if nr_labyrinth + nr_seven_drop + nr_devourer <= 7:
						 needed = {
							  	'Seven drop': nr_seven_drop,
							    'Devourer': nr_devourer,
							  	'Ugins Labyrinth': nr_labyrinth,
							  	'Other': 7 - nr_seven_drop - nr_labyrinth
						 }
						 opening_hand_prob = multivariate_hypgeom(deck, needed)
						 #We now need to topdeck Ugin's Lab on turn one
						 prob_at_least_one_lab += opening_hand_prob * deck['Ugins Labyrinth'] / 53
						 if nr_seven_drop + nr_devourer >= 1:
							 prob_sol_land += opening_hand_prob * deck['Ugins Labyrinth'] / 53

	 #Situation 3
	for nr_labyrinth in [0]:
		  for nr_devourer in [1, 2, 3, 4]:
			  for nr_seven_drop in range(deck['Seven drop'] + 1):
				  if nr_labyrinth + nr_seven_drop + nr_devourer <= 7:
						 needed = {
							  	'Seven drop': nr_seven_drop,
							    'Devourer': nr_devourer,
							  	'Ugins Labyrinth': nr_labyrinth,
							  	'Other': 7 - nr_seven_drop - nr_labyrinth
						 }
						 opening_hand_prob = multivariate_hypgeom(deck, needed)
						 #We now need to topdeck Ugin's Lab on turn one
						 #Hypergeometric probability of seeing at least one success in a sample of 5 from a population of 53 with 4 successes is 0.33551
						 prob_at_least_one_lab += opening_hand_prob * 0.33551
						 prob_sol_land += opening_hand_prob * 0.33551


	conditional_prob = prob_sol_land / prob_at_least_one_lab
	return conditional_prob

for nr_seven_drops_in_deck in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:

	 deck = {
	 	'Seven drop': nr_seven_drops_in_deck - 4,
		  'Devourer': 4,
	 	'Ugins Labyrinth': 4,
	 	'Other': 60 - 4 - nr_seven_drops_in_deck
	 }
	 
	 cond_prob_devourer = conditional_probability_Devourer(deck)
	 
	 print(f'With {nr_seven_drops_in_deck} seven-drops: {cond_prob_devourer * 100:.1f}% on the draw, considering Devourer.')

def conditional_probability_too_many7(deck):
	 #Determoine probability to see at least two land

	 prob_at_least_two_land = 0
	 for nr_labyrinth in [0, 1, 2, 3, 4]:
		 for nr_other_land in [0, 1, 2, 3, 4, 5, 6, 7]:
			 for nr_seven_drop in range(deck['Seven drop'] + 1):
				 if nr_labyrinth + nr_other_land + nr_seven_drop <= 7 and nr_labyrinth + nr_other_land >= 2:
						 needed = {
							  	'Seven drop': nr_seven_drop,
							  	'Ugins Labyrinth': nr_labyrinth,
							'Other land': nr_other_land,
							  	'Other spell': 7 - nr_seven_drop - nr_labyrinth - nr_other_land
						 }
						 prob_at_least_two_land += multivariate_hypgeom(deck, needed)

	 #Determine probability to see at least two land AND at least three seven-drop

	 prob_at_least_three_seven = 0
	 for nr_labyrinth in [0, 1, 2, 3, 4]:
		 for nr_other_land in [0, 1, 2, 3, 4, 5, 6, 7]:
			 for nr_seven_drop in range(deck['Seven drop'] + 1):
				 if nr_labyrinth + nr_other_land + nr_seven_drop <= 7 and nr_labyrinth + nr_other_land >= 2 and nr_seven_drop >= 3:
						 needed = {
							  	'Seven drop': nr_seven_drop,
							  	'Ugins Labyrinth': nr_labyrinth,
							'Other land': nr_other_land,
							  	'Other spell': 7 - nr_seven_drop - nr_labyrinth - nr_other_land
						 }
						 prob_at_least_three_seven += multivariate_hypgeom(deck, needed)

	 conditional_prob = prob_at_least_three_seven / prob_at_least_two_land
	 return conditional_prob

print('')
print("We now describe the conditional probability of seeing at least three 7-drop in an opening hand with at least 2 lands, assuming 24 lands in a 60-card deck.")
print('')

for nr_seven_drops_in_deck in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:

	 deck = {
	 	'Seven drop': nr_seven_drops_in_deck,
	 	'Ugins Labyrinth': 4,
		'Other land': 20,
	 	'Other spell': 60 - 4 - 20 - nr_seven_drops_in_deck
	 }
	 
	 print(f'With {nr_seven_drops_in_deck} seven-drops: {conditional_probability_too_many7(deck) * 100:.1f}%.')



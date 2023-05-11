import random

def put_lands_on_bottom(hand, lands_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		lands_to_bottom - The number of lands to bottom (must be <= number of lands in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	Bottomable_other_lands = min(hand['Other Land'], lands_to_bottom)
	hand['Other Land'] -= Bottomable_other_lands

	Bottomable_basic_lands = min(hand['Basic Land'], lands_to_bottom - Bottomable_other_lands)
	hand['Basic Land'] -= Bottomable_basic_lands

def put_spells_on_bottom(hand, spells_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		spells_to_bottom - The number of spells to bottom (must be <= number of spells in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	Bottomable_other_spells = min(hand['Other Spell'], spells_to_bottom)
	hand['Other Spell'] -= Bottomable_other_spells

	Bottomable_Ossification = min(hand['Ossification'], spells_to_bottom - Bottomable_other_spells)
	hand['Ossification'] -= Bottomable_Ossification

def total_lands(hand):
	return hand['Basic Land'] + hand['Other Land']

def total_spells(hand):
	return hand['Ossification'] + hand['Other Spell']

	
def run_one_sim():	
	#Conditional on drawing at least one Ossification and at least two lands by a certain turn, 
	#after accounting for mulligans in a 26-land, 60-card deck with 4 Ossification, 
	#we'll look for the probability to have access to a basic land

	keephand = False 
	
	for handsize in [7, 6, 5, 4]:
		#We may mull 7, 6, or 5 cards and keep every 4-card hand
		#Once we actually keep, the variable keephand will be set to True
		if not keephand:
			
			#Construct library as a list
			library = []
			for card in decklist.keys():
				library += [card] * decklist[card]
			random.shuffle(library)

			#Construct a random opening hand
			hand = {
				'Ossification': 0,
				'Other Spell': 0,
				'Basic Land': 0,
				'Other Land': 0
			}
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1

			if handsize == 7:
				#Do we keep?
				if (total_lands(hand) >= 2 and total_lands(hand) <= 5):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 3 land, 3 spells
				if total_spells(hand) > 3:
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, 2, or 3 spells so we put a land on the bottom
					put_lands_on_bottom(hand, 1)
				#Do we keep?
				if (total_lands(hand) >= 2 and total_lands(hand) <= 4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if total_spells(hand) > 3:
					#Two spells on the bottom
					put_spells_on_bottom(hand, 2)
				elif total_spells(hand) == 3:
					#One land, one spell on the bottom
					put_lands_on_bottom(hand, 1)
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					put_lands_on_bottom(hand, 2)
				#Do we keep?
				if (total_lands(hand) >= 2 and total_lands(hand) <= 4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if total_spells(hand) > 3:
					#Three spells on the bottom
					put_spells_on_bottom(hand, 3)
				elif total_spells(hand) == 3:
					#One land, two spell on the bottom
					put_lands_on_bottom(hand, 1)
					put_spells_on_bottom(hand, 2)
				elif total_spells(hand) == 2:
					#Two land, one spell on the bottom
					put_lands_on_bottom(hand, 2)
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0 or 1 spell so we put three land on the bottom
					put_lands_on_bottom(hand, 3)
				#Do we keep?
				keephand = True
	
	if play_draw == 'draw':
		#Draw a card on turn 1
		card_drawn = library.pop(0)
		hand[card_drawn] += 1

	for turn in range(2, turn_allowed + 1):
		#If, e.g., turn_allowed is 3 then this range is {2, 3}
		card_drawn = library.pop(0)
		hand[card_drawn] += 1

	if total_lands(hand) >= 2 and hand['Ossification'] >= 1 and hand['Basic Land'] >= 1:
		return 'Success'
	if total_lands(hand) >= 2 and hand['Ossification'] >= 1 and hand['Basic Land'] == 0:
		return 'Failure'
	if total_lands(hand) < 2 or hand['Ossification'] == 0:
		return 'Irrelevant for conditioning'

num_simulations = 500000
#Uncertainty with five million simulations will be about +/- 0.03%

nr_lands = 26
deck_size = 60
nr_Ossification = 4

for turn_allowed in [2, 3, 4]:
	for basic_lands in [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
		for play_draw in ['play', 'draw']:
			decklist = {
				'Ossification': nr_Ossification,
				'Other Spell': deck_size - nr_Ossification - nr_lands,
				'Basic Land': basic_lands,
				'Other Land': nr_lands - basic_lands
			}
			num_success = 0.0
			num_relevant_games = 0.0
			for _ in range(num_simulations):
				outcome = run_one_sim()
				if outcome == 'Success':
					num_success += 1
					num_relevant_games += 1
				if outcome == 'Failure':
					num_relevant_games += 1
			if play_draw == 'play':
				prob_on_play = num_success / num_relevant_games
			if play_draw == 'draw':
				prob_on_draw = num_success / num_relevant_games

		print(f"Conditional probability of basic on turn {turn_allowed} with {basic_lands} basics: {prob_on_play *100:.1f}% (play) / {prob_on_draw *100:.1f}% (draw)")
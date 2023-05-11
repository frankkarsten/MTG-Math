import random

def put_lands_on_bottom(hand, lands_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		lands_to_bottom - The number of lands to bottom (must be <= number of lands in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	hand['Land'] -= lands_to_bottom

def put_spells_on_bottom(hand, spells_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		spells_to_bottom - The number of spells to bottom (must be <= number of spells in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	#First, bottom other spells
	Bottomable_other_spells = min(hand['Other Spell'], spells_to_bottom)
	hand['Other Spell'] -= Bottomable_other_spells

	#Then, try to keep 1 Invasion but bottom the rest
	Bottomable_Invasion = min(max(hand['Invasion'] -1, 0), spells_to_bottom - Bottomable_other_spells)
	hand['Invasion'] -= Bottomable_Invasion

	#Then, bottom Dragons as needed
	Bottomable_Dragon = min(hand['Dragon'], spells_to_bottom - Bottomable_other_spells - Bottomable_Invasion)
	hand['Dragon'] -= Bottomable_Dragon

def total_lands(hand):
	return hand['Land']

def total_spells(hand):
	return hand['Dragon'] + hand['Invasion'] + hand['Other Spell']

	
def run_one_sim():	

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
				'Invasion': 0,
				'Dragon': 0,
				'Other Spell': 0,
				'Land': 0
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

	if total_lands(hand) >= 2 and hand['Invasion'] >= 1:
		return 2 + hand['Dragon']
	if total_lands(hand) < 2 or hand['Invasion'] == 0:
		return 'No castable Invasion'

num_simulations = 500000
#Uncertainty with five million simulations will be about +/- 0.03%

nr_lands = 24
deck_size = 60
nr_Invasion = 4

for turn_allowed in [2, 3, 4]:
	for nr_dragons in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
		for play_draw in ['play', 'draw']:
			decklist = {
				'Invasion': nr_Invasion,
				'Dragon': nr_dragons,
				'Other Spell': deck_size - nr_Invasion - nr_dragons - nr_lands,
				'Land': nr_lands
			}
			damage = 0.0
			num_relevant_games = 0.0
			for _ in range(num_simulations):
				outcome = run_one_sim()
				if outcome == 'No castable Invasion':
					pass
				else:
					damage += outcome
					num_relevant_games += 1
			if play_draw == 'play':
				dmg_on_play = damage / num_relevant_games
			if play_draw == 'draw':
				dmg_on_draw = damage / num_relevant_games

		print(f"Expected damage on turn {turn_allowed} with {nr_dragons} Dragons: {dmg_on_play:.2f} (play) / {dmg_on_draw :.2f} (draw)")
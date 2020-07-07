'''
MULLIGAN RULE:
• A 7-card hand is kept if it has 2, 3, 4, or 5 lands. 
• For a mulligan to 6, we first choose what to put on the bottom and decide keep or mull afterwards. 
	To get a good mix, we bottom the most expensive spell if we drew 3+ spells and we bottom a land if we drew 5+ lands. 	
	Afterwards, we keep if we hold 2, 3, or 4 lands. Otherwise, we mulligan.
• For a mulligan to 5, we try to get close to 3 lands and 2 spells. 
	So we bottom two spells (the most expensive ones) if we drew 4+ spells, we bottom a spell and a land if we drew 3 spells, and we bottom two lands if we drew 2 spells. 
	Afterwards, we keep if we have 2, 3, or 4 lands; otherwise, we mulligan.
• For a mulligan to 4, we try to get close to 3 lands and 1 spell. Then we always keep.
'''

import random

def put_lands_on_bottom(hand, lands_remaining_to_bottom):
	#Bottom Mountains before bottoming Forests
	Bottomable_Mountain = min(hand['Mountain'], lands_remaining_to_bottom)
	hand['Mountain'] -= Bottomable_Mountain
	lands_remaining_to_bottom -= Bottomable_Mountain

	Bottomable_Forest = min(hand['Forest'], lands_remaining_to_bottom)
	hand['Forest'] -= Bottomable_Forest
	lands_remaining_to_bottom -= Bottomable_Forest

def nr_lands(hand):
	return hand['Forest'] + hand['Mountain']
	
def run_one_sim(drawfirst, number_of_lands_needed):	
	#Initialize variables
	lands_in_play = 0
	turn_of_interest = 4
	
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
				'Spell': 0,
				'Forest': 0,
				'Mountain': 0
			}
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1

			if handsize == 7:
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 5):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 4 land, 2 spells
				if hand['Spell'] > 2:
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, or 2 spells so we put a land on the bottom
					put_lands_on_bottom(hand, 1)
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if hand['Spell'] > 3:
					#Two spells on the bottom
					hand['Spell'] -= 2
				elif hand['Spell'] == 3:
					#One land, one spell on the bottom
					put_lands_on_bottom(hand, 1)
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					put_lands_on_bottom(hand, 2)
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if hand['Spell'] > 3:
					#Three spells on the bottom
					hand['Spell'] -= 3
				elif hand['Spell'] == 3:
					#One land, two spell on the bottom
					put_lands_on_bottom(hand, 1)
					hand['Spell'] -= 2
				elif hand['Spell'] == 2:
					#Two land, one spell on the bottom
					put_lands_on_bottom(hand, 2)
					hand['Spell'] -= 1
				else:
					#The hand has 0 or 1 spell so we put three land on the bottom
					put_lands_on_bottom(hand, 3)
				#Do we keep?
				keephand = True
	
	for turn in range(1, turn_of_interest + 1):
		#If turn_of_interest is 4 then this range is {1, 2, 3, 4}
		#Play/draw is taken into account
		draw_a_card = True if (turn == 1 and drawfirst) or (turn > 1) else False
		if (draw_a_card):
			card_drawn = library.pop(0)
			hand[card_drawn] += 1

	return 1 if hand['Forest'] >= number_of_lands_needed else 0


num_simulations = 5000000
#Uncertainty with five million simulations will be about +/- 0.03%

for deck_size in [40, 60]:
	
	print("===> We now consider decks of size " + str(deck_size))
	
	for drawfirst in [True, False]:
		
		print("--We now set drawfirst to be "+str(drawfirst))
		
		#Start with mono-color decks where only total number of lands is relevant
		land_set = {
			40: range(15, 19 + 1),
			60: range(23, 27 + 1),
		}
		for num_lands in land_set[deck_size]:
			decklist = {
				'Spell': deck_size - num_lands,
				'Mountain': 0,
				'Forest': num_lands
			}
			num_success = 0.0
			for _ in range(num_simulations):
				num_success += run_one_sim(drawfirst, 4)
			print(f"For a deck with {num_lands} lands and {decklist['Spell']} spells, P[4 lands by turn 4] = {num_success / num_simulations *100:.1f}%")
		
		#Consider two-color decks with colored mana issues
		Forest_set = {
			40: range(8, 9 + 1),
			60: range(12, 16 + 1),
		}
		for nr_Forest in Forest_set[deck_size]:
			nr_Mountain = 8 if deck_size == 40 else 11
			decklist = {
				'Spell': deck_size - nr_Mountain - nr_Forest,
				'Mountain': nr_Mountain,
				'Forest': nr_Forest
			}
			num_success = 0.0
			for _ in range(num_simulations):
				num_success += run_one_sim(drawfirst, 1)
			print(f"For {nr_Mountain} Mountain, {nr_Forest} Forest, and {decklist['Spell']} spells, P[1 Forest by turn 4] = {num_success / num_simulations *100:.1f}%")
			num_success = 0.0
			for _ in range(num_simulations):
				num_success += run_one_sim(drawfirst, 2)
			print(f"For {nr_Mountain} Mountain, {nr_Forest} Forest, and {decklist['Spell']} spells, P[2 Forest by turn 4] = {num_success / num_simulations *100:.1f}%")

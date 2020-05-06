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

def run_one_sim():	
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
				'Land': 0
			}
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1

			if handsize == 7:
				#Do we keep?
				if (hand['Land'] >= 2 and hand['Land'] <= 5):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 4 land, 2 spells
				if hand['Spell'] > 2:
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, or 2 spells so we put a land on the bottom
					hand['Land'] -= 1
				#Do we keep?
				if (hand['Land'] >= 2 and hand['Land'] <= 4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if hand['Spell'] > 3:
					#Two spells on the bottom
					hand['Spell'] -= 2
				elif hand['Spell'] == 3:
					#One land, one spell on the bottom
					hand['Land'] -= 1
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					hand['Land'] -= 2
				#Do we keep?
				if (hand['Land'] >= 2 and hand['Land'] <= 4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if hand['Spell'] > 3:
					#Three spells on the bottom
					hand['Spell'] -= 3
				elif hand['Spell'] == 3:
					#One land, two spell on the bottom
					hand['Land'] -= 1
					hand['Spell'] -= 2
				elif hand['Spell'] == 2:
					#Two land, one spell on the bottom
					hand['Land'] -= 2
					hand['Spell'] -= 1
				else:
					#The hand has 0 or 1 spell so we put three land on the bottom
					hand['Land'] -= 3
				#Do we keep?
				keephand = True
	
	for turn in range(1, turn_of_interest + 1):
		#If turn_of_interest is 4 then this range is {1, 2, 3, 4}
		#Play/draw is randomized
		draw_a_card = True if (turn == 1 and random.random() < 0.5) or (turn > 1) else False
		if (draw_a_card):
			card_drawn = library.pop(0)
			hand[card_drawn] += 1

		if (hand['Land'] > 0):
			hand['Land'] -= 1
			lands_in_play += 1
		
	return 1 if lands_in_play >= turn_of_interest else 0


num_simulations = 5000000
#Uncertainty with five million simulations will be about +/- 0.03%

for deck_size in [60,80]:
	print("===> We now consider decks of size " + str(deck_size))
	land_set = range(21,31) if deck_size == 60 else range(27,41)
	for nr_lands in land_set:
		decklist = {
			'Spell': deck_size - nr_lands,
			'Land': nr_lands
		}
		num_success = 0.0
		for _ in range(num_simulations):
			num_success += run_one_sim()
		print(f"For deck with {nr_lands} lands and {decklist['Spell']} spells, P[4 lands by turn 4] = {num_success / num_simulations *100:.2f}%")

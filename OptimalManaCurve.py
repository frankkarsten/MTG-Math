'''
MULLIGAN RULE:
• A 7-card hand is kept if it has 2, 3, 4, or 5 lands. 
• For a mulligan to 6, we first choose what to put on the bottom and decide keep or mull afterwards. 
	To get a good mix, we bottom the most expensive spell if we drew 4+ spells and we bottom a land if we drew 4+ lands. 	
	Afterwards, we keep if we hold 2, 3, or 4 lands. Otherwise, we mulligan.
• For a mulligan to 5, we try to get close to 3 lands and 2 spells. 
	So we bottom two spells (the most expensive ones) if we drew 4+ spells, we bottom a spell and a land if we drew 3 spells, and we bottom two lands if we drew 2 spells. 
	Afterwards, we keep if we have 2, 3, or 4 lands; otherwise, we mulligan.
• For a mulligan to 4, we try to get close to 3 lands and 1 spell. Then we always keep.
'''

'''
GAMEPLAY RULE:
On each turn, we play a land if possible. Then, we cast the highest cost spell that we have mana available for. 
If we have untapped lands remaining after that, we again play the highest cost spell that we can cast. And so on. 
This might cause us to play a three-drop on turn four rather than two two-drops, but that’s not unreasonable because the three-drop may have more impact on the game at that point.
'''

import numpy as np
import random
from collections import Counter

#Manually adjust these parameters to set the deck type and an initial guess for where to start searching
#Make sure that this initial guess matches the companion requirements, if applicable
deck_size = 60
companion = "No"
initial_1_cmc = 3
initial_2_cmc = 10
initial_3_cmc = 10
initial_4_cmc = 7
initial_5_cmc = 4
initial_land = 26

def put_spells_on_bottom(hand, spells_remaining_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		spells_remaining_to_bottom - The number of spells to bottom (must be <= number of spells in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	Bottomable_cmc_5 = min(hand['5 CMC'], spells_remaining_to_bottom)
	hand['5 CMC'] -= Bottomable_cmc_5
	spells_remaining_to_bottom -= Bottomable_cmc_5

	Bottomable_cmc_4 = min(hand['4 CMC'], spells_remaining_to_bottom)
	hand['4 CMC'] -= Bottomable_cmc_4
	spells_remaining_to_bottom -= Bottomable_cmc_4

	Bottomable_cmc_3 = min(hand['3 CMC'], spells_remaining_to_bottom)
	hand['3 CMC'] -= Bottomable_cmc_3
	spells_remaining_to_bottom -= Bottomable_cmc_3

	Bottomable_cmc_2 = min(hand['2 CMC'], spells_remaining_to_bottom)
	hand['2 CMC'] -= Bottomable_cmc_2
	spells_remaining_to_bottom -= Bottomable_cmc_2

	Bottomable_cmc_1 = min(hand['1 CMC'], spells_remaining_to_bottom)
	hand['1 CMC'] -= Bottomable_cmc_1
	spells_remaining_to_bottom -= Bottomable_cmc_1

def nr_spells(hand):
	return hand['1 CMC'] + hand['2 CMC'] + hand['3 CMC'] + hand['4 CMC'] + hand['5 CMC']

def run_one_sim(playfirst):	
	#Initialize variables
	lands_in_play = 0
	mana_spent = 0
	cumulative_mana_in_play = 0
	turn_of_interest = 7
		
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
				'1 CMC': 0,
				'2 CMC': 0,
				'3 CMC': 0,
				'4 CMC': 0,
				'5 CMC': 0,
				'6 CMC': 0,
				'Land': 0
			}
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1

			#Do we keep?
			if handsize == 7:
				if (hand['Land'] >= 2 and hand['Land'] <= 5):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 3 land, 3 spells
				if nr_spells(hand) > 3:
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, 2, or 3 spells so we put a land on the bottom
					hand['Land'] -= 1
				#Do we keep?
				if (hand['Land'] >= 2 and hand['Land'] <= 4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if nr_spells(hand) > 3:
					#Two spells on the bottom
					put_spells_on_bottom(hand, 2)
				elif nr_spells(hand) == 3:
					#One land, one spell on the bottom
					hand['Land'] -= 1
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					hand['Land'] -= 2
				#Do we keep?
				if (hand['Land'] >= 2 and hand['Land'] <= 4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if nr_spells(hand) > 3:
					#Three spells on the bottom
					put_spells_on_bottom(hand, 3)
				elif nr_spells(hand) == 3:
					#One land, two spell on the bottom
					hand['Land'] -= 1
					put_spells_on_bottom(hand, 2)
				elif nr_spells(hand) == 2:
					#Two land, one spell on the bottom
					hand['Land'] -= 2
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0 or 1 spell so we put three land on the bottom
					hand['Land'] -= 3
				#Do we keep?
				keephand = True
	
	#Add companion.
	if companion in ["Kaheera", "Lutri", "Zirda", "Lurrus"]:
		hand['3 CMC'] += 1
	if companion in ["Umori"]:
		hand['4 CMC'] += 1
	if companion in ["Jegantha", "Yorion", "Obosh", "Keruga"]:
		hand['5 CMC'] += 1
	if companion in ["Gyruda"]:
		hand['6 CMC'] += 1
			
	for turn in range(1, turn_of_interest + 1):
		#For turn_of_interest = 7, this range is {1, 2, ..., 7} so we consider mana spent over the first 7 turns
		mana_spent += cumulative_mana_in_play
		#This previous line is essential to get compounded mana spent
		draw_a_card = True if (turn == 1 and not playfirst) or (turn > 1) else False
		if (draw_a_card):
			card_drawn = library.pop(0)
			hand[card_drawn] += 1

		if (hand['Land'] > 0):
			hand['Land'] -= 1
			lands_in_play += 1
		
		mana_available = lands_in_play
		
		if (companion == "Gyruda"):
			Castable_cmc_6 = min(hand['6 CMC'], mana_available // 6)
			hand['6 CMC'] -= Castable_cmc_6
			mana_available -= Castable_cmc_6 * 6
			mana_spent += Castable_cmc_6 * 6
			cumulative_mana_in_play += Castable_cmc_6 * 6

		Castable_cmc_5 = min(hand['5 CMC'], mana_available // 5)
		hand['5 CMC'] -= Castable_cmc_5
		mana_available -= Castable_cmc_5 * 5
		mana_spent += Castable_cmc_5 * 5
		cumulative_mana_in_play += Castable_cmc_5 * 5
		
		Castable_cmc_4 = min(hand['4 CMC'], mana_available // 4)
		hand['4 CMC'] -= Castable_cmc_4
		mana_available -= Castable_cmc_4 * 4
		mana_spent += Castable_cmc_4 * 4
		cumulative_mana_in_play += Castable_cmc_4 * 4

		Castable_cmc_3 = min(hand['3 CMC'], mana_available // 3)
		hand['3 CMC'] -= Castable_cmc_3
		mana_available -= Castable_cmc_3 * 3
		mana_spent += Castable_cmc_3 * 3
		cumulative_mana_in_play += Castable_cmc_3 * 3
		
		Castable_cmc_2 = min(hand['2 CMC'], mana_available // 2)
		hand['2 CMC'] -= Castable_cmc_2
		mana_available -= Castable_cmc_2 * 2
		mana_spent += Castable_cmc_2 * 2
		cumulative_mana_in_play += Castable_cmc_2 * 2
		
		Castable_cmc_1 = min(hand['1 CMC'], mana_available // 1)
		hand['1 CMC'] -= Castable_cmc_1
		mana_available -= Castable_cmc_1 * 1
		mana_spent += Castable_cmc_1 * 1
		cumulative_mana_in_play += Castable_cmc_1 * 1

	return mana_spent


#Initialize local search algorithm
num_simulations = 3000
best_one = initial_1_cmc 
best_two = initial_2_cmc 
best_three = initial_3_cmc 
best_four = initial_4_cmc 
best_five = initial_5_cmc 
best_land = initial_land 
previous_best_mana_spent = 0
sims_for_best_deck = 0
continue_searching = True

Feasible_set = (25, 35, 25, 1, 9, 35) if companion == "Lurrus" or companion == "Obosh" else (12, 24, 24, 16, 12, 50)
Estimation = np.zeros(Feasible_set)
Number_sims = np.zeros(Feasible_set)

#Start the local search
#We start at a given initial feasible solution and we keep moving to better points in a neighborhood until no better point exists. 
#Then we have reached a local optimum. We need a certain number of simulations before we can "safely" stop.
#Neighborhood of a deck X: all possible decks where the number of one-drops is at most 1 more or 1 fewer than the number of one-drops in X...
#...and likewise for two-drops, three-drops, and so on. For all, it has to hold that the deck is of the right deck size.
#We start with a limited number of simulations as we explore and increase the number of simulations in every step
#If we have to re-evaluate a deck, we combine the simulations from the current iterations with the ones that have already taken place prior.

while continue_searching:
	best_mana_spent = 0
	improvement_possible = False
	for one in range(max(best_one - 1, 0), best_one + 2):
		for two in range(max(best_two - 1, 0), best_two + 2):
			for three in range(max(best_three - 1, 0), best_three + 2):
				for four in range(max(best_four - 1, 0), best_four + 2):
					for five in range(max(best_five - 1, 0), best_five + 2):
						for land in range(max(best_land - 1, 0), best_land + 2):
							
							companion_restriction_satisfied = True
							if companion == "Lurrus" and three + four + five > 0:
								companion_restriction_satisfied = False
							if companion == "Obosh" and two + four > 0:
								companion_restriction_satisfied = False
							if companion == "Keruga" and one + two > 0:
								companion_restriction_satisfied = False
							if companion == "Gyruda" and one + three + five > 0:
								companion_restriction_satisfied = False
							
							if one + two + three + four + five + land == deck_size and companion_restriction_satisfied:
						
								decklist = {
									'1 CMC': one,
									'2 CMC': two,
									'3 CMC': three,
									'4 CMC': four,
									'5 CMC': five,
									'Land': land
								}
								
								dont_bother = False
								if (Number_sims[ one, two, three, four, five, land] > 50000 and Estimation[ one, two, three, four, five, land] < 0.998 * previous_best_mana_spent):
									dont_bother = True
								if (Number_sims[ one, two, three, four, five, land] > 100000 and Estimation[ one, two, three, four, five, land] < 0.999 * previous_best_mana_spent):
									dont_bother = True
								if (Number_sims[ one, two, three, four, five, land] > 200000 and Estimation[ one, two, three, four, five, land] < 0.9995 * previous_best_mana_spent):
									dont_bother = True
								if not dont_bother:
									total_mana_spent = 0.0
									for _ in range(int(num_simulations / 2)):
										#Half sims play first, half sims draw first
										total_mana_spent += run_one_sim(True)
										total_mana_spent += run_one_sim(False)
									average_mana_spent = round(total_mana_spent / num_simulations , 4)
									previous_total_sims = Number_sims[ one, two, three, four, five, land]
									Number_sims[ one, two, three, four, five, land] += num_simulations
									previous_estimate = Estimation[ one, two, three, four, five, land]
									Estimation[ one, two, three, four, five, land] = round((previous_estimate * previous_total_sims + average_mana_spent * num_simulations) / Number_sims[ one, two, three, four, five, land], 4)
									current_deck_is_same_as_previous_best = (one == best_one and two == best_two and three == best_three and four == best_four and five == best_five)
									if Estimation[ one, two, three, four, five, land] >= best_mana_spent:
										firstword = "Update!" if current_deck_is_same_as_previous_best else "Improv!" if Estimation[ one, two, three, four, five, land] > previous_best_mana_spent else "-------"
										print("---"+firstword+ "Deck "+ str(one) + ", " + str(two) + ", " + str(three) + ", " + str(four) + ", " + str(five) + ", " + str(land) + " had " + str(previous_estimate) +"/"+ str(int(previous_total_sims))+", now "+str(Estimation[ one, two, three, four, five, land])+"/"+str(int(Number_sims[ one, two, three, four, five, land])))
										best_mana_spent = Estimation[ one, two, three, four, five, land]
										new_best_one = one
										new_best_two = two
										new_best_three = three
										new_best_four = four
										new_best_five = five
										new_best_land = land
										sims_for_best_deck = Number_sims[ one, two, three, four, five, land]
									if Estimation[ one, two, three, four, five, land] < best_mana_spent and Estimation[ one, two, three, four, five, land] > 0.999 * best_mana_spent:
										firstword = "Update!" if current_deck_is_same_as_previous_best else "Close! "
										print("---"+firstword+"Deck "+ str(one) + ", " + str(two) + ", " + str(three) + ", " + str(four) + ", " + str(five) + ", " + str(land) + " had " + str(previous_estimate) +"/"+ str(int(previous_total_sims))+", now "+str(Estimation[ one, two, three, four, five, land])+"/"+str(int(Number_sims[ one, two, three, four, five, land])))

	previous_still_best = (new_best_one == best_one and new_best_two == best_two and new_best_three == best_three and new_best_four == best_four and new_best_five == best_five)
	previous_best_mana_spent = best_mana_spent
	if previous_still_best and sims_for_best_deck > 200000:
		continue_searching = False
	else:
		continue_searching = True
		
	best_one = new_best_one
	best_two = new_best_two
	best_three = new_best_three
	best_four = new_best_four
	best_five = new_best_five
	best_land = new_best_land
	num_simulations += 1000
	print("====>Deck: " + str(best_one) + " one-drops, " + str(best_two) + " two, " + str(best_three) + " three, " + str(best_four) + " four, " + str(best_five) + " five, " + str(best_land) + " lands ==> "+str(best_mana_spent)+".")

print("Best options overall:")
for one in range(max(best_one - 3, 0), best_one + 3):
		for two in range(max(best_two - 3, 0), best_two + 3):
			for three in range(max(best_three - 3, 0), best_three + 3):
				for four in range(max(best_four - 3, 0), best_four + 3):
					for five in range(max(best_five - 3, 0), best_five + 3):
						for land in range(max(best_land - 3, 0), best_land + 3):
							
							companion_restriction_satisfied = True
							if companion == "Lurrus" and three + four + five > 0:
								companion_restriction_satisfied = False
							if companion == "Obosh" and two + four > 0:
								companion_restriction_satisfied = False
							if companion == "Keruga" and one + two > 0:
								companion_restriction_satisfied = False
							if companion == "Gyruda" and one + three + five > 0:
								companion_restriction_satisfied = False
							
							if one + two + three + four + five + land == deck_size and companion_restriction_satisfied:
								if Estimation[ one, two, three, four, five, land] > 0.9995 * best_mana_spent and Number_sims[ one, two, three, four, five, land] > 100000:
									print("Deck "+ str(one) + ", " + str(two) + ", " + str(three) + ", " + str(four) + ", " + str(five) + ", " + str(land) + ": " + str(Estimation[ one, two, three, four, five, land])+"/"+str(int(Number_sims[ one, two, three, four, five, land])))						

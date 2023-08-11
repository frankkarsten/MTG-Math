import random

#Manually adjust these parameters to set the deck type and an initial guess for where to start searching
#The card values should sum to 98 because we're always adding a Sol Ring
#Note that the simulation code allows for card draw spells, but these were now fixed at 0 in the optimization because early tests never favored them
deck_size = 99
commander_cost = 6
initial_rock = 9
initial_1_cmc = 6
initial_2_cmc = 12
initial_3_cmc = 10
initial_4_cmc = 14
initial_5_cmc = 9
initial_6_cmc = 0
initial_land = 38
initial_draw = 0



debug_mode = False
beat_other_mode = True

def put_spells_on_bottom(hand, spells_remaining_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		spells_remaining_to_bottom - The number of spells to bottom after a mulligan (must be <= number of spells in hand)
	Returns - nothing, it just adjusts the opening hand value by bottoming excess rocks and the most expensive spells after a mull
	"""
	#If the hand has too much mana, the first card(s) to bottom are all but one Rock
	if (hand['Rock'] >= 3) or (hand['Land'] >= 3 and hand['Rock'] >= 2):
		Bottomable_rock = min(hand['Rock'] - 1, spells_remaining_to_bottom)
		hand['Rock'] -= Bottomable_rock
		spells_remaining_to_bottom -= Bottomable_rock

	Bottomable_cmc_6 = min(hand['6 CMC'], spells_remaining_to_bottom)
	hand['6 CMC'] -= Bottomable_cmc_6
	spells_remaining_to_bottom -= Bottomable_cmc_6

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

	#Card advantage becomes more important after a mulligan, so bottom that last
	Bottomable_draw = min(hand['Draw'], spells_remaining_to_bottom)
	hand['Draw'] -= Bottomable_draw
	spells_remaining_to_bottom -= Bottomable_draw
	
	#In case of unusual all land and all rock hands, bottom the remainder
	Bottomable_rock = min(hand['Rock'], spells_remaining_to_bottom)
	hand['Rock'] -= Bottomable_rock
	spells_remaining_to_bottom -= Bottomable_rock


def nr_spells(hand):
	return hand['1 CMC'] + hand['2 CMC'] + hand['3 CMC'] + hand['4 CMC'] + hand['5 CMC'] + hand['6 CMC'] + hand['Rock'] + hand['Draw']

def nr_mana(hand):
	return hand['Land'] + hand['Rock']

def draw_random_card(library):
	total_cards = sum(library.values())
	probabilities = [count / total_cards for count in library.values()]
	
	selected_card = random.choices(list(library.keys()), weights=probabilities, k=1)[0]
	library[selected_card] -= 1
	
	return selected_card	

def run_one_sim(SolRingInOpener, decklist, commander_cost):	
	#Initialize variables
	lands_in_play = 0
	rocks_in_play = 0
	compounded_mana_spent = 0
	cumulative_mana_in_play = 0
	turn_of_interest = 7
	mana_available = 0
	mana_rock_cost = 2 #1 is Elf, 2 is Signet, 3 is Commander Sphere
	draw_cost = 1 #Cost is 3 for Divination, 4 for Harmonize
	draw_draw = 3 #Draw is 2 for Divination, 3 for Harmonize
	six_drop_value = 6.2 #Six drops are very powerful and count as 6.2 mana each (unless we consider turn 9 and/or mana Elves, then it's just 6)
	
	#Draw opening hands and mulligan
	keephand = False 
	if debug_mode:
		print("----------")

	for handsize in [(7, 'free'), 7, 6, 5, 4]:
		#We may mull free, 7, 6, or 5 cards and keep every 4-card hand
		#Once we actually keep, the variable keephand will be set to True
		if not keephand:
			
			#Contruct library as a dictionary
			library = decklist.copy()

			#Construct a random opening hand
			hand = {
				'1 CMC': 0,
				'2 CMC': 0,
				'3 CMC': 0,
				'4 CMC': 0,
				'5 CMC': 0,
				'6 CMC': 0,
				'Rock': 0,
				'Sol Ring': 0,
				'Draw': 0,
				'Land': 0
			}

			if handsize == (7, 'free') and SolRingInOpener:
				#Add Sol Ring to hand, then six at random
				library['Sol Ring'] =- 1
				hand['Sol Ring'] += 1
				for _ in range(6):
					card_drawn = draw_random_card(library)
					hand[card_drawn] += 1
			elif handsize == (7, 'free') and not SolRingInOpener:
				#Remove Sol Ring from library when drawing seven, then put it back in library
				library['Sol Ring'] =- 1
				for _ in range(7):
					card_drawn = draw_random_card(library)
					hand[card_drawn] += 1
				library['Sol Ring'] =+ 1
			else:
				#After a mulligan, no additional Sol Ring checks for now					
	 			for _ in range(7):
	 				card_drawn = draw_random_card(library)
	 				hand[card_drawn] += 1

			if debug_mode:
				print("Opening hand:", hand)

			#Check to see if we keep				
			if handsize == (7, 'free'):
				if (hand['Land'] >= 3 and hand['Land'] <= 5 and nr_mana(hand) <= 5) or (hand['Land'] >= 1 and hand['Land'] <= 5 and hand['Sol Ring'] == 1):
					keephand = True
				
			if handsize == 7:
				if (hand['Land'] >= 2 and hand['Land'] <= 5 and nr_mana(hand) <= 5) or (hand['Land'] >= 1 and hand['Land'] <= 5 and hand['Sol Ring'] == 1):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 3 land, 2 spells, 1 rock
				if nr_spells(hand) > 3:
					put_spells_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, 2, or 3 spells so we put a land on the bottom
					hand['Land'] -= 1
				#Do we keep?
				if (hand['Land'] >= 2 and hand['Land'] <= 4) or (hand['Land'] >= 1 and hand['Sol Ring'] == 1):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 1 spell, 1 rock
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
				if (hand['Land'] >= 2 and hand['Land'] <= 4) or (hand['Land'] >= 1 and hand['Sol Ring'] == 1):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 rock
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

			if debug_mode:
				print("After bottoming:", hand)
				print("Keephand:", keephand)
	
	#Add commander as a free spell
	hand[f'{commander_cost} CMC'] += 1
	if debug_mode:
		print("After adding commander:", hand)
	
	commander_sphere_in_play = 0
	
	for turn in range(1, turn_of_interest + 1):
		#For turn_of_interest = 7, this range is {1, 2, ..., 7} so we consider mana spent over the first 7 turns
		#compounded_mana_spent is what we return at the end
		#At the start of every turn, we add to it the sum of mana values of all 1-drops, 2-drops, ..., 6-drops that we have cast thus far
		#During the turn, we add to it the mana value of any 1-drop, 2-drop, ..., 6-drop we cast
		#Note that mana rocks or card draw spells don't count towards this
		
		compounded_mana_spent += cumulative_mana_in_play
		
		#In Commander, you always draw a card, even when playing first
		card_drawn = draw_random_card(library)
		hand[card_drawn] += 1
		
		#Play a land if possible
		land_played = False
		if (hand['Land'] > 0):
			hand['Land'] -= 1
			lands_in_play += 1
			land_played = True
		
		mana_available = lands_in_play + rocks_in_play
		mana_available_at_start_turn = mana_available
		we_cast_a_nonrock_spell_this_turn = False
		
		if debug_mode:
			print(f"TURN {turn}. Card drawn {card_drawn}. {lands_in_play} lands, {rocks_in_play} rocks. Mana available {mana_available}. Cumulative mana {compounded_mana_spent}. Hand:", hand)
		
		if (turn == 1):
			#lucky = 1 if hand['Sol Ring'] == 1 else 0
			if (mana_available >= 1) and hand['Sol Ring'] == 1:
				hand['Sol Ring'] -= 1
				#Sol Ring counts as 2 mana rocks
				rocks_in_play += 2
				#Also cast Signet if possible
				if hand['Rock'] >= 1 and mana_rock_cost == 2:
					hand['Rock'] -= 1
					rocks_in_play += 1
				mana_available = 0
				#We can't do anything else after a turn one Sol Ring
				#We are assumed to have colored spells in hand, and if the Signet is a Boros Signet then it can't tap
		
		if turn >= 2:
			if (mana_available >= 1) and hand['Sol Ring'] == 1:
				hand['Sol Ring'] -= 1
				#Costs one mana, immediately adds two. Card is utterly broken
				mana_available += 1
				rocks_in_play += 2
			
		if turn in [1, 2] and mana_rock_cost == 1:
			#Cast an Elf
			Castable_rock = min(hand['Rock'], mana_available // mana_rock_cost)
			hand['Rock'] -= Castable_rock
			#Rocks cost 1 each
			mana_available -= Castable_rock
			rocks_in_play += Castable_rock
			#Rocks DO NOT count as mana spent or mana in play. Mana in play represents creatures, planeswalkers, etc. Rocks are like lands

		if (turn == 2) and mana_rock_cost == 2:
			Castable_rock = min(hand['Rock'], mana_available // mana_rock_cost)
			hand['Rock'] -= Castable_rock
			#Rocks cost 2 each, then tap for 1 each
			mana_available -= Castable_rock * mana_rock_cost
			mana_available += Castable_rock
			rocks_in_play += Castable_rock
			#Rocks DO NOT count as mana spent or mana in play. Mana in play represents creatures, planeswalkers, etc. Rocks are like lands
		
		if (turn == 3) and mana_rock_cost == 3:
			Castable_rock = min(hand['Rock'], mana_available // mana_rock_cost)
			hand['Rock'] -= Castable_rock
			#Rocks cost 3 each, then tap for 1 each
			mana_available -= Castable_rock * mana_rock_cost
			mana_available += Castable_rock
			rocks_in_play += Castable_rock
			commander_sphere_in_play += Castable_rock
			#Rocks DO NOT count as mana spent or mana in play. Mana in play represents creatures, planeswalkers, etc. Rocks are like lands

		#On turn 3 or 4, cast a mana rock and a (mana available - 1) drop if possible
		if turn in [3, 4] and mana_available >= max(2, mana_rock_cost) and mana_available <= 7:
			#Artifacts tap for mana right away but Elves don't
			cmc_of_followup_spell = mana_available + 1 - mana_rock_cost if mana_rock_cost in [2, 3] else mana_available - 1
			if hand['Rock'] >= 1 and hand[f'{cmc_of_followup_spell} CMC'] >= 1:
				hand['Rock'] -= 1
				mana_available +=  1 - mana_rock_cost if mana_rock_cost in [2, 3] else  -1
				rocks_in_play += 1
				hand[f'{cmc_of_followup_spell} CMC'] -= 1
				mana_available -= cmc_of_followup_spell
				compounded_mana_spent += cmc_of_followup_spell
				cumulative_mana_in_play += cmc_of_followup_spell
				we_cast_a_nonrock_spell_this_turn = True
		
		if debug_mode:
			print(f"After rocks, mana available {mana_available}. Cumulative mana {compounded_mana_spent}. Hand:", hand)
		
		if mana_available >= 3 and mana_available <= 6:
			if hand[f'{mana_available} CMC'] == 0:
				#We have, for example, 5 mana but don't have a 5-drop in hand
				#But let's check if we can cast a 2 and a 3 before checking for 4s
				#Since mana_available - 2 could be 2, we also gotta check if the cards are distinct
				if (mana_available -2 != 2 and hand['2 CMC'] >= 1 and hand[f'{mana_available - 2} CMC'] >= 1) or (mana_available -2 == 2 and hand['2 CMC'] >= 2):
					hand['2 CMC'] -= 1
					hand[f'{mana_available - 2} CMC'] -= 1
					compounded_mana_spent += mana_available
					cumulative_mana_in_play += mana_available
					mana_available = 0
					we_cast_a_nonrock_spell_this_turn = True
		
		Castable_cmc_6 = min(hand['6 CMC'], mana_available // 6)
		hand['6 CMC'] -= Castable_cmc_6
		mana_available -= Castable_cmc_6 * 6
		#Six drops are very powerful and count as 6.2 mana each
		compounded_mana_spent += Castable_cmc_6 * six_drop_value
		cumulative_mana_in_play += Castable_cmc_6 * six_drop_value

		Castable_cmc_5 = min(hand['5 CMC'], mana_available // 5)
		hand['5 CMC'] -= Castable_cmc_5
		mana_available -= Castable_cmc_5 * 5
		compounded_mana_spent += Castable_cmc_5 * 5
		cumulative_mana_in_play += Castable_cmc_5 * 5
		
		Castable_cmc_4 = min(hand['4 CMC'], mana_available // 4)
		hand['4 CMC'] -= Castable_cmc_4
		mana_available -= Castable_cmc_4 * 4
		compounded_mana_spent += Castable_cmc_4 * 4
		cumulative_mana_in_play += Castable_cmc_4 * 4

		Castable_cmc_3 = min(hand['3 CMC'], mana_available // 3)
		hand['3 CMC'] -= Castable_cmc_3
		mana_available -= Castable_cmc_3 * 3
		compounded_mana_spent += Castable_cmc_3 * 3
		cumulative_mana_in_play += Castable_cmc_3 * 3
		
		Castable_cmc_2 = min(hand['2 CMC'], mana_available // 2)
		hand['2 CMC'] -= Castable_cmc_2
		mana_available -= Castable_cmc_2 * 2
		compounded_mana_spent += Castable_cmc_2 * 2
		cumulative_mana_in_play += Castable_cmc_2 * 2
		
		Castable_cmc_1 = min(hand['1 CMC'], mana_available // 1)
		hand['1 CMC'] -= Castable_cmc_1
		mana_available -= Castable_cmc_1 * 1
		compounded_mana_spent += Castable_cmc_1 * 1
		cumulative_mana_in_play += Castable_cmc_1 * 1

		Castable_rock = min(hand['Rock'], mana_available // mana_rock_cost)
		hand['Rock'] -= Castable_rock
		mana_available -= Castable_rock * mana_rock_cost
		mana_available += Castable_rock if mana_rock_cost in [2, 3] else 0
		rocks_in_play += Castable_rock
		if mana_rock_cost == 3:
			commander_sphere_in_play += Castable_rock

		if Castable_cmc_6 >= 1 or Castable_cmc_5 >= 1 or Castable_cmc_4 >= 1 or Castable_cmc_3 >= 1 or Castable_cmc_2 >= 1 or Castable_cmc_1 >= 1:
			we_cast_a_nonrock_spell_this_turn = True

		#If we retroactively notice we could've snuck in a mana rock, do so
		if (mana_available_at_start_turn >= 2 and mana_available == 1) and hand['Rock'] >= 1 and mana_rock_cost == 2 and we_cast_a_nonrock_spell_this_turn:
			hand['Rock'] -= 1
			rocks_in_play += 1
			mana_available =- 1
		if (mana_available_at_start_turn >= 3 and mana_available == 2) and hand['Rock'] >= 1 and mana_rock_cost == 3 and we_cast_a_nonrock_spell_this_turn:
			hand['Rock'] -= 1
			rocks_in_play += 1
			mana_available =- 2
			commander_sphere_in_play += Castable_rock
			
		#Finally, cast a card draw spell or sac a Commander Sphere
		if (draw_cost <= mana_available and hand['Draw'] >= 1) or (commander_sphere_in_play >= 1 and mana_available >= 6):
			if (draw_cost <= mana_available and hand['Draw'] >= 1):
				hand['Draw'] -= 1
				mana_available -= draw_cost
				for _ in range (draw_draw):
					card_drawn = draw_random_card(library)
					hand[card_drawn] += 1

			if (commander_sphere_in_play >= 1 and mana_available >= 6):
				rocks_in_play -= 1
				commander_sphere_in_play -= 1
				card_drawn = draw_random_card(library)
				hand[card_drawn] += 1

			if not land_played and hand['Land'] >= 1:
				hand['Land'] -= 1
				lands_in_play += 1
				mana_available += 1
				land_played = True

			#Afterwards, cast spells
			if (mana_available >= 1) and hand['Sol Ring'] == 1:
				hand['Sol Ring'] -= 1
				#Costs one mana, immediately adds two. Card is utterly broken
				mana_available += 1
				rocks_in_play += 2

			Castable_cmc_6 = min(hand['6 CMC'], mana_available // 6)
			hand['6 CMC'] -= Castable_cmc_6
			mana_available -= Castable_cmc_6 * 6
			compounded_mana_spent += Castable_cmc_6 * six_drop_value
			cumulative_mana_in_play += Castable_cmc_6 * six_drop_value
	
			Castable_cmc_5 = min(hand['5 CMC'], mana_available // 5)
			hand['5 CMC'] -= Castable_cmc_5
			mana_available -= Castable_cmc_5 * 5
			compounded_mana_spent += Castable_cmc_5 * 5
			cumulative_mana_in_play += Castable_cmc_5 * 5
			
			Castable_cmc_4 = min(hand['4 CMC'], mana_available // 4)
			hand['4 CMC'] -= Castable_cmc_4
			mana_available -= Castable_cmc_4 * 4
			compounded_mana_spent += Castable_cmc_4 * 4
			cumulative_mana_in_play += Castable_cmc_4 * 4
	
			Castable_cmc_3 = min(hand['3 CMC'], mana_available // 3)
			hand['3 CMC'] -= Castable_cmc_3
			mana_available -= Castable_cmc_3 * 3
			compounded_mana_spent += Castable_cmc_3 * 3
			cumulative_mana_in_play += Castable_cmc_3 * 3
			
			Castable_cmc_2 = min(hand['2 CMC'], mana_available // 2)
			hand['2 CMC'] -= Castable_cmc_2
			mana_available -= Castable_cmc_2 * 2
			compounded_mana_spent += Castable_cmc_2 * 2
			cumulative_mana_in_play += Castable_cmc_2 * 2
			
			Castable_cmc_1 = min(hand['1 CMC'], mana_available // 1)
			hand['1 CMC'] -= Castable_cmc_1
			mana_available -= Castable_cmc_1 * 1
			compounded_mana_spent += Castable_cmc_1 * 1
			cumulative_mana_in_play += Castable_cmc_1 * 1
	
			Castable_rock = min(hand['Rock'], mana_available // mana_rock_cost)
			hand['Rock'] -= Castable_rock
			mana_available -= Castable_rock * mana_rock_cost
			mana_available += Castable_rock if mana_rock_cost in [2, 3] else 0
			rocks_in_play += Castable_rock
		
		if debug_mode:
			print(f"After spells, mana available {mana_available}. Cumulative mana {compounded_mana_spent}. Hand:", hand)
	#Return lucky (True if you had Sol Ring on turn 1) to enable better rare event simulation with reduced variance, although that part was cut for time reasons
	return compounded_mana_spent


#Initialize local search algorithm
num_simulations = 10000
best_one = initial_1_cmc 
best_two = initial_2_cmc 
best_three = initial_3_cmc 
best_four = initial_4_cmc 
best_five = initial_5_cmc
best_six = initial_6_cmc
best_rock = initial_rock
best_land = initial_land
best_draw = initial_draw 
previous_best_mana_spent = 0
previous_sims_for_best_deck = 0
sims_for_best_deck = 0
continue_searching = True

#We'll store and update the results for various decks in two dictionaries
Estimation = {}
Number_sims = {}

#Start the local search
#We start at a given initial feasible solution and we keep moving to better points in a neighborhood until no better point exists. 
#Then we have reached a local optimum. We need a certain number of simulations before we can "safely" stop.
#Neighborhood of a deck X, when the last nr sims for the best deck is < 150000: 
	#all possible decks where the sum of the the absolute values of the difference with X is at most one.
#Neighborhood of a deck X, when the last nr sims for the best deck is >= 150000: 
	#all possible 99-card decks where for each card type, the absolute values of the difference with the number of copies of that card type in X is at most one.
#We start with a limited number of simulations (num_simulations, 3000) as we explore and increase the number of simulations in every step
#If we have to re-evaluate a deck, we combine the simulations from the current iterations with the ones that have already taken place prior.


def get_true_false(prob_true, prob_false):
    random_number = random.uniform(0, 1)
    
    if random_number < prob_true:
        return True
    else:
        return False

while continue_searching:
	best_mana_spent = 0

	if beat_other_mode:
		opp_commander = 4 
		opp_decklist = {
		'1 CMC': 6,
		'2 CMC': 12,
		'3 CMC': 13,
		'4 CMC': 0,
		'5 CMC': 13,
		'6 CMC': 8,
		'Rock': 7,
		'Sol Ring': 1,
		'Draw': 0,
		'Land': 39
		}	
		opposing_compounded_mana_to_beat_list = []
		for _ in range(int(num_simulations/10)):
			opp_1 = run_one_sim(True, opp_decklist, opp_commander) if random.uniform(0, 1) <= 7/99.0 else run_one_sim(False, opp_decklist, opp_commander)
			opp_2 = run_one_sim(True, opp_decklist, opp_commander) if random.uniform(0, 1) <= 7/99.0 else run_one_sim(False, opp_decklist, opp_commander)
			opp_3 = run_one_sim(True, opp_decklist, opp_commander) if random.uniform(0, 1) <= 7/99.0 else run_one_sim(False, opp_decklist, opp_commander)
			max_opp_compounded_mana_spent = max(opp_1, opp_2, opp_3)
			opposing_compounded_mana_to_beat_list.append(max_opp_compounded_mana_spent)
			#print(opposing_compounded_mana_to_beat_list)
			
	improvement_possible = False
	for one in range(max(best_one - 1, 0), best_one + 2):
		for two in range(max(best_two - 1, 0), best_two + 2):
			for three in range(max(best_three - 1, 0), best_three + 2):
				for four in range(max(best_four - 1, 0), best_four + 2):
					for five in range(max(best_five - 1, 0), best_five + 2):
						for six in range(max(best_six - 1, 0), best_six + 2):
							for rock in range(max(best_rock - 1, 0), best_rock + 2):
								for draw in [0]:
								#[0]: #This could vary initially,  range(max(best_draw - 1, 0), best_draw + 2), but was later fixed at 0 to greatly reduce optimization time
									for land in range(max(best_land - 1, 0), best_land + 2):
								
										#We are now considering a new deck; is this actually in the neighborhood of the previous best deck?
										nr_changes = abs(one - best_one) + abs(two - best_two) + abs(three - best_three) + abs(four - best_four)
										nr_changes += abs(five - best_five) + abs(six - best_six) + abs(rock - best_rock) + abs(draw - best_draw) + abs(land - best_land)
										if previous_sims_for_best_deck < 150000:
											in_neighborhood = one + two + three + four + five + six + rock + draw + land == deck_size - 1 and nr_changes <= 2 
										else:
											in_neighborhood = one + two + three + four + five + six + rock + draw + land == deck_size - 1 
										#Note that we check for deck_size -1 because Sol Ring is always part of the deck
									
										if in_neighborhood: 
										
											decklist = {
												'1 CMC': one,
												'2 CMC': two,
												'3 CMC': three,
												'4 CMC': four,
												'5 CMC': five,
												'6 CMC': six,
												'Rock': rock,
												'Sol Ring': 1,
												'Draw': draw,
												'Land': land
											}
											
											if (one, two, three, four, five, six, rock, draw, land) not in Estimation.keys():
												Estimation[one, two, three, four, five, six, rock, draw, land] = 0
											if (one, two, three, four, five, six, rock, draw, land) not in Number_sims.keys():
												Number_sims[one, two, three, four, five, six, rock, draw, land] = 0
	
											#If we know from previous iterations that this deck is performing not even close to the best deck, then don't waste more sims
											dont_bother = False
											if (Number_sims[ one, two, three, four, five, six, rock, draw, land] > 50000 and Estimation[ one, two, three, four, five, six, rock, draw, land] < 0.998 * previous_best_mana_spent):
												dont_bother = True
											if (Number_sims[ one, two, three, four, five, six, rock, draw, land] > 100000 and Estimation[ one, two, three, four, five, six, rock, draw, land] < 0.999 * previous_best_mana_spent):
												dont_bother = True
											if (Number_sims[ one, two, three, four, five, six, rock, draw, land] > 200000 and Estimation[ one, two, three, four, five, six, rock, draw, land] < 0.9995 * previous_best_mana_spent):
												dont_bother = True
												
											if not dont_bother:
												total_mana_spent = 0.0
												lucky_games = int(num_simulations * 7/99) #these are the games where the first opening hand has Sol Ring
												unlucky_games = num_simulations - lucky_games #these are the games where the first opening hand does NOT have Sol Ring
												for i in range(lucky_games):
													mana_spent_in_sim = run_one_sim(True, decklist, commander_cost)
													if beat_other_mode:
														to_beat = opposing_compounded_mana_to_beat_list[int(i/10)]
														if mana_spent_in_sim > to_beat:
															total_mana_spent += 1
															#total_mana_spent now gets the interpretation of the number of games you won
													else:
														total_mana_spent += mana_spent_in_sim
												for i in range(lucky_games, lucky_games + unlucky_games):
													mana_spent_in_sim = run_one_sim(False, decklist, commander_cost)
													if beat_other_mode:
														to_beat = opposing_compounded_mana_to_beat_list[int(i/10)]
														if mana_spent_in_sim > to_beat:
															total_mana_spent += 1
															#total_mana_spent now gets the interpretation of the number of games you won
													else:
														total_mana_spent += mana_spent_in_sim
												average_mana_spent = round(total_mana_spent / num_simulations , 4)
												#Add previous total sims to current number sims
												previous_total_sims = Number_sims[ one, two, three, four, five, six, rock, draw, land]
												Number_sims[ one, two, three, four, five, six, rock, draw, land] += num_simulations
												#Take nr_sim-weighted combination of previous estimation and current estimation
												previous_estimate = Estimation[ one, two, three, four, five, six, rock, draw, land]
												Estimation[ one, two, three, four, five, six, rock, draw, land] = round((previous_estimate * previous_total_sims + average_mana_spent * num_simulations) / Number_sims[ one, two, three, four, five, six, rock, draw, land], 4)
												
												current_deck_is_same_as_previous_best = (one == best_one and two == best_two and three == best_three and four == best_four and five == best_five and six == best_six and rock == best_rock and draw == best_draw)
												
												#Are we doing better than the previuos best deck?
												if Estimation[ one, two, three, four, five, six, rock, draw, land] >= best_mana_spent:
													firstword = "Update!" if current_deck_is_same_as_previous_best else "Improv!" if Estimation[ one, two, three, four, five, six, rock, draw, land] >= previous_best_mana_spent else "-------"
													print("---"+firstword+ "Deck "+ str(one) + ", " + str(two) + ", " + str(three) + ", " + str(four) + ", " + str(five) + ", " + str(six) + " | " + str(draw) + ", " + str(rock) + ", " + str(land) + " had " + str(previous_estimate) +"/"+ str(int(previous_total_sims))+", now "+str(Estimation[ one, two, three, four, five, six, rock, draw, land])+"/"+str(int(Number_sims[ one, two, three, four, five, six, rock, draw, land])))
													best_mana_spent = Estimation[ one, two, three, four, five, six, rock, draw, land]
													new_best_one = one
													new_best_two = two
													new_best_three = three
													new_best_four = four
													new_best_five = five
													new_best_six = six
													new_best_rock = rock
													new_best_draw = draw
													new_best_land = land
													sims_for_best_deck = Number_sims[ one, two, three, four, five, six, rock, draw, land]
												elif Estimation[ one, two, three, four, five, six, rock, draw, land] < previous_best_mana_spent and Estimation[ one, two, three, four, five, six, rock, draw, land] > 0.998 * best_mana_spent:
													firstword = "Update!" if current_deck_is_same_as_previous_best else "Close! "
													print("---"+firstword+"Deck "+ str(one) + ", " + str(two) + ", " + str(three) + ", " + str(four) + ", " + str(five) + ", " + str(six) + " | " + str(draw) + ", " + str(rock) + ", " + str(land) + " had " + str(previous_estimate) +"/"+ str(int(previous_total_sims))+", now "+str(Estimation[ one, two, three, four, five, six, rock, draw, land])+"/"+str(int(Number_sims[ one, two, three, four, five, six, rock, draw, land])))

	previous_still_best = (new_best_one == best_one and new_best_two == best_two and new_best_three == best_three and new_best_four == best_four and new_best_five == best_five and new_best_six == best_six and new_best_rock == best_rock and new_best_draw == best_draw)
	previous_best_mana_spent = best_mana_spent
	if previous_still_best and sims_for_best_deck > 200000:
		continue_searching = False
	else:
		continue_searching = True
		
	#Move to the best option we've seen in the immediate neighborhood
	best_one = new_best_one
	best_two = new_best_two
	best_three = new_best_three
	best_four = new_best_four
	best_five = new_best_five
	best_six = new_best_six
	best_rock = new_best_rock
	best_draw = new_best_draw
	best_land = new_best_land
	
	#However, check if we've seen a better option with reasonable sample size in previous iterations; if so, override
	for (one, two, three, four, five, six, rock, draw, land) in Estimation.keys():
		if Estimation[ one, two, three, four, five, six, rock, draw, land] > best_mana_spent and Number_sims[ one, two, three, four, five, six, rock, draw, land] >= previous_sims_for_best_deck / 2:
			previous_best_mana_spent = Estimation[ one, two, three, four, five, six, rock, draw, land]
			best_mana_spent = Estimation[ one, two, three, four, five, six, rock, draw, land]
			best_one = one
			best_two = two
			best_three = three
			best_four = four
			best_five = five
			best_six = six
			best_rock = rock
			best_draw = draw
			best_land = land
			sims_for_best_deck = Number_sims[ one, two, three, four, five, six, rock, draw, land]
			print("!!!!!!!!!OVERRIDE!!!!!!!")
			continue_searching = True
			
	num_simulations += 1000
	previous_sims_for_best_deck = sims_for_best_deck
	print("====>Deck: " + str(best_one) + " one-drops, " + str(best_two) + " two, " + str(best_three) + " three, " + str(best_four) + " four, " + str(best_five) + " five, " + str(best_six) + " six, " + str(best_draw) + " Harmonize, "+ str(best_rock) + " Signet, 1 Sol Ring, " + str(best_land) + " lands ==> "+str(best_mana_spent)+".")
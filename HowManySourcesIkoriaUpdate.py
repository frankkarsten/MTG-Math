import random
OF = open('OutputFile.txt', 'w')

def printing(text):
	print(text)
	OF.write(text + "\n")

def put_lands_on_bottom(hand, lands_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		lands_to_bottom - The number of lands to bottom (must be <= number of lands in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	Bottomable_other_lands = min(hand['Other Land'], lands_to_bottom)
	hand['Other Land'] -= Bottomable_other_lands

	Bottomable_good_lands = min(hand['Good Land'], lands_to_bottom - Bottomable_other_lands)
	hand['Good Land'] -= Bottomable_good_lands

def total_lands(hand):
	return hand['Good Land'] + hand['Other Land']
	
def run_one_sim():	
	#We will look for the probability of casting a spell with CMC TurnAllowed on turn TurnAllowed that requires NrGoodLandsNeeded colored mana of a certain color in its cost.
	#For example, for a 2WW Wrath of God, we use TurnAllowed=4 and NrGoodLandsNeeded=2. As a requirement, NrGoodLandsNeeded <= TurnAllowed must always hold.

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
				'Good Land': 0,
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
				#We have to bottom. Ideal would be 4 land, 2 spells
				if hand['Spell'] > 2:
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, or 2 spells so we put a land on the bottom
					put_lands_on_bottom(hand, 1)
				#Do we keep?
				if (total_lands(hand) >= 2 and total_lands(hand) <= 4):
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
				if (total_lands(hand) >= 2 and total_lands(hand) <= 4):
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
	
	for turn in range(2, turn_allowed + 1):
		#If, e.g., turn_allowed is 4 then this range is {2, 3, 4}
		#We skip draw in turn 1 because we're always on the play
		card_drawn = library.pop(0)
		hand[card_drawn] += 1

	if total_lands(hand) >= turn_allowed and hand['Good Land'] >= good_lands_needed:
		return 'Success'
	if total_lands(hand) >= turn_allowed and hand['Good Land'] < good_lands_needed:
		return 'Failure'
	if total_lands(hand) < turn_allowed:
		return 'Irrelevant for conditioning'

num_simulations = 100
#Uncertainty with five million simulations will be about +/- 0.03%

nr_lands = {
	40: 17,
	60: 24,
	80: 34,
	99: 40
}

nr_good_lands = {
	40: range(3, 17 +1),
	60: range(6, 24 +1),
	80: range(8, 34 +1),
	99: range(10, 40 +1)
}

for deck_size in [40, 60, 80, 99]:
	printing("===> We now consider decks of size " + str(deck_size))
	for turn_allowed in range(1, 8):
		good_lands_range = [1, 2, 3, 4] if turn_allowed == 4 else [2, 3] if turn_allowed == 7 else range(1, min(4, turn_allowed +1))
		for good_lands_needed in good_lands_range:
			casting_cost = str(turn_allowed - good_lands_needed) + 'C' * good_lands_needed if turn_allowed - good_lands_needed > 0 else 'C' * good_lands_needed
			printing(f"--Next, the probability to cast a {casting_cost} spell on-curve in a {deck_size}-card deck")
			printing(f"--One row per number of colored sources")
			printing(f"--First row is {min(nr_good_lands[deck_size])} sources; last row is {max(nr_good_lands[deck_size])} sources")
			for good_lands_in_deck in nr_good_lands[deck_size]:
				decklist = {
					'Spell': deck_size - nr_lands[deck_size],
					'Good Land': good_lands_in_deck,
					'Other Land': nr_lands[deck_size] - good_lands_in_deck
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
				printing(f"{num_success / num_relevant_games *100:.2f}%")

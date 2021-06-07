'''
MULLIGAN RULE: Consider a red-blue deck.
• A 7-card hand is kept if it has 2, 3, 4, or 5 lands.
• For a mulligan to 6, we first choose what to put on the bottom and decide keep or mull afterwards. 
	To get a good mix, we bottom a spell if we drew 4+ spells and we bottom a land if we drew 4+ lands. 	
	Afterwards, we keep if we hold 2, 3, or 4 lands. Otherwise, we mulligan.
• When bottoming lands, we might choose between Mines, Mountains, duals, and Islands. 
	We always keep a potential Mine, and then favor as many duals as possible.
	We keep one Island if we didn't add a dual yet but bottom additional Islands as much as possible. 
	Finally we put Mountains on the bottom if needed.
• For a mulligan to 5, we try to get close to 3 lands and 2 spells. 
	So we bottom two spells if we drew 4+ spells, we bottom a spell and a land if we drew 3 spells, and we bottom two lands if we drew 2 spells. 
	Afterwards, we keep if we have 2, 3, or 4 lands; otherwise, we mulligan.
• For a mulligan to 4, we try to get close to 3 lands and 1 spell. Then we always keep.
'''


import random
from collections import Counter

num_simulations = 1000000

def put_lands_on_bottom(hand, lands_remaining_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		lands_remaining_to_bottom - The number of lands to bottom (<= number of lands in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	if hand['Dual'] == 0:
		#Keep one Island if possible but bottom additional Island as much as possible
		island_to_bottom = min( max(hand['Island'] -1, 0), lands_remaining_to_bottom )
	else:
		#Bottom Islands as much as possible
		island_to_bottom = min( hand['Island'], lands_remaining_to_bottom )
	hand['Island'] -= island_to_bottom
	lands_remaining_to_bottom -= island_to_bottom
	#If we still need to bottom some lands, then bottom Mountains as much as needed
	mountain_to_bottom = min( hand['Mountain'], lands_remaining_to_bottom )
	hand['Mountain'] -= mountain_to_bottom
	lands_remaining_to_bottom -= mountain_to_bottom
	#If we still need to bottom some lands, then bottom duals as much as needed
	dual_to_bottom = min( hand['Dual'], lands_remaining_to_bottom )
	hand['Dual'] -= dual_to_bottom
	lands_remaining_to_bottom -= dual_to_bottom
	#If we still need to bottom some lands, then bottom Mines as much as needed
	mine_to_bottom = min( hand['Dwarven Mine'], lands_remaining_to_bottom )
	hand['Dwarven Mine'] -= mine_to_bottom

def put_spells_on_bottom(hand, spells_remaining_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		spells_remaining_to_bottom - The number of spells to bottom (<= number of spells in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	other_spell_to_bottom = min( hand['Spell'], spells_remaining_to_bottom )
	hand['Spell'] -= other_spell_to_bottom
	spells_remaining_to_bottom -= other_spell_to_bottom
	#If we still need to bottom some lands, then bottom Brainstorms as much as needed
	brainstorm_to_bottom = min( hand['Brainstorm'], spells_remaining_to_bottom )
	hand['Brainstorm'] -= brainstorm_to_bottom
	

def nr_lands(hand):
	return hand['Mountain'] + hand['Island'] + hand['Dual'] + hand['Dwarven Mine']

def run_one_sim(decklist, sim_type = 'Mine'):	
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
				'Mountain': 0,
				'Island': 0,
				'Dual': 0,
				'Dwarven Mine': 0,
				'Brainstorm': 0,
				'Spell': 0
			}
			
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1

			if handsize == 7:
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 5):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 3 land, 3 spells
				if nr_lands(hand) > 3:
					put_lands_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, 2, or 3 lands so we put a spell on the bottom
					put_spells_on_bottom(hand, 1)
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if nr_lands(hand) <= 3:
					#Two spells on the bottom
					put_spells_on_bottom(hand, 2)
				elif nr_lands(hand) == 4:
					#One land, one spell on the bottom
					put_spells_on_bottom(hand, 1)
					put_lands_on_bottom(hand, 1)
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					put_lands_on_bottom(hand, 2)
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if nr_lands(hand) <= 3:
					put_spells_on_bottom(hand, 3)
				elif nr_lands(hand) == 4:
					put_spells_on_bottom(hand, 2)
					put_lands_on_bottom(hand, 1)
				elif nr_lands(hand) == 5:
					put_spells_on_bottom(hand, 1)
					put_lands_on_bottom(hand, 2)
				else:
					put_lands_on_bottom(hand, 3)
				#Do we keep?
				keephand = True
	
	if sim_type == 'Opening hand':
		blue_sources_in_opener = hand['Island'] + hand['Dual']
		return 'Blue' if blue_sources_in_opener > 0 else 'No'
	
	battlefield = {
		'Mountain': 0,
		'Dwarven Mine': 0,
		'Dual': 0
	}
	
	for turn in [1, 2, 3, 4]:
		draw_a_card = True if (turn == 1 and random.random() < 0.5) or (turn > 1) else False
		if (draw_a_card):
			card_drawn = library.pop(0)
			hand[card_drawn] += 1
		#Play a Brainstorm (on turn 2 or 3, cause Triomes make this tough on turn 1)
		if (turn == 2 or turn == 3) and hand['Brainstorm'] > 0 and battlefield['Dual'] > 0:
			hand['Brainstorm'] -= 1
			card_drawn = library.pop(0)
			hand[card_drawn] += 1
			card_drawn = library.pop(0)
			hand[card_drawn] += 1
		#Play a land. No point in playing an Island for the purpose of this calculation
		if turn < 4:
			if hand['Dual'] > 0:
				hand['Dual'] -= 1
				battlefield['Dual'] += 1
			elif hand['Mountain'] > 0:
				hand['Mountain'] -= 1
				battlefield['Mountain'] += 1
			elif hand['Dwarven Mine'] > 0:
				hand['Dwarven Mine'] -= 1
				battlefield['Dwarven Mine'] += 1
	#Now we're in turn 4, ready to play a land
	if (hand['Dwarven Mine'] + battlefield['Dwarven Mine'] == 0):
		Outcome = 'No Mine'
	if hand['Dwarven Mine'] + battlefield['Dwarven Mine']> 0 and battlefield['Mountain'] + battlefield['Dual'] + battlefield['Dwarven Mine'] >= 3 and hand['Dwarven Mine'] > 0:
		Outcome = 'Three Mountains'
	if hand['Dwarven Mine'] + battlefield['Dwarven Mine'] > 0 and (battlefield['Mountain'] + battlefield['Dual'] + battlefield['Dwarven Mine'] < 3 or hand['Dwarven Mine'] == 0):
		Outcome = 'Not enough Mountains'
	return Outcome

def determine_prob(decklist):

	print("-----------------")
	print(decklist)	

	print("We now consider the probability to draw 3 Mountain by turn 4, conditional on drawing a Dwarven Mine")
	
	#For Dwarven Mine purposes, treat Fabled Passage as a Mountain
	passages = decklist['Fabled Passage']
	decklist['Mountain'] += passages
	decklist['Fabled Passage'] = 0
	
	total_relevant_games = 0.0
	total_favorable_games = 0.0
		
	for _ in range(num_simulations):
		Outcome = run_one_sim(decklist)
		if (Outcome == "Not enough Mountains"):
			total_relevant_games += 1
		if (Outcome == "Three Mountains"):
			total_relevant_games += 1
			total_favorable_games += 1
	
	print("Probability:" +str(round(total_favorable_games / total_relevant_games * 100.0 ,1))+"%.")

	print("We now consider the probability that a keepable opening hand contains a blue source")

	#For opening hand purposes, treat Fabled Passage as a Island
	decklist['Mountain'] -= passages
	decklist['Island'] += passages
	
	total_relevant_games = 0.0
	total_favorable_games = 0.0
	for _ in range(num_simulations):
		Outcome = run_one_sim(decklist, sim_type = 'Opening hand')
		if (Outcome == "No"):
			total_relevant_games += 1
		if (Outcome == "Blue"):
			total_relevant_games += 1
			total_favorable_games += 1
	print("Probability:" +str(round(total_favorable_games / total_relevant_games * 100.0 ,1))+"%.")
	
	
SamPardee_decklist = {
	'Mountain': 6,
	'Island': 4,
	'Fabled Passage': 4,
	'Dual': 8,
	'Dwarven Mine': 4,
	'Brainstorm': 4,
	'Spell': 30
}
determine_prob(SamPardee_decklist)

JohnGirardot_decklist = {
	'Mountain': 4,
	'Island': 4,
	'Dual': 8,
	'Fabled Passage': 4,
	'Dwarven Mine': 4,
	'Brainstorm': 4,
	'Spell': 32
}
determine_prob(JohnGirardot_decklist)

SperlingNettles_decklist = {
	'Mountain': 6,
	'Island': 2,
	'Dual': 10,
	'Fabled Passage': 3,
	'Dwarven Mine': 4,
	'Brainstorm': 4,
	'Spell': 31
}
determine_prob(SperlingNettles_decklist)

RaphLevy_decklist = {
	'Mountain': 6,
	'Island': 3,
	'Dual': 9,
	'Fabled Passage': 3,
	'Dwarven Mine': 4,
	'Brainstorm': 4,
	'Spell': 31
}
determine_prob(RaphLevy_decklist)
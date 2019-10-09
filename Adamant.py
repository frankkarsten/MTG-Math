'''
MULLIGAN RULE: Consider a red-green deck that tries to exploit the red adamant spells or lands.
• A 7-card hand is kept if it has 2, 3, 4, or 5 lands and at least one land of each color, and it’s mulliganed otherwise. 
	The “both color” requirement is waived if that color is only a minor splash, i.e., when you run 6 or fewer lands of that color.
• For a mulligan to 6, we first choose what to put on the bottom and decide keep or mull afterwards. 
	To get a good mix, we bottom a spell if we drew 4+ spells and we bottom a land if we drew 4+ lands. 	
	Afterwards, we keep if we hold 2, 3, or 4 lands. Otherwise, we mulligan.
• When bottoming lands, we might choose between Mines, Mountains, and Forests. 
	We always keep a potential Mine. 
	We keep one Forest if possible but bottom additional Forests as much as possible. 
	Finally we put Mountains on the bottom if needed.
• For a mulligan to 5, we try to get close to 3 lands and 2 spells. 
	So we bottom two spells if we drew 4+ spells, we bottom a spell and a land if we drew 3 spells, and we bottom two lands if we drew 2 spells. 
	Afterwards, we keep if we have 2, 3, or 4 lands; otherwise, we mulligan.
• For a mulligan to 4, we try to get close to 3 lands and 1 spell. Then we always keep.
'''


import random
from collections import Counter

num_simulations = 1000000
#Uncertainty with this many simulations will be about +/- 0.2%

def put_lands_on_bottom(hand, lands_remaining_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		lands_remaining_to_bottom - The number of lands to bottom (>= number of lands in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	#Keep one Forest if possible but bottom additional Forests as much as possible
	forest_to_bottom = min( max(hand['Forest'] -1, 0), lands_remaining_to_bottom )
	hand['Forest'] -= forest_to_bottom
	lands_remaining_to_bottom -= forest_to_bottom
	#If we still need to bottom some lands, then bottom Mountains as much as needed
	hand['Mountain'] -= lands_remaining_to_bottom
	#Since, in case we're interested in Dwarven Mine, the decklist only has one Dwarven Mine and we never bottom all lands, we never bottom it
	
def nr_lands(hand):
	return hand['Mountain'] + hand['Forest'] + hand['Dwarven Mine']

def run_one_sim(sim_type):	
	"""
	sim_type should be "Adamant" to condition on drawing at least turn_of_interest lands and an adamant spell by turn turn_of_interest
	sim_type should be "Mine" to condition on drawing at at least a Dwarven Mine by turn turn_of_interest
	"""
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
				'Forest': 0,
				'Dwarven Mine': 0,
				'Adamant spell': 0,
				'Spell': 0
			}
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1

			if handsize == 7:
				#Do we keep?
				#Assuming we play enough of each land (so it's not just a minor splash) we want a red source and a green source
				both_colors = True if (hand['Mountain'] + hand['Dwarven Mine'] >= 1 or decklist['Mountain'] < 7) and (hand['Forest'] >= 1 or decklist['Forest'] < 7) else False
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 5 and both_colors):
					keephand = True

			#When we have to bottom, note that hand['Adamant spell'] is at most 1 due to the decklist so we never bottom it
			if handsize == 6:
				#We have to bottom. Ideal would be 3 land, 3 spells
				if hand['Spell'] + hand['Adamant spell'] > 3:
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, 2, or 3 spells so we put a land on the bottom
					put_lands_on_bottom(hand, 1)
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if hand['Spell'] + hand['Adamant spell'] > 3:
					#Two spells on the bottom
					hand['Spell'] -= 2
				elif hand['Spell'] + hand['Adamant spell'] == 3:
					#One land, one spell on the bottom
					hand['Spell'] -= 1
					put_lands_on_bottom(hand,1)
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					put_lands_on_bottom(hand,2)
				#Do we keep?
				if (nr_lands(hand) >= 2 and nr_lands(hand) <= 4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if hand['Spell'] + hand['Adamant spell'] > 3:
					#Three spells on the bottom
					hand['Spell'] -= 3
				elif hand['Spell'] + hand['Adamant spell'] == 3:
					#One land, two spell on the bottom
					hand['Spell'] -= 2
					put_lands_on_bottom(hand,1)
				elif hand['Spell'] + hand['Adamant spell'] == 2:
					#Two land, one spell on the bottom
					hand['Spell'] -= 1
					put_lands_on_bottom(hand,2)
				else:
					#The hand has 0 or 1 spell so we put three land on the bottom
					put_lands_on_bottom(hand,3)
				#Do we keep?
				keephand = True
			
	for turn in range(1, turn_of_interest + 1):
		#If, e.g., turn_of_interest is 3 then this range is {1, 2, 3}
		draw_a_card = True if (turn == 1 and random.random() < 0.5) or (turn > 1) else False
		if (draw_a_card):
			card_drawn = library.pop(0)
			hand[card_drawn] += 1

	if (sim_type == "Adamant"):
		if (nr_lands(hand) >= turn_of_interest and hand['Mountain'] >= 3 and hand['Adamant spell'] > 0):
			Outcome = 'Red Adamant'
		if (nr_lands(hand) >= turn_of_interest and hand['Mountain'] < 3 and hand['Adamant spell'] > 0):
			Outcome = 'No Red Adamant'
		if (nr_lands(hand) < turn_of_interest or hand['Adamant spell'] == 0 ):
			Outcome = 'Not enough lands'
			
	if (sim_type == "Mine"):
		if (hand['Mountain'] >= 3 and hand['Dwarven Mine'] > 0):
			Outcome = 'Three Mountains'
		if (hand['Mountain'] < 3 and hand['Dwarven Mine'] > 0):
			Outcome = 'Not enough Mountains'
		if (hand['Dwarven Mine'] == 0):
			Outcome = 'No Mine'
			
	return Outcome

for sim_type in ["Adamant", "Mine"]:
	number_mine = 1 if sim_type=="Mine" else 0
	for turn_of_interest in [4, 5, 6]:
		print("-----------------")
		print("We now consider the probability to draw 3 Mountain by turn "+str(turn_of_interest))
		if (sim_type == "Adamant"): 
			print("Conditional on drawing at least an adamant spell and " + str(turn_of_interest) + " lands by turn " + str(turn_of_interest))
		if (sim_type == "Mine"):
			print("Conditional on drawing a Dwarven Mine")
		print("-----------------")
		for num_basics in range(3,17):
		
			decklist = {
				'Mountain': num_basics,
				'Forest': 17 - num_basics - number_mine,
				'Dwarven Mine': number_mine,
				'Spell': 22,
				'Adamant spell': 1
			}
			
			total_relevant_games = 0.0
			total_favorable_games = 0.0
				
			for _ in range(num_simulations):
				Outcome = run_one_sim(sim_type)
				if (Outcome == "No Red Adamant" or Outcome == "Not enough Mountains"):
					total_relevant_games += 1
				if (Outcome == "Red Adamant" or Outcome == "Three Mountains"):
					total_relevant_games += 1
					total_favorable_games += 1

			print("Probability for deck with " + str(num_basics) + " Mountains: "
				+str(round(total_favorable_games / total_relevant_games * 100.0 ,1))+"%.")

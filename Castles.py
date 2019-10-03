'''
CLARIFICATION 1: Why did I choose to focus on this conditional probability?
I found the probability I determined interesting for several reasons:
•	I condition on drawing a Castle because I don't care whether or not I drew a Mountain if I don’t have a Castle. 
	The presence of a Castle effectively reduces the number of draws that could produce a Mountain.
•	I take into account mulligans because you would never keep 1 Castle and 6 spells in practice.
	Nor would you keep 2 Castle and 5 Mountains. 
	Including these hands would skew the probabilities in a way that wouldn’t match reality.
•	I focused on turns 2 and 3 because these may often be the turn where you have to drop a Castle.
	Also, these are the key turns where curving out with an untapped land is important.
'''

'''
CLARIFICATION 2: How are London mulligans handled?
•	A 7-card hand is kept if it has 2, 3, 4, or 5 lands. It is mulliganed otherwise.
•	For a mulligan to 6, we first choose what to put on the bottom and decide keep or mull afterwards. 
	To get a good mix, we bottom a spell if we drew 4+ spells and we bottom a land if we drew 4+ lands. 
	Afterwards, we keep if we hold 2, 3, or 4 lands. Otherwise, we mulligan.
•	When bottoming lands, we might choose between Castles, basics, and other lands. 
	We always keep one Castle if possible and bottom any Castles as much as needed. 
	Next, we bottom as many other lands as needed. Finally, we bottom basics as needed. 
	This also applies to 5-card and 4-card hands.
•	For a mulligan to 5, we try to get close to 3 lands and 2 spells. 
	So we bottom two spells if we drew 4+ spells, we bottom a spell and a land if we drew 3 spells, and we bottom two lands if we drew 2 spells.
	Afterwards, we keep if we have 2, 3, or 4 lands; otherwise, we mulligan.
•	For a mulligan to 4, we try to get close to 3 lands and 1 spell. Then we always keep.
'''

'''
CLARIFICATION 3: How about 20-land aggro decks or 28-land control decks?
Although my numbers are based on a 24-land deck, they remain useful as good estimates for decks with different land counts. To give an idea:
•	20 land deck: 10 basics, 4 Castles, 6 other lands: 87.9% probability of drawing a basic for a Castle by turn 3
•	24 land deck: 10 basics, 4 Castles, 10 other lands: 85.2% probability of drawing a basic for a Castle by turn 3 (cf. the table)
•	28 land deck: 10 basics, 4 Castles, 14 other lands: 83.4% probability of drawing a basic for a Castle by turn 3
Generally speaking, compared to a 24-land deck the probabilities are generally 2-3 percentage points higher for 20-land decks and 1-2 percentage points lower for 28-land decks. 
This is not a big difference.
'''

'''
CLARIFICATION 4: How about a deck with fewer than 4 Castles?
Although my numbers are based on a 4-Castle deck, they remain useful as good estimates for decks with different numbers of Castles. To give an idea:
•	2 Castle deck: 10 basics, 2 Castles, 12 other lands: 84.4% probability of drawing a basic for a Castle by turn 3
•	3 Castle deck: 10 basics, 3 Castles, 11 other lands: 84.8% probability of drawing a basic for a Castle by turn 3 
•	4 Castle deck: 10 basics, 4 Castles, 10 other lands: 85.2% probability of drawing a basic for a Castle by turn 3 (cf. the table)
This difference is negligible.
'''

import random
from collections import Counter

def log(s):
    if DEBUG:
        print(s)

DEBUG = False

turn_of_interest = 3
num_simulations = 100000

def put_lands_on_bottom(hand, lands_remaining_to_bottom):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in decklist, with number drawn
		lands_remaining_to_bottom - The number of lands to bottom (>= number of lands in hand)
	Returns - nothing, it just adjusts the hand value
	"""
	#Keep one Castle if possible and bottom additional Castles
	castles_to_bottom = min( max(hand['Castle'] -1, 0), lands_remaining_to_bottom )
	hand['Castle'] -= castles_to_bottom
	lands_remaining_to_bottom -= castles_to_bottom
	#Bottom other lands as much as possible
	other_land_to_bottom = min(hand['Other land'],lands_remaining_to_bottom)
	hand['Other land'] -= other_land_to_bottom
	lands_remaining_to_bottom -= other_land_to_bottom
	#If we still need to bottom some lands, then bottom basics as much as needed
	hand['Basic land'] -= lands_remaining_to_bottom

def nr_lands(hand):
	return hand['Basic land'] + hand['Other land'] + hand['Castle']

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

			log("We mulligan to "+str(handsize)+" and the library is")
			log(library)
			log(Counter(library))

			#Construct a random opening hand
			hand = {
				'Castle': 0,
				'Basic land': 0,
				'Other land': 0,
				'Spell': 0
			}
			for _ in range(7):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1
			log("Hand is:")
			log(hand)

			if handsize == 7:
				#Do we keep?
				if (nr_lands(hand)>=2 and nr_lands(hand)<=5):
					keephand = True

			if handsize == 6:
				#We have to bottom. Ideal would be 3 land, 3 spells
				if hand['Spell'] > 3:
					hand['Spell'] -= 1
				else:
					#The hand has 0, 1, 2, or 3 spells so we put a land on the bottom
					put_lands_on_bottom(hand,1)
				#Do we keep?
				if (nr_lands(hand)>=2 and nr_lands(hand)<=4):
					keephand = True

			if handsize == 5:
				#We have to bottom. Ideal would be 3 land, 2 spells
				if hand['Spell'] > 3:
					#Two spells on the bottom
					hand['Spell'] -= 2
				elif hand['Spell'] == 3:
					#One land, one spell on the bottom
					hand['Spell'] -= 1
					put_lands_on_bottom(hand,1)
				else:
					#The hand has 0, 1, or 2 spells so we put two land on the bottom
					put_lands_on_bottom(hand,2)
				#Do we keep?
				if (nr_lands(hand)>=2 and nr_lands(hand)<=4):
					keephand = True

			if handsize == 4:
				#We have to bottom. Ideal would be 3 land, 1 spell
				if hand['Spell'] > 3:
					#Three spells on the bottom
					hand['Spell'] -= 3
				elif hand['Spell'] == 3:
					#One land, two spell on the bottom
					hand['Spell'] -= 2
					put_lands_on_bottom(hand,1)
				elif hand['Spell'] == 2:
					#Two land, one spell on the bottom
					hand['Spell'] -= 2
					put_lands_on_bottom(hand,2)
				else:
					#The hand has 0 or 1 spell so we put three land on the bottom
					put_lands_on_bottom(hand,3)
				#Do we keep?
				keephand = True
			
			log("Keephand is now "+str(keephand)+" and hand is now:")
			log(hand)
			
	for turn in range(1, turn_of_interest + 1):
		#If, e.g., turn_of_interest is 3 then this range is {1, 2, 3}
		log("We enter turn "+str(turn))
		draw_a_card = True if (turn == 1 and random.random()< 0.5) or (turn > 1) else False
		if (draw_a_card):
			card_drawn = library.pop(0)
			hand[card_drawn] += 1
			log("We drew "+card_drawn)

	if (hand['Castle'] >= 1 and hand['Basic land'] >= 1):
		Outcome = 'Untapped Castle'
	if (hand['Castle'] >= 1 and hand['Basic land'] == 0):
		Outcome = 'Tapped Castle'
	if (hand['Castle'] == 0):
		Outcome = 'No Castle'
	log("Outcome is: "+Outcome)
	return Outcome

for num_basics in range(2,21):

	decklist = {
		'Castle': 4,
		'Basic land': num_basics,
		'Other land': 24-4-num_basics,
		'Spell': 36
	}
	
	print("We now consider the following decklist:")
	print(Counter(decklist))

	total_relevant_games = 0.0
	total_favorable_games = 0.0
		
	for i in range(num_simulations):
		log("----------SIM "+str(i))
		Outcome = run_one_sim()
		if (Outcome == "Tapped Castle"):
			total_relevant_games += 1
		if (Outcome == "Untapped Castle"):
			total_relevant_games += 1
			total_favorable_games += 1
		log("Now at "+str(total_favorable_games)+" favorable out of "+str(total_relevant_games)+" relevant")

	print('Consider games where you drew a Castle by turn '+str(turn_of_interest))
	print("Probability of also drawing a basic by that turn is "
		+str(round(total_favorable_games / total_relevant_games * 100.0 ,1))+"%.")

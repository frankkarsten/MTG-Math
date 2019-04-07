import random
from collections import Counter
import sys
sys.stdout = open('outputfile.txt', 'w')

def log(s):
    if DEBUG:
        print(s)

DEBUG = False   

Jund = {
	'Shock land': 12,
	'Check land': 11,
	'OTHER': 17,
	'Dreadhorde Butcher': 4,
	'Dreadhorde Arcanist': 3,
	'Colossus': 4,
	'Adventurous Impulse': 3,
	'Shock': 3,
	'Thud': 3
}

def simulate_combo(hand, deck):	
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		deck - A shuffled list of 53 or more cards
	Returns - either True (1) if the opponent was dealt 20+ damage by turn 3, and False (0) otherwise
	"""
	#Note: The hand will contain a shock dual, so all lands can enter untapped
	#Note: Lands are assumed to produce all colors. This is a simplification that will overestimate the real probability.
	turn = 1
	land_in_play = 0
	Butcher_in_play = False
	Arcanist_in_play = False
	opp_life = 20
	for turn in [1,2,3]:
		#Draw a card; we're on the play with probability 50%
		log("Welcome to turn "+ str(turn))
		if (turn > 1 or random.random()>0.5):
			card_drawn = deck.pop(0)
			hand[card_drawn] += 1
			log("We drew: " + card_drawn)
			if (card_drawn == 'Shock land' or card_drawn == 'Check land'):
				hand['land'] += 1
				#Again, we won't actually use variables hand['Shock land'] + hand['Check land']
				#Only the total variable hand['land'] is relevant
		#Play a land
		if (hand['land'] > 0):
			land_in_play += 1
			hand['land'] -= 1
			log("We play a land. Hand is now:")
			log(hand)
		#We will assume sufficient mana for now, and check to see if we had 3+ lands on turn 3
		if (turn == 1):
			#Cast Shock if we have Arcanist but no Butcher, or if we have no Impulse
			condition = hand['Dreadhorde Arcanist'] > 0 and hand['Dreadhorde Butcher'] == 0
			shock_cast = False
			if (hand['Shock'] > 0 and ( condition or hand['Adventurous Impulse'] == 0) ):
				opp_life = 18
				hand['Shock'] -= 1
				shock_cast = True
				log("We cast Shock.")
			#Cast Impulse otherwise, taking Butcher if we don't already have one and a land otherwise
			if ( shock_cast == False and hand['Adventurous Impulse'] > 0):
				log("We cast Adventurous Impulse.")
				hand['Adventurous Impulse'] -= 1
				cards_seen = []
				for _ in range(3):
					cards_seen.append(deck.pop(0))
				if (hand['Dreadhorde Butcher'] == 0 and 'Dreadhorde Butcher' in cards_seen):
					hand['Dreadhorde Butcher'] += 1
					log("We add Dreadhorde Butcher to our hand.")
				elif ('Shock land' in cards_seen or 'Check land' in cards_seen):
					hand['land'] += 1
					log("We add a land to our hand.")
		#We will assume sufficient mana for now, and check to see if we had 3+ lands on turn 3
		if (turn == 2):
			#Cast Butcher if we have it
			if (hand['Dreadhorde Butcher'] > 0):
				Butcher_in_play += 1
				opp_life -= 1
				log("We cast Dreadhorde Butcher.")
			#Otherwise, cast Arcanist if we have it
			elif (hand['Dreadhorde Arcanist'] > 0):
				Arcanist_in_play += 1
				log("We cast Dreadhorde Arcanist.")
		if (turn == 3):
			if (land_in_play < 3):
				#We won't be able to combo
				opp_life = 100
				log("Not enough lands!")
			else:
				if (hand['Colossus'] > 0 and hand['Thud'] > 0):
					if (Butcher_in_play):
						opp_life -= 20
					if (Arcanist_in_play):
						opp_life -= 18
	log("Opponent's life at the end: "+str(opp_life))
	if (opp_life <=0):
		return True
	else:
		return False

def simulate_hand(decklist):
	num_simulations = 1000000
	num_successes = 0
	sim_hand = {}
	sim_deck = []
	for _ in range(num_simulations):
		previous_hand_kept = False
		#We iterate over all hand sizes
		#But we only run a simulation with one keepable hand, then set previous_hand_kept to True
		for mulligan_to in [7, 6, 5, 4, 3, 2]:
			#Generates deck as a list variable
			deck=[]
			for card in decklist.keys():
				deck += [card] * decklist[card]
			#The random.sample takes a random sample of mulligan_to cards from deck without replacement
			#Feeding that sample into Counter gives a dictionary with the number drawn for each cardtype
			hand = Counter(random.sample(deck, mulligan_to))
			shock_lands = hand['Shock land']
			creature_pieces = hand['Dreadhorde Butcher'] + hand['Dreadhorde Arcanist'] + hand['Adventurous Impulse']
			instant_pieces = hand['Colossus'] + hand['Thud']
			#If hand doesn’t contain at least a shock dual, a combo creature, and a combo spell, mulligan
			#The shock dual restriction ensures that subsequent check lands will enter untapped
			if (shock_lands > 0 and creature_pieces > 0 and instant_pieces > 0 and not previous_hand_kept):
				#All lands will be treated as five-color hands for simplicity
				hand['land'] = hand['Shock land'] + hand['Check land']
				#We won't use the variables hand['Shock land'] + hand['Check land'] from now on
				#Only the total variable hand['land'] is relevant from now on
				log("=====")
				log("We're going to start a new simulation with this hand and deck:")
				log(hand)
				#Build the non-hand part of the deck as a list variable, then shuffle it
				sim_deck = []
				for card in decklist.keys():
					sim_deck += [card] * ( decklist[card] - hand[card] )
					random.shuffle(sim_deck)
				log(sim_deck)
				num_successes += simulate_combo(hand, sim_deck)
				previous_hand_kept = True
	return (num_successes / num_simulations)

print(f'Probability of assembling a turn-3 kill: {simulate_hand(Jund) * 100:.2f}%.')

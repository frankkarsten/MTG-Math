import random
from collections import Counter
from itertools import combinations
import math

list_of_opening_hands = []
for Guide in range(8):
	for Bolt in range(8):
		for Charm in range(8):
			for Land in range(8):
				if Guide + Bolt + Charm + Land == 7:
					hand = {
						'Goblin Guide': Guide,
						'Lightning Bolt': Bolt,
						'Boros Charm': Charm,
						'Sacred Foundry': Land
					}
					list_of_opening_hands.append(hand)
						
def binom(n, k):
	"""	
	Parameters:
		n - Number of elements of the entire set
		k - Number of elements in the subset
	It should hold that 0 <= k <= n
	Returns - The binomial coefficient n choose k that represents the number of ways of picking k unordered outcomes from n possibilities
	"""
	answer = 1
	for i in range(1, min(k, n - k) + 1):
		answer = answer * (n + 1 - i) / i
	return int(answer)

def multivariate_hypgeom(deck, needed):
	"""	
	Parameters:
		deck - A dictionary of cardname : number of copies
		needed - A dictionary of cardname : number of copies
	It should hold that the cardname keys of deck and needed are identical
	Returns - the multivariate hypergeometric probability of drawing exactly the cards in 'needed' from 'deck' when drawing without replacement 
	"""
	answer = 1
	sum_deck = 0
	sum_needed = 0
	for card in deck.keys():
		answer *= binom(deck[card], needed[card])
		sum_deck += deck[card]
		sum_needed += needed[card]
	return answer / binom(sum_deck, sum_needed)
	
def simulate_one_game(hand, library, drawfirst):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		library - A list of 53 or more cards, most of which will be shuffled 
			(but after mull one or more cards on the bottom may be known)
		drawfirst - A boolean that is True if on the draw and False on the play
	Returns - A number that represents the kill-turn where 20 damage was dealt
	"""
	
	#Initialize variables
	turn = 1
	opp_life = 20
	opp_Push = 1
	opp_Dispel = 1
	battlefield = {}
	for card in decklist.keys():
		battlefield[card] = 0

	#Loop over turns
	while True:
		
		#Draw a card if on the draw or if turn 2 or later
		if drawfirst or turn >= 2:
			card_drawn = library.pop(0)
			hand[card_drawn] += 1

		#Play a land and tap all lands for mana
		if (hand['Sacred Foundry'] > 0):
			hand['Sacred Foundry'] -= 1
			battlefield['Sacred Foundry'] += 1
		mana_available = battlefield['Sacred Foundry']

		#Play Goblin Guide if possible, and attack
		playable_goblins = min(mana_available, hand['Goblin Guide'])
		hand['Goblin Guide'] -= playable_goblins
		mana_available -= playable_goblins
		battlefield['Goblin Guide'] += playable_goblins
		if opp_Push > 0 and battlefield['Goblin Guide'] > 0:
			opp_Push -= 1
			battlefield['Goblin Guide'] -= 1
		opp_life -= battlefield['Goblin Guide'] * 2

		#Cast as many 1-mana Bolts as possible, unless that would leaves us with 1 mana remaining and Charm in hand
		#Example: If we have 3 lands, 2 Bolts, and 1 Charm, we want to cast one Bolt and one Charm
		if mana_available >= 1 and hand['Lightning Bolt'] >= mana_available:
			hand['Lightning Bolt'] -= mana_available
			opp_life -= 3 * mana_available
			mana_available = 0
			if opp_Dispel > 0:
				opp_Dispel -= 1
				opp_life += 3
										
		if mana_available >= 2 and hand['Lightning Bolt'] in [mana_available - 1, mana_available - 2] and hand['Boros Charm'] >= 1:
			hand['Lightning Bolt'] -= mana_available - 2
			opp_life -= 3 * (mana_available - 2)
			hand['Boros Charm'] -= 1
			opp_life -= 4
			if opp_Dispel > 0:
				opp_Dispel -= 1
				opp_life += 4
			mana_available = 0
			
		#Spend excess mana on Charms
		playable_charms = min(mana_available // 2, hand['Boros Charm'])
		hand['Boros Charm'] -= playable_charms
		mana_available -= playable_charms * 2
		opp_life -= playable_charms * 4 
		if opp_Dispel > 0 and playable_charms > 0:
			opp_Dispel -= 1
			opp_life += 4
		
		#Spend excess mana on Bolts
		playable_bolts = min(mana_available, hand['Lightning Bolt'])
		hand['Lightning Bolt'] -= playable_bolts
		mana_available -= playable_bolts
		opp_life -= playable_bolts * 3
		if opp_Dispel > 0 and playable_bolts > 0:
			opp_Dispel -= 1
			opp_life += 3
		
		if (opp_life <= 0):
			break
		else:
			turn += 1
				
	return turn

def simulate_one_specific_hand(hand, bottom, drawfirst, num_iterations):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		bottom - A dictionary, with the same cardnames as in deck, with cards that will be put on the bottom
			(This is due to London mull. Bottom order is currently arbitrary and assumed to be irrelevant.)
		drawfirst - A boolean that is True if on the draw and False on the play
		num_iterations - Simulation sample size. Could be 10 if precision isn't important, could be 100,000 if it's important.
	Returns - A list representing [expected kill-turn where 20 damage was dealt, P(turn 3 kill), P(turn 4 kill), P(turn 5 kill), P(turn 6+ kill)]
	"""
	kill_turn_sum = 0.0
	
	for i in range(num_iterations):
		
		#Copy opening hand information into a variable that can be manipulated in the simulation
		sim_hand = {}
		for card in decklist.keys():
			sim_hand[card] = hand[card]
		
		#Construct the library: first the random part, which gets shuffled
		sim_library = []
		for card in decklist.keys():
			sim_library += [card] * ( decklist[card] - sim_hand[card] - bottom[card])
		random.shuffle(sim_library)
		
		#Then put the bottom part on the bottom
		#The order is assumed not to matter here
		for card in bottom.keys():
			sim_library += [card] * bottom[card]
			
		#Simulate the actual game	
		kill_turn = simulate_one_game(sim_hand, sim_library, drawfirst)
		kill_turn_sum += kill_turn
		
	return kill_turn_sum/num_iterations


def what_to_put_on_bottom (hand, drawfirst, number_bottom, num_iterations):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		drawfirst - A boolean that is True if on the draw and False on the play
		number_bottom - The number of cards that needs to be put on the bottom
		num_iterations - Simulation sample size. Could be 10 if precision isn't important, could be 10,000 if it's important.
	Returns - A dictionary, with the same cardnames as in deck, with the best set of cards to put on the bottom
	Note - the optimization criterion is minimized. That's appropriate if it's a kill-turn.
	"""	
	best_goal = 50
	best_bottom = {}
	
	#Transform hand into a list to be able to iterate handily
	hand_list = []
	for card in hand.keys():
		hand_list += [card] * hand[card]
	
	#Iterate over all tuples of length number_bottom containing elements from hand_list 
	#There may be duplicates right now, that's bad for runtime but shouldn't affect the maximum
	for bottom in combinations(hand_list, number_bottom):
		bottom_dict = {}
		for card in decklist.keys():
			bottom_dict[card] = 0
		for card in bottom:
			bottom_dict[card] += 1
		
		remaining_hand = {}
		for card in decklist.keys():
			remaining_hand[card] = hand[card] - bottom_dict[card]
		
		goal = simulate_one_specific_hand(remaining_hand, bottom_dict, drawfirst, num_iterations)
		
		if (goal <= best_goal):
			best_goal = goal
			for card in decklist.keys():
				best_bottom[card] = bottom_dict[card]
	
	return best_bottom
	
def simulate_one_handsize(handsize, drawfirst):
	"""	
	Parameters:
		handsize - Opening hand size, could be in {0, 1, ..., 6, 7}
		drawfirst - A boolean that is True if on the draw and False on the play
	Returns - the probability of achieving the goal with this opening hand size and play/draw setting
	Note - for handsize > 1 the value of success_probability(handsize - 1) needs to be known!!!
	"""
	sum_kill_turn = 0.0
	
	#Construct library as a list
	library = []
	for card in decklist.keys():
		library += [card] * decklist[card]
	
	for hand in list_of_opening_hands:
		
		#Determine probability of drawing this hand
		opening_hand = hand.copy()
		prob = multivariate_hypgeom(decklist, opening_hand)
		
		#The following numbers can be adjusted manually to increase/decrease total runtime
		sample_size_per_bottom = math.ceil(20000 * handsize * prob)
		sample_size_per_hand_under_best_bottom = math.ceil(100000 * handsize * prob)
		
		#Determine the set of cards that are best to put on the bottom
		if (handsize < 7):
			best_bottom = what_to_put_on_bottom(opening_hand, drawfirst, 7 - handsize, sample_size_per_bottom)
		else:
			best_bottom = {} 
			for card in decklist.keys():
				best_bottom[card] = 0
		
		#Take the bottom part from the hand part
		for card in opening_hand.keys():
			opening_hand[card] = opening_hand[card] - best_bottom[card]
		
		#For a one-card opening hand we auto-keep
		if (handsize <= 1):
			kill_turn_outcomes = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, sample_size_per_hand_under_best_bottom)
			exp_kill_turn = kill_turn_outcomes
			
		#For a larger opening hand we choose keep or mull based on success probability
		if (handsize > 1):
			kill_turn_when_keep = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, sample_size_per_hand_under_best_bottom)
			kill_turn_when_mull = kill_turn_list[handsize - 1]
			exp_kill_turn = min(kill_turn_when_keep, kill_turn_when_mull)

		sum_kill_turn += exp_kill_turn * prob
		
	return sum_kill_turn

optimal_lands = 20
optimal_killturn = 10

for Lands in range(20, 26 + 1):

	decklist = {
		'Goblin Guide': 12,
		'Lightning Bolt': 16,
		'Boros Charm': 32 - Lands,
		'Sacred Foundry': Lands
	}

	final_kill_turn_for_7 = 0
	Results = "For "+ str(Lands) +" lands: "
	for drawfirst in [True, False]:
		kill_turn_list = [None] * 10
		for handsize in range(1, 8):
			kill_turn_list[handsize] = simulate_one_handsize(handsize, drawfirst)
			if (handsize == 7):
				final_kill_turn_for_7 += kill_turn_list[handsize] / 2.0
				Results += f'{kill_turn_list[handsize]:.4f} on the draw, ' if drawfirst else f'{kill_turn_list[handsize]:.4f} on the play, '
	Results += f'{final_kill_turn_for_7 :.4f} overall.'
	print(Results)
	if (final_kill_turn_for_7 < optimal_killturn):
		optimal_lands = Lands

def hand_to_text(hand):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
	Returns - The hand in nice text form
	"""	
	text = ""
	for card in hand.keys():
		if hand[card] > 0:
			text += str(hand[card]) + " " + card + " " 
	return text
	
decklist = {
	'Goblin Guide': 8,
	'Lightning Bolt': 16,
	'Boros Charm': 32 - optimal_lands,
	'Sacred Foundry': Lands
}

with open("burn_output.csv","w") as file:
	file.write("Hand, drawfirst, probability, keep or mull at 7, exp kill turn at 7, keep or mull at 6, best bottom at 6, keep or mull at 5, best bottom at 5")
	file.write("\n")

	for drawfirst in [True, False]:
		for hand in list_of_opening_hands:
			#Determine probability of drawing this hand
			opening_hand = hand.copy()
			prob = multivariate_hypgeom(decklist, opening_hand)
			file.write(hand_to_text(hand) + "," + str(drawfirst) + "," + str(prob)+ ",")
				
			for handsize in [7, 6, 5]:
				#Determine the set of cards that are best to put on the bottom
				if (handsize < 7):
					best_bottom = what_to_put_on_bottom(opening_hand, drawfirst, 7 - handsize, 10000)
				else:
					best_bottom = {} 
					for card in decklist.keys():
						best_bottom[card] = 0
				
				#Take the bottom part from the hand part
				for card in opening_hand.keys():
					opening_hand[card] = opening_hand[card] - best_bottom[card]
				
				#Choose keep or mull based on success probability
				kill_turn_when_keep = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, 50000)
				kill_turn_when_mull = kill_turn_list[handsize - 1]
				if (kill_turn_when_mull < kill_turn_when_keep):
					file.write("Mull!,")
				else:
					file.write("Keep!,")
					
				if (handsize == 7):
					file.write(str(kill_turn_when_keep)+",")
				if (handsize < 7):
					file.write(hand_to_text(best_bottom)+",")
				
			file.write("\n")
file.close()

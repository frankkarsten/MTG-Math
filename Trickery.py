import random
from collections import Counter
from itertools import combinations

decklist = {
	'Trickery': 1,
	'Outburst': 4,
	'Emrakul': 4,
	'Land': 51
}

### of T3 Emrakul with 2 Emrakul, 53 land: 90.75%
### of T3 Emrakul with 3 Emrakul, 52 land: 91.46%
### of T3 Emrakul with 4 Emrakul, 51 land: 91.34%

def simulate_one_game(hand, library, drawfirst):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		library - An ordered list of 53 or more cards, most of which will be shuffled 
			(but after mull one or more cards on the bottom may be known)
		drawfirst - A boolean that is True if on the draw and False on the play
	Returns - either True (1) if the goal was achieved and False (0) otherwise
	"""
	
	#TURN 1 GAMEPLAY SEQUENCE

	#Draw a card if on the draw
	if (drawfirst):
		card_drawn = library.pop(0)
		hand[card_drawn] += 1

	#Play a land
	land_in_play = 0
	if (hand['Land'] > 0):
		hand['Land'] -= 1
		land_in_play += 1

	#TURN 2 GAMEPLAY SEQUENCE

	#Draw a card
	card_drawn = library.pop(0)
	hand[card_drawn] += 1
	
	#Play a land
	if (hand['Land'] > 0):
		hand['Land'] -= 1
		land_in_play += 1

	#TURN 3 GAMEPLAY SEQUENCE

	#Draw a card
	card_drawn = library.pop(0)
	hand[card_drawn] += 1

	#Play a land
	if (hand['Land'] > 0):
		hand['Land'] -= 1
		land_in_play += 1
	
	#If possible, cast Violent Outburst
	#Return True if we were able to combo off, and False otherwise
	if (land_in_play == 3 and hand['Outburst'] > 0):
		#Is there still Trickery in deck?
		if (hand['Trickery'] == 1):
			return False
		else:
			#Drawing or milling has the same effect for our purposes
			mill_nr = random.randint(1,3)
			for _ in range(mill_nr):
				card_drawn = library.pop(0)
				hand[card_drawn] += 1
			#Check if the library still contains at least one Emrakul
			if (hand['Emrakul'] < decklist['Emrakul']):
				return True
			else:
				return False
	return False

def simulate_one_specific_hand(hand, bottom, drawfirst, num_iterations):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		bottom - A dictionary, with the same cardnames as in deck, with cards that will be put on the bottom
			(This is due to London mull. Bottom order is currently arbitrary and assumed to be irrelevant.)
		drawfirst - A boolean that is True if on the draw and False on the play
		num_iterations - Simulation sample size. Could be 10 if precision isn't important, could be 100,000 if it's important.
	Returns - the probability of achieving the goal with this opening hand
	"""
	count_good_hands = 0.0
	
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
		if simulate_one_game(sim_hand, sim_library, drawfirst)== True:
			count_good_hands += 1
		
	return count_good_hands/num_iterations


def what_to_put_on_bottom (hand, drawfirst, number_bottom, num_iterations):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		drawfirst - A boolean that is True if on the draw and False on the play
		number_bottom - The number of cards that needs to be put on the bottom
		num_iterations - Simulation sample size. Could be 10 if precision isn't important, could be 10,000 if it's important.
	Returns - A dictionary, with the same cardnames as in deck, with the best set of cards to put on the bottom
	Note - the optimization criterion is maximized, not minimized. That's appropriate if it's a success probability.
	"""	
	best_goal = 0
	best_bottom = {}
	
	#Transform hand into a list to be able to iterate handily
	hand_list = []
	for card in hand.keys():
		hand_list += [card] * hand[card]
	
	#Iterate over all tuples of length number_bottom containing elements from hand_list 
	#There may be duplicates right now, that's bad for runtime but shouldn't affect the maximum
	for bottom in combinations(hand_list, number_bottom):
		#Transform back to dictionary for convenience
		bottom_dict = {}
		for card in decklist.keys():
			bottom_dict[card] = 0
		for card in bottom:
			bottom_dict[card] += 1
		
		remaining_hand = {}
		for card in decklist.keys():
			remaining_hand[card] = hand[card] - bottom_dict[card]
		
		goal = simulate_one_specific_hand(remaining_hand, bottom_dict, drawfirst, num_iterations)
		
		if (goal >= best_goal):
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
	#The following numbers can be adjusted manually to increase/decrease total runtime
	sample_size_for_num_hands = 4000 * handsize if handsize < 7 else 100000
	sample_size_per_bottom = 4 * handsize
	sample_size_per_hand_under_best_bottom = 8 * handsize
	
	count_probability = 0.0

	#Construct library as a list
	library = []
	for card in decklist.keys():
		library += [card] * decklist[card]
	
	for iterator in range(sample_size_for_num_hands):
		
		if( iterator > 100 and iterator % 1000 == 0):
			print(f'We are now on hand number {iterator}. Current prob = {count_probability / iterator * 100 :.2f} %.')
		
		#Construct a random opening hand
		#Here, random.sample takes a random sample of 7 cards from library without replacement
		#Feeding that sample into "Counter" gives a dictionary with the number drawn for each cardtype
		opening_hand = Counter(random.sample(library, 7))
	
		#Determine the set of cards that are best to put on the bottom
		if (handsize < 7):
			best_bottom = what_to_put_on_bottom(opening_hand, drawfirst, 7 - handsize, sample_size_per_bottom)
		else:
			best_bottom = {} 
			for card in decklist.keys():
				best_bottom[card] = 0
		
		#Remove the cards to bottom from the opening hand
		for card in opening_hand.keys():
			opening_hand[card] = opening_hand[card] - best_bottom[card]
		
		#For a one-card opening hand we auto-keep
		if (handsize <= 1):
			succes_prob = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, sample_size_per_hand_under_best_bottom)
			
		#For a larger opening hand we choose keep or mull based on success probability
		if (handsize > 1):
			succes_prob_when_keep = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, sample_size_per_hand_under_best_bottom)
			succes_prob_when_mull = success_probability[handsize - 1]
			succes_prob = max(succes_prob_when_keep, succes_prob_when_mull)
		count_probability += succes_prob
		
	return count_probability / sample_size_for_num_hands

final_prob_for_7 = 0
for drawfirst in [True, False]:
	#Ugly initialization of the success_probability list
	success_probability = [None] * 10

	for handsize in range(1, 8):
		print(f'We will now simulate handsize {handsize} when drawfirst is {drawfirst}.')
		success_probability[handsize] = simulate_one_handsize(handsize,drawfirst)
		print(f'The success probability for handsize {handsize} when drawfirst is {drawfirst}: { success_probability[handsize] * 100 :.2f} %.') 
		if (handsize == 7):
			final_prob_for_7 += success_probability[handsize]
print(f'So when you sit down and have yet to roll the die, the number is {final_prob_for_7 * 50:.2f} %.')

import random
from collections import Counter
from itertools import combinations
from datetime import datetime


### of T3 Emrakul with 2 Emrakul, 53 land: Updated with new, faster sims: 90.819%.
### of T3 Emrakul with 3 Emrakul, 52 land: Updated with new, faster sims: 91.509%.
### of T3 Emrakul with 4 Emrakul, 51 land: Updated with new, faster sims: 91.512%.
### of T3 Emrakul with 5 Emrakul, 51 land: Updated with new, faster sims: 91.400%.

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
		if (hand['Trickery'] == decklist['Trickery']):
			return False
		else:
			#Find Trickery in library list
			above_Trickery = library[:library.index('Trickery')].copy()
			random.shuffle(above_Trickery)
			below_Trickery = library[library.index('Trickery') +1:].copy()
			library = below_Trickery + above_Trickery
			#Mill 3; drawing or milling has the same effect for our purposes
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
	#Use set to avoid duplicates
	for bottom in set(combinations(hand_list, number_bottom)):
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
	#Initialize
	count_probability = 0.0

	#The following number can be adjusted manually to increase/decrease total runtime
	multiplier = 20000

	#Construct library as a list, as well as the max-7 library from which to take possible opening hands
	library = []
	max_7_library = []
	for card in decklist.keys():
		library += [card] * decklist[card]
		max_7_library += [card] * min(decklist[card], 7)
	
	#Iterate over all possible opening hands
	for opening_hand_list in set(combinations(max_7_library, 7)):
		
		#Feeding the list into "Counter" gives a dictionary with the number drawn for each cardtype
		opening_hand = Counter(opening_hand_list)
		probability = multivariate_hypgeom(decklist, Counter(opening_hand))
		
		#Determine sample sizes
		sample_size_per_bottom = int(max(10, handsize * probability * multiplier))
		sample_size_per_hand_under_best_bottom = int(max(20, handsize * probability * multiplier * 4))
		if handsize == 7:
			sample_size_per_bottom *= 5
			sample_size_per_hand_under_best_bottom *= 5
		
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
		#print(f"Succes_prob {succes_prob} with hand: ", end='')
		#print(opening_hand)
		count_probability += succes_prob * probability
		
	return count_probability

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 0, length = 100, fill = '█', printEnd = "\r", newline_on_complete=False):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete if specified
    if iteration == total and newline_on_complete: 
        print()

for Emrakul in [2, 3, 4, 5]:
	decklist = {
		'Trickery': 1,
		'Outburst': 4,
		'Emrakul': Emrakul,
		'Land': 55 - Emrakul
	}
	print(decklist)
	printProgressBar(0, 70, prefix = 'Progress:', suffix = 'Complete', length = 50)
	start_time = datetime.now()

	final_prob_for_7 = 0
	i = 0
	for drawfirst in [True, False]:
		#Ugly initialization of the success_probability list
		success_probability = [None] * 10

		for handsize in range(1, 8):
			#print(f'We will now simulate handsize {handsize} when drawfirst is {drawfirst}.')
			success_probability[handsize] = simulate_one_handsize(handsize,drawfirst)
			#print(f'The success probability for handsize {handsize} when drawfirst is {drawfirst}: { success_probability[handsize] * 100 :.2f} %.') 
			if (handsize == 7):
				final_prob_for_7 += success_probability[handsize]
				i += handsize
			i += handsize
			end_time = datetime.now()
			printProgressBar(i, 70, prefix = 'Progress:', suffix = 'Complete', length = 50)
	print("Sims completed in", (end_time - start_time).seconds, end=' seconds')
	print(f'\nSuccess probability (avg of play and draw): {final_prob_for_7 * 50:.3f} %.\n')

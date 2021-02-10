import random
from collections import Counter
from itertools import combinations
from datetime import datetime

#SUCCESS_DEFINITION can be:
# 'T2' (only turn 2 big spell is ok)
# 'T4' (turn 3 or 4 2 big spell is also ok)
# 'Balanced' (turn 2 is 100% success, turn 3 is 85% success, turn 4 is 60% success)
SUCCESS_DEFINITION = 'Balanced'

def give_missing(hand, land_in_play):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		land_in_play - An integer
	Returns - a list of combo pieces that we still need to draw
	"""
	missing = []
	if hand['Trickery'] == 0:
		missing.append('Trickery')
	if hand['Stonecoil'] + hand['Crypt'] == 0:
		missing.append('Stonecoil')
		missing.append('Crypt')
	if hand['Temple'] + hand['Land'] + land_in_play < 2:
		missing.append('Temple')
		missing.append('Land')
	return missing

def simulate_one_game(hand, library, drawfirst):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		library - An ordered list of 53 or more cards, most of which will be shuffled 
			(but after mull one or more cards on the bottom may be known)
		drawfirst - A boolean that is True if on the draw and False on the play
	Returns - either True (1) if the goal was achieved and False (0) otherwise
	"""
	
	if SUCCESS_DEFINITION == 'T2':
		success = {
			2: 1,
			3: 0,
			4: 0
		}

	if SUCCESS_DEFINITION == 'T4':
		success = {
			2: 1,
			3: 1,
			4: 1
		}

	if SUCCESS_DEFINITION == 'Balanced':
		success = {
			2: 1.00,
			3: 0.85,
			4: 0.60
		}
	
	#TURN 1 GAMEPLAY SEQUENCE
	
	#Draw a card if on the draw
	if (drawfirst):
		card_drawn = library.pop(0)
		hand[card_drawn] += 1

	#Play a land
	land_in_play = 0
	if (hand['Temple'] > 0):
		hand['Temple'] -= 1
		land_in_play += 1
		#Is the top card a missing piece? If so, scry to bottom.
		missing = give_missing(hand, land_in_play)
		if library[0] not in missing:
			bottomed = library.pop(0)
	elif (hand['Land'] > 0):
		hand['Land'] -= 1
		land_in_play += 1

	for turn in [2, 3, 4]:
	
		#Draw a card
		card_drawn = library.pop(0)
		hand[card_drawn] += 1
		
		if hand['Trickery'] > 0 and hand['Land'] + land_in_play >= 2 and hand['Crypt'] + hand['Stonecoil'] > 0:
			#We will be able to cast Trickery!
			
			#Start by playing an untapped land if needed
			land_played = False
			if hand['Land'] > 0 and land_in_play == 1:
				hand['Land'] -= 1
				land_in_play += 1
				land_played = True
				
			#Figure out which zero to cast.
			if hand['Crypt'] > 0 and hand['Stonecoil'] > 0:
				#If we have a choice, pick the one with the fewest bad hits remaining in library
				if Counter(library)['Stonecoil'] > Counter(library)['Crypt']:
					#Deck has more Stonecoils, so cast Stonecoil
					zero_to_cast = 'Stonecoil'
				else:
					#Deck has more Crypts or equal, so cast Crypt
					zero_to_cast = 'Crypt'
			elif hand['Crypt'] > 0 and hand['Stonecoil'] == 0:
				zero_to_cast = 'Crypt'
			elif hand['Crypt'] == 0 and hand['Stonecoil'] > 0:
				zero_to_cast = 'Stonecoil'
			else:
				zero_to_cast = 'None'
			
			#Cast Trickery. Mill 3.
			hand['Trickery'] -= 1
			hand[zero_to_cast] -= 1
			mill_nr = random.randint(1,3)
			for _ in range(mill_nr):
				milled = library.pop(0)
			
			#Look at cards until we hit another nonland card
			bad_zero_hit = 'Stonecoil' if zero_to_cast == 'Crypt' else 'Crypt'
			bad_hit = False
			while bad_hit == False:
				card_seen = library.pop(0)
				if card_seen == 'Emrakul':
					#Return a certain amount of success based on the current turn
					return success[turn]
				if card_seen in [bad_zero_hit, 'Trickery']:
					#Stop the loop after whiffing
					bad_hit = True
					#End by playing a Temple if possible
					if land_played == False and hand['Temple'] > 0:
						hand['Temple'] -= 1
						land_in_play += 1
						#Is the top card a missing piece? If so, scry to bottom.
						missing = give_missing(hand, land_in_play)
						if library[0] not in missing:
							bottomed = library.pop(0)
		
		else:
			#We couldn't cast Trickery
			if (hand['Temple'] > 0):
				hand['Temple'] -= 1
				land_in_play += 1
				#Is the top card a missing piece? If so, scry to bottom.
				missing = give_missing(hand, land_in_play)
				if library[0] not in missing:
					bottomed = library.pop(0)
			elif (hand['Land'] > 0):
				hand['Land'] -= 1
				land_in_play += 1
		
	#After looping over turns 2, 3, and 4, we still haven't returned a success
	#So we whiffed
	return 0

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
		count_good_hands += simulate_one_game(sim_hand, sim_library, drawfirst)
		
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

for Temple in [8, 9, 10, 11, 12, 13, 14]:
	for Emrakul in [20, 21, 22, 23, 24]:
		decklist = {
			'Trickery': 4,
			'Stonecoil': 4,
			'Crypt': 4,
			'Emrakul': Emrakul,
			'Temple': Temple,
			'Land': 60 - 4 - 4 - 4 - Emrakul - Temple
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
		print(f'\nSo when you sit down and have yet to roll the die, the number is {final_prob_for_7 * 50:.3f} %.\n')

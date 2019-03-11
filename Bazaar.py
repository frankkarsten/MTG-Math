from functools import lru_cache
from math import factorial as fac
import random
#import sys
#sys.stdout = open('outputfile.txt', 'w')

def log(s):
    if DEBUG:
        print(s)

DEBUG = False   
mulligan_to = 7
#This number specifies the lowest possible hand size you're willing to mulligan to in search of your key 4-of
#If you're willing to mulligan into oblivion, then mulligan_to should be 1.
max_mulls = 7 - mulligan_to    

#I start with code almost entirely written by theelk801; I only made minor adjustments
#His code is available here: https://github.com/theelk801/bazaar_of_baghdad

@lru_cache(maxsize=None)
def bino(a, b):
    """
    computes the binomial coefficient (a choose b)
    """
    if b > a:
        return 0
    return fac(a) // (fac(a - b) * fac(b))


@lru_cache(maxsize=None)
def hypogeo(N1, n1, N2, n2, N3, n3):
    """
    computes hypergeometric probability in three variables
    """
    numerator = bino(N1, n1) * bino(N2, n2) * bino(N3, n3)
    denominator = bino(N1 + N2 + N3, n1 + n2 + n3)
    return numerator / denominator


def hand_gen(bazaars, powders, other, hand_size=7):
    """
    generates all possible opening hands given makeup of the deck
    """
    for i in range(bazaars + 1):
        for j in range(powders + 1):
            for k in range(other + 1):
                if i + j + k == hand_size:
                    yield i, j, k


def powder_gen(powders_in_hand, other_in_hand, to_put_under):
    """
    generates all possible ways to put cards from hand onto bottom of library while mulling, leaving at least one powder
    assumes that there are no bazaar in hand as the hand would be kept
    """
    for i in range(powders_in_hand):
        for j in range(other_in_hand + 1):
            if i + j == to_put_under:
                yield i, j


@lru_cache(maxsize=None)
def prob_of_keep(bazaars_in_hand,
                 bazaars_in_deck,
                 powders_in_hand,
                 powders_in_deck,
                 other_in_hand,
                 other_in_deck,
                 powders_on_bottom=0,
                 other_on_bottom=0,
                 mull_count=0,
                 have_to_put_cards_on_bottom=True):
    """
    computes the probability that a given hand will result in a keep or will mulligan into a hand that will keep
    """

    # start with easy pass/fails
    if bazaars_in_hand > 0 and mull_count<7:
        return 1.0

    # start with regular mulligan odds, if we can mulligan lower (otherwise it's zero)
    regular_mull = 0
    if (mull_count < max_mulls):
    	for i, j, k in hand_gen(bazaars_in_deck,
    							powders_in_deck + powders_on_bottom,
    							other_in_deck + other_on_bottom):
    		# NOTE: For Vancouver mull rule, handsize should be 7 - (mull_count + 1)
    		# find probability of hand being drawn
    		prob = hypogeo(bazaars_in_deck, i, powders_in_deck + powders_on_bottom,
    					   j, other_in_deck + other_on_bottom, k)
    		# multiply by probability of hand leading to a keep
    		prob *= prob_of_keep(
    			i,
    			bazaars_in_deck,
    			j,
    			powders_in_deck + powders_on_bottom,
    			k,
    			other_in_deck + other_on_bottom,
    			mull_count = mull_count + 1, 
    			have_to_put_cards_on_bottom=True)
    		regular_mull += prob

    # if serum powder not in hand, or probability is already 1, we can stop
    if powders_in_hand == 0 or regular_mull == 1.0:
        return regular_mull

    # create list of all possible outcomes
    all_mulls = [regular_mull]

    # potentially put cards on the bottom
    powders_to_bottom = min(mull_count, powders_in_hand - 1) if have_to_put_cards_on_bottom else 0
    other_to_bottom = mull_count - powders_to_bottom if have_to_put_cards_on_bottom else 0
    powders_left = powders_in_deck - powders_in_hand
    other_left = other_in_deck - other_in_hand
    powder_mull = 0
    for i, j, k in hand_gen(bazaars_in_deck, powders_left, other_left,
    						7 - mull_count):
    	prob = hypogeo(bazaars_in_deck, i, powders_left, j, other_left, k)
    	prob *= prob_of_keep(i, bazaars_in_deck, j, powders_left, k,
    						 other_left,
    						 powders_on_bottom + powders_to_bottom,
    						 other_on_bottom + other_to_bottom, mull_count, have_to_put_cards_on_bottom=False)
    	powder_mull += prob
    if powder_mull == 1.0:
    	return 1.0
    all_mulls.append(powder_mull)
    return max(all_mulls)

def prob_of_good_hand(bazaars=4, powders=4, other=52):
    """
    computes the overall probability of a keep for all possible hands
    """
    total = 0
    for i, j, k in hand_gen(bazaars, powders, other):
        prob = hypogeo(bazaars, i, powders, j, other, k)
        prob *= prob_of_keep(i, bazaars, j, powders, k, other)
        total += prob
    return total

print("Probability of holding Bazaar when willing to mull down to "+ str(mulligan_to)+": "+str(prob_of_good_hand()))
print("That was the exact probabily. Now starting a simulation to check.")

#The above is almost entirely copied from theelk801 (https://github.com/theelk801/bazaar_of_baghdad)
#I only made minor adjustments and fixes
#Below is a simulation written by me, Frank Karsten, under the simplifying assumption that you always use Powder if you don’t hold Bazaar
#I may use it later to consider Eternal Scourge and Gemstone Caverns as well

num_iterations = 10 ** 7
count_bazaar = 0
scourge_exiled = 0
cards_in_hand_when_keep = 0
on_draw = False

for iteration in range(num_iterations):
	log("==========================")
	if(iteration % 100000 == 0 and iteration>0):
		print ("Iteration number "+str(iteration)+". Current prob: "+ str(round(100 * count_bazaar / iteration,2))+"%")
	decklist = {
		'Bazaar': 4, 
		'Powder': 4, 
		'Scourge': 0,
		'Cavern': 0,
		'Other': 52
	}
	number_mulls = 0
	mull_type = 'Regular'

	while True:
		cards_in_hand = {
			'Bazaar': 0, 
			'Powder': 0, 
			'Scourge': 0,
			'Cavern': 0,
			'Other': 0,
		}
		if (mull_type == 'Regular'):
			we_need_to_put_cards_on_bottom = True
			deck = []
			for card in decklist.keys():
				deck += [card] * decklist[card]
			random.shuffle(deck)
			number_cards_to_draw = 7
		elif (mull_type == 'Via Powder'):
			number_cards_to_draw = 7 - number_mulls
			we_need_to_put_cards_on_bottom = False
	
		log(deck)
		for _ in range(number_cards_to_draw):
			cards_in_hand[deck.pop(0)] += 1
		log("We have an opening hand with " + str(cards_in_hand['Bazaar']) + " Bazaar, " + str(cards_in_hand['Powder']) + " Powder, " + str(cards_in_hand['Other']) + " Other.")
		if (number_mulls >= 7):
			log("Stop!")
			break
		elif (cards_in_hand['Bazaar'] >= 1):
			count_bazaar += 1
			log("Bazaar!")
			cards_in_hand_when_keep += 7 - number_mulls
			if (on_draw and cards_in_hand['Caverns']>0 and cards_in_hand['Scourge']>0):
				scourge_exiled += 1
			break
		elif (cards_in_hand['Bazaar'] == 0 and cards_in_hand['Powder'] == 0 and number_mulls < max_mulls):
			number_mulls += 1
			mull_type = 'Regular'
			log("Reg mull! number_mulls: "+str(number_mulls))
		elif (cards_in_hand['Bazaar'] == 0 and cards_in_hand['Powder'] == 0 and number_mulls >= max_mulls):
			cards_in_hand_when_keep += 7 - number_mulls
			log("Stop!")
			break
		elif (cards_in_hand['Bazaar'] == 0 and cards_in_hand['Powder'] > 0):
			mull_type = 'Via Powder'
			put_on_bottom = {
				'Bazaar': 0,
				'Powder': 0, 
				'Scourge': 0,
				'Cavern': 0,
				'Other': 0
			}
			if (we_need_to_put_cards_on_bottom):
				put_on_bottom['Bazaar'] =  0 
				put_on_bottom['Powder'] = min(number_mulls, cards_in_hand['Powder'] - 1) 
				put_on_bottom['Cavern'] = min(number_mulls - put_on_bottom['Powder'], cards_in_hand['Cavern'])
				put_on_bottom['Other'] = min(number_mulls - put_on_bottom['Powder'] - put_on_bottom['Cavern'], cards_in_hand['Other'])
				put_on_bottom['Scourge'] = number_mulls - put_on_bottom['Powder'] - put_on_bottom['Cavern'] - put_on_bottom['Other']
			for card in decklist.keys():
				deck += [card] * put_on_bottom[card]
				decklist[card] -= cards_in_hand[card] - put_on_bottom[card]
			scourge_exiled += cards_in_hand['Scourge'] - put_on_bottom['Scourge']
			log("Powder mull! We put "+ str(put_on_bottom['Powder']) + " powders and "+ str(put_on_bottom['Other']) + " other on bottom and exiled " + str(cards_in_hand['Powder'] - put_on_bottom['Powder']) + "powders and "+ str(cards_in_hand['Other'] - put_on_bottom['Other']) + " others.")
		
								
print('Probability: ' + str(round(100 * count_bazaar / num_iterations,2))+"%")
print('Expected number of Eternal Scourge exiled: ' + str(round(scourge_exiled / num_iterations,3)))
print('Expected number of cards in hand when keeping: ' + str(round(cards_in_hand_when_keep / num_iterations,2)))






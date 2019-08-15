import random
from collections import Counter
from itertools import combinations

#import sys
#sys.stdout = open('outputfile.txt', 'w')

def llog(s):
    if SUPERDEBUG:
        print(s)

def log(s):
    if DEBUG:
        print(s)

SUPERDEBUG = False
DEBUG = False

decklist = {
	'Carrion Feeder': 4,
	'Gravecrawler': 4,
	'Insolent Neonate': 4,
	'Stitchers Supplier': 4,
	'Bloodghast': 4,
	'Satyr Wayfinder': 4,
	'Vengevine': 4,
	'Hogaak': 4,
	'Faithless Looting': 4,
	'Interactive': 4,
	'Bloodstained Mire': 10,
	'City of Brass': 10
}

#All non-fetch lands treated as fetcheable City of Brass. 
#This is an extreme modeling, but it keeps me sane because
#it greatly simplifies what we need to keep track of.

def choose_discard(hand, number_remaining_discard):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		number_remaining_discard - 2 for Faithless Looting and 1 for Insolent Neonate
	Returns - a list of the cards to discard, based on a fixed priority order
	"""
	answer = []
	
	#If you have a fetchland, then just discard regular lands early
	if (hand['Bloodstained Mire'] >= 1):
		priority_list = ['Bloodghast', 'Vengevine', 'City of Brass', 'Interactive', 'Gravecrawler', 
			'Insolent Neonate', 'Carrion Feeder', 'Faithless Looting', 'Satyr Wayfinder', 
			'Stitchers Supplier', 'Bloodstained Mire', 'Hogaak']
	
	#Otherwise, HODL
	else:
		priority_list = ['Bloodghast', 'Vengevine', 'Interactive', 'Gravecrawler',
			'Insolent Neonate', 'Carrion Feeder', 'Faithless Looting', 'Satyr Wayfinder',
			'Stitchers Supplier', 'Hogaak', 'City of Brass', 'Bloodstained Mire']
	
	for card in priority_list:
		number_to_discard = min(hand[card], number_remaining_discard)
		answer += [card] * number_to_discard
		number_remaining_discard = max(0, number_remaining_discard - number_to_discard)
	
	return answer

def describe_game_state(hand, battlefield, graveyard, library): 
	"""	
	This function is merely used while debugging simulate_one_game
	"""
	llog("")
	llog("Hand is now:")
	llog(hand)
	llog("Battlefield is now:")
	llog(battlefield)
	llog("Graveyard is now:")
	llog(graveyard)
	llog("Library is now:")
	llog(library)
	llog(Counter(library))
	llog("")

def play_fetchland(hand, battlefield, graveyard, library): 
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Bloodstained Mire'] -= 1
	library.remove('City of Brass')
	random.shuffle(library)
	battlefield['City of Brass'] += 1
	graveyard['Bloodstained Mire'] +=1
	llog("We fetched.")
	describe_game_state(hand, battlefield, graveyard, library)
 
def play_land(hand, battlefield, graveyard, library): 
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['City of Brass'] -= 1
	battlefield['City of Brass'] += 1
	llog("We played City of Brass.")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Supplier(hand, battlefield, graveyard, library): 
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Stitchers Supplier'] -= 1
	battlefield['Stitchers Supplier'] += 1
	#ETB trigger: Mill the top 3
	for _ in range(3):
		card_milled = library.pop(0)
		graveyard[card_milled] += 1
	llog("We play a Stitchers Supplier.")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Looting(hand, battlefield, graveyard, library): 
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Faithless Looting'] -= 1
	graveyard['Faithless Looting'] += 1
	llog("We play a Faithless Looting.")
	for _ in range(2):
		card_drawn = library.pop(0)
		hand[card_drawn] += 1
		llog("We drew: " + card_drawn +"\n")
	#Use the function choose_discard to figure out which cards to discard
	cards_to_discard = choose_discard(hand, 2)
	for card in cards_to_discard:
		hand[card] -= 1
		graveyard[card] += 1
		llog("We discard: " + card +"\n")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Neonate(hand, battlefield, graveyard, library):
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Insolent Neonate'] -= 1
	graveyard['Insolent Neonate'] += 1
	llog("We play an Insolent Neonate and sac it.")
	#We immediately sacrifice Neonate!
	if (sum(hand.values()) > 0):
		#Use the function choose_discard to figure out which card to discard
		cards_to_discard = choose_discard(hand, 1)
		for card in cards_to_discard:
			hand[card] -= 1
			graveyard[card] += 1
			llog("We discard: " + card +"\n")
		card_drawn = library.pop(0)
		hand[card_drawn] += 1
		llog("We drew: " + card_drawn +"\n")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Feeder(hand, battlefield, graveyard, library):
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Carrion Feeder'] -= 1
	battlefield['Carrion Feeder'] += 1
	llog("We play a Carrion Feeder.")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Gravecrawler_from_hand(hand, battlefield, graveyard, library):
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Gravecrawler'] -= 1
	battlefield['Gravecrawler'] += 1
	llog("We play a Gravecrawler from hand.")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Gravecrawler_from_graveyard(hand, battlefield, graveyard, library):
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	graveyard['Gravecrawler'] -= 1
	battlefield['Gravecrawler'] += 1
	llog("We play a Gravecrawler from hand.")
	describe_game_state(hand, battlefield, graveyard, library)
	
def play_Bloodghast_from_hand(hand, battlefield, graveyard, library):
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Bloodghast'] -= 1
	battlefield['Bloodghast'] += 1
	llog("We play a Bloodghast from hand.")
	describe_game_state(hand, battlefield, graveyard, library)

def play_Wayfinder(hand, battlefield, graveyard, library):
	"""	
	This function edits the parameters self-explanatorily for simulate_one_game
	"""
	hand['Satyr Wayfinder'] -= 1
	battlefield['Satyr Wayfinder'] += 1
	#ETB trigger: Mill the top 4, don't take a land
	for _ in range(4):
		card_milled = library.pop(0)
		graveyard[card_milled] += 1
	llog("We play a Satyr Wayfinder.")
	describe_game_state(hand, battlefield, graveyard, library)

def simulate_one_game(hand, library, drawfirst):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		library - A list of 53 or more cards, most of which will be shuffled 
			(but after mull one or more cards on the bottom may be known)
		drawfirst - A boolean that is True if on the draw and False on the play
	Returns - either True (1) if the goal was achieved and False (0) otherwise
	"""
	
	#Initialize variables
	Hogaak_cmc = 7
	llog("----------Start of a new game----------")
	turn = 1
	battlefield = {}
	graveyard = {}
	for card in decklist.keys():
		graveyard[card] = 0
		battlefield[card] = 0
		
	#Draw a card if on the draw
	llog("Welcome to turn "+ str(turn))
	describe_game_state(hand, battlefield, graveyard, library)
	if (drawfirst):
		card_drawn = library.pop(0)
		hand[card_drawn] += 1
		llog("We drew: " + card_drawn +"\n")
	
	#Play a land
	land_played = False 
	if (hand['Bloodstained Mire'] > 0):
		play_fetchland(hand, battlefield, graveyard, library)
		land_played = True
	if (hand['City of Brass'] > 0 and land_played == False):
		play_land(hand, battlefield, graveyard, library)
		land_played = True
	
	mana_available = battlefield['City of Brass']
	
	#TURN 1 GAMEPLAY SEQUENCE
	
	#Play Supplier if possible
	if (hand['Stitchers Supplier'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Supplier(hand, battlefield, graveyard, library)
	
	#If you already hold Satyr Wayfinder and a second land, play a black creature if possible
	#This potentially enables turn-2 Wayfinder into Hogaak
	if (hand['Satyr Wayfinder'] > 0 and hand['Bloodstained Mire'] + hand['City of Brass'] > 0):
		if (hand['Carrion Feeder'] > 0 and mana_available >= 1):
			mana_available -= 1
			play_Feeder(hand, battlefield, graveyard, library)
		if (hand['Gravecrawler'] > 0 and mana_available >= 1):
			mana_available -= 1
			play_Gravecrawler_from_hand(hand, battlefield, graveyard, library)
	
	#Play Looting or Neonate if possible
	if (hand['Faithless Looting'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Looting(hand, battlefield, graveyard, library)
	if (hand['Insolent Neonate'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Neonate(hand, battlefield, graveyard, library)
		
	#If we didn't hold Satyr Wayfinder but also didn't have a red spell
	#Then play a black creature now if possible
	if (hand['Carrion Feeder'] > 0 and mana_available >= 1):
			mana_available -= 1
			play_Feeder(hand, battlefield, graveyard, library)
	if (hand['Gravecrawler'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Gravecrawler_from_hand(hand, battlefield, graveyard, library)
		
	turn = 2
	
	#Draw a card
	llog("Welcome to turn "+ str(turn))
	describe_game_state(hand, battlefield, graveyard, library)
	card_drawn = library.pop(0)
	hand[card_drawn] += 1
	llog("We drew: " + card_drawn+"\n")

	mana_available = battlefield['City of Brass']
	land_played = False 
	
	#TURN 2 GAMEPLAY SEQUENCE BEFORE PLAYING LAND
	
	#If we can cast land, Satyr Wayfinder, Hogaak, then just do that
	#Also, if we have no Hogaak yet and no Stitcher's Supplier in hand...
	#...but Wayfinder would enable Hogaak if it's in the top 4, then just go for that
	castable_Wayfinder = hand['Bloodstained Mire'] + hand['City of Brass'] > 0 and hand['Satyr Wayfinder'] >= 1
	black_creature_for_convoke = battlefield['Carrion Feeder'] + battlefield['Stitchers Supplier'] + battlefield['Gravecrawler'] + graveyard['Bloodghast']
	delve_count_after_Wayfinder = sum(graveyard.values()) + min(hand['Bloodstained Mire'], 1) + 4
	Hogaak_hand_castable = black_creature_for_convoke >= 1 and delve_count_after_Wayfinder + 1 + black_creature_for_convoke >= Hogaak_cmc
	Hogaak_hand_enabled = hand['Hogaak'] >= 1 and Hogaak_hand_castable
	Hogaak_graveyard_castable = black_creature_for_convoke >= 1 and delve_count_after_Wayfinder - 1 + 1 + black_creature_for_convoke >= Hogaak_cmc
	Hogaak_graveyard_enabled = graveyard['Hogaak'] >= 1 and Hogaak_graveyard_castable
	Hogaak_sure = castable_Wayfinder and ( Hogaak_hand_enabled or Hogaak_graveyard_enabled)
	Hogaak_possible = castable_Wayfinder and ( Hogaak_hand_castable or Hogaak_graveyard_castable)
	Wayfinder_good_choice = Hogaak_possible and hand['Stitchers Supplier'] == 0
	if (castable_Wayfinder and (Hogaak_sure or Wayfinder_good_choice)):
		#Play a land
		if (hand['Bloodstained Mire'] > 0):
			play_fetchland(hand, battlefield, graveyard, library)
			land_played = True
		if (hand['City of Brass'] > 0 and land_played == False):
			play_land(hand, battlefield, graveyard, library)
			land_played = True
		mana_available += 1
		#Play Satyr Wayfinder
		if (hand['Satyr Wayfinder'] >0 and mana_available == 2):
			mana_available -= 2
			play_Wayfinder(hand, battlefield, graveyard, library)
	
	#If we're not casting land, Satyr Wayfinder, then opt to play one-mana cards in a fixed sequence
	
	creatures_cast_for_Vengevine = 0
	
	#Play Supplier if possible
	if (hand['Stitchers Supplier'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Supplier(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
		
	#Play Feeder if we control Supplier or already found Hogaak
	condition = battlefield['Stitchers Supplier'] > 0 or hand['Hogaak'] + graveyard['Hogaak'] > 0
	if (condition and hand['Carrion Feeder'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Feeder(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1

	#If we have already seen Vengevine, then play Neonate over Looting if possible
	#If we have not yet seen Vengevine, then play Looting over Neonate if possible
	Venge_seen = hand['Vengevine'] > 0 or graveyard['Vengevine'] > 0
	condition = Venge_seen or hand['Faithless Looting'] == 0
	if (condition and hand['Insolent Neonate'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Neonate(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
	if (hand['Faithless Looting'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Looting(hand, battlefield, graveyard, library)

	#If we didn't have Neonate/Looting to dig for Hogaak when needed
	#Then we just play Feeder now
	if (hand['Carrion Feeder'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Feeder(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
	
	#Play Gravecrawler from hand if all else fails
	if (hand['Gravecrawler'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Gravecrawler_from_hand(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine = 1

	#If we saw no Hogaak yet and have another B/G convoker, then sac Supplier to Feeder
	#We do this before playing a land due to Bloodghast
	land_in_hand = hand['Bloodstained Mire'] + hand['City of Brass'] > 0
	creature_available = hand['Stitchers Supplier'] + hand['Carrion Feeder'] + hand['Gravecrawler'] + graveyard['Gravecrawler'] + graveyard['Bloodghast'] > 0
	Vengevine_available = hand['Insolent Neonate'] > 0 and graveyard['Vengevine'] > 0
	other_convoker = land_in_hand and ( creature_available or Vengevine_available)
	if (battlefield['Stitchers Supplier'] > 0 and battlefield['Carrion Feeder'] > 0 and hand['Hogaak'] + graveyard['Hogaak'] == 0 and other_convoker):
		battlefield['Stitchers Supplier'] -= 1
		graveyard['Stitchers Supplier'] += 1
		for _ in range(3):
			card_milled = library.pop(0)
			graveyard[card_milled] += 1
	
	#TURN 2 PLAY A LAND AFTER A POSSIBLE ONE-MANA SPELL
	
	if (hand['Bloodstained Mire'] > 0 and land_played == False):
		play_fetchland(hand, battlefield, graveyard, library)
		land_played = True
		mana_available += 1
	if (hand['City of Brass'] > 0 and land_played == False):
		play_land(hand, battlefield, graveyard, library)
		land_played = True
		mana_available += 1

	#Return Bloodghasts
	battlefield['Bloodghast'] = graveyard['Bloodghast']
	graveyard['Bloodghast'] = 0
	
	#TURN 2 GAMEPLAY SEQUENCE AFTER PLAYING LAND
	
	#Opt to play one-mana cards in the same fixed sequence as before
	#Except now we may return Vengevines too
	
	#If it's possible to still play Wayfinder now, then do so
	#I don't believe this can happen, but it's kept in as a backup security
	#Just in case I missed something in the entire logic
	if (hand['Satyr Wayfinder'] > 0 and mana_available >= 2):
		mana_available -= 2
		play_Wayfinder(hand, battlefield, graveyard, library)

	#Play Supplier if possible
	if (hand['Stitchers Supplier'] > 0 and mana_available >= 1):
		mana_available -= 1
		creatures_cast_for_Vengevine += 1
		if (creatures_cast_for_Vengevine == 2):
			battlefield['Vengevine'] = graveyard['Vengevine'] 
			graveyard['Vengevine'] = 0
		play_Supplier(hand, battlefield, graveyard, library)
		
	#Play Feeder if we control Supplier or already found Hogaak
	condition = battlefield['Stitchers Supplier'] > 0 or hand['Hogaak'] + graveyard['Hogaak'] > 0
	if (condition and hand['Carrion Feeder'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Feeder(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
		if (creatures_cast_for_Vengevine == 2):
			battlefield['Vengevine'] = graveyard['Vengevine'] 
			graveyard['Vengevine'] = 0

	#Play Gravecrawler if we already found Hogaak
	if (hand['Hogaak'] + graveyard['Hogaak'] > 0):
		if (hand['Gravecrawler'] > 0 and mana_available >= 1):
			mana_available -= 1
			play_Gravecrawler_from_hand(hand, battlefield, graveyard, library)
			creatures_cast_for_Vengevine += 1
			if (creatures_cast_for_Vengevine == 2):
				battlefield['Vengevine'] = graveyard['Vengevine'] 
				graveyard['Vengevine'] = 0
		if (graveyard['Gravecrawler'] > 0 and mana_available >= 1 and battlefield['Carrion Feeder'] + battlefield['Stitchers Supplier'] > 0):
			mana_available -= 1
			play_Gravecrawler_from_graveyard(hand, battlefield, graveyard, library)
			creatures_cast_for_Vengevine += 1
			if (creatures_cast_for_Vengevine == 2):
				battlefield['Vengevine'] = graveyard['Vengevine'] 
				graveyard['Vengevine'] = 0

	#Play Neonate or Looting if possible
	#If you can return Vengevine, then choose Neonate over Looting
	#Otherwise, play Looting over Neonate
	condition = graveyard['Vengevine'] or hand['Faithless Looting'] == 0
	if (condition and hand['Insolent Neonate'] > 0 and mana_available >= 1):
		mana_available -= 1
		creatures_cast_for_Vengevine += 1
		if (creatures_cast_for_Vengevine == 2):
			battlefield['Vengevine'] = graveyard['Vengevine'] 
			graveyard['Vengevine'] = 0
		play_Neonate(hand, battlefield, graveyard, library)
	if (hand['Faithless Looting'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Looting(hand, battlefield, graveyard, library)

	#If we didn't have Neonate/Looting to dig for Hogaak when needed
	#Then we just play Feeder now
	if (hand['Carrion Feeder'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Feeder(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
		if (creatures_cast_for_Vengevine == 2):
			battlefield['Vengevine'] = graveyard['Vengevine'] 
			graveyard['Vengevine'] = 0
	
	#Play Gravecrawler from hand if all else fails
	if (hand['Gravecrawler'] > 0 and mana_available >= 1):
		mana_available -= 1
		play_Gravecrawler_from_hand(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
		if (creatures_cast_for_Vengevine == 2):
			battlefield['Vengevine'] = graveyard['Vengevine'] 
			graveyard['Vengevine'] = 0

	#Play Gravecrawler from graveyard if all else fails
	if (graveyard['Gravecrawler'] > 0 and mana_available >= 1 and battlefield['Carrion Feeder'] + battlefield['Stitchers Supplier'] > 0):
		mana_available -= 1
		play_Gravecrawler_from_graveyard(hand, battlefield, graveyard, library)
		creatures_cast_for_Vengevine += 1
		if (creatures_cast_for_Vengevine == 2):
			battlefield['Vengevine'] = graveyard['Vengevine'] 
			graveyard['Vengevine'] = 0
	
	#Cast Hogaak if possible
	BG_creature_for_convoke = battlefield['Carrion Feeder'] + battlefield['Vengevine'] + battlefield['Gravecrawler'] 
	BG_creature_for_convoke += battlefield['Stitchers Supplier'] + battlefield['Bloodghast'] + battlefield['Satyr Wayfinder']
	delve_count = sum(graveyard.values())
	Hogaak_hand_enabled = hand['Hogaak'] >= 1 and BG_creature_for_convoke >= 2 and delve_count + BG_creature_for_convoke >= Hogaak_cmc
	Hogaak_graveyard_enabled = graveyard['Hogaak'] >= 1 and BG_creature_for_convoke >= 2 and delve_count - 1 + BG_creature_for_convoke >= Hogaak_cmc
	Hogaak_cast = Hogaak_hand_enabled or Hogaak_graveyard_enabled
			
	#If we couldn't cast Hogaak yet but control Supplier and Feeder, then sac Supplier to Feeder
	#Then do this once again in case we control two Suppliers
	for _ in range(2):
		if ( (not Hogaak_cast) and battlefield['Stitchers Supplier'] > 0 and battlefield['Carrion Feeder'] > 0):
			battlefield['Stitchers Supplier'] -= 1
			graveyard['Stitchers Supplier'] += 1
			for _ in range(3):
				card_milled = library.pop(0)
				graveyard[card_milled] += 1
			#Then, again try to cast Hogaak if possible
			BG_creature_for_convoke = battlefield['Carrion Feeder'] + battlefield['Vengevine'] + battlefield['Gravecrawler'] 
			BG_creature_for_convoke += battlefield['Stitchers Supplier'] + battlefield['Bloodghast'] + battlefield['Satyr Wayfinder']
			delve_count = sum(graveyard.values())
			Hogaak_hand_enabled = hand['Hogaak'] >= 1 and BG_creature_for_convoke >= 2 and delve_count + BG_creature_for_convoke >= Hogaak_cmc
			Hogaak_graveyard_enabled = graveyard['Hogaak'] >= 1 and BG_creature_for_convoke >= 2 and delve_count - 1 + BG_creature_for_convoke >= Hogaak_cmc
			Hogaak_cast = Hogaak_hand_enabled or Hogaak_graveyard_enabled

	#Return True if we were able to cast Hogaak
	if (Hogaak_cast):
		llog("Succes!!!\n")
		return True
	else:
		llog("Failure!!!\n")
		return False	

def simulate_one_specific_hand(hand, bottom, drawfirst, num_iterations):
	"""	
	Parameters:
		hand - A dictionary, with the same cardnames as in deck, with number drawn
		bottom - A dictionary, with the same cardnames as in deck, with cards that will be put on the bottom
			(This is due to London mull. Bottom order is currently arbitrary and assumed to be irrelevant.)
		drawfirst - A boolean that is True if on the draw and False on the play
		num_iterations - Simulation sample size. Could be 10 if precision isn't important, far more otherwise.
	Returns - the probability of achieving the goal with this opening hand
	"""
	count_good_hands = 0.0
	
	for i in range(num_iterations):
		
		llog("Welcome to iteration number "+ str(i))
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
	Returns - A dictionary, with the same cardnames as in deck, with the best set of cards to put on the bottom
	"""	
	best_goal = 0
	best_bottom = {}
	llog("Welcome to the what_to_put_on_bottom function!")
	
	#Transform hand into a list to be able to iterate handily
	hand_list = []
	for card in hand.keys():
		hand_list += [card] * hand[card]
	llog("hand_list is:")
	llog(hand_list)
	llog("")
	
	#Iterate over all tuples of length number_bottom containing elements from hand_list 
	for bottom in combinations(hand_list, number_bottom):
		llog("********************************************************************")
		llog("Currently considering the following bottom:")
		llog(bottom)
		#Transform back to dictionary for convenience
		bottom_dict = {}
		for card in decklist.keys():
			bottom_dict[card] = 0
		for card in bottom:
			bottom_dict[card] += 1
		llog(bottom_dict)
		
		remaining_hand = {}
		for card in decklist.keys():
			remaining_hand[card] = hand[card] - bottom_dict[card]
		llog("Remaining hand:")
		llog(remaining_hand)
		
		goal = simulate_one_specific_hand(remaining_hand, bottom_dict, drawfirst, num_iterations)
		llog("Goal: "+str(goal))
		
		if (goal >= best_goal):
			best_goal = goal
			for card in decklist.keys():
				best_bottom[card] = bottom_dict[card]
			llog("We now set best_goal to "+str(best_goal)+" and best_bottom to:")
			llog(best_bottom)
	
	llog("THE BEST BOTTOM IS:")
	llog(best_bottom)
	
	return best_bottom
	
def simulate_one_handsize(handsize, drawfirst):
	"""	
	Parameters:
		handsize - Opening hand size, could be in {0, 1, ..., 6, 7}
		drawfirst - A boolean that is True if on the draw and False on the play
	Returns - the probability of achieving the goal with this opening hand size
	Note - for handsize > 1 the value of success_probability(handsize - 1) needs to be known
	"""
	multiplier_for_handsize_iteration = handsize 
	num_hands = 5000 * multiplier_for_handsize_iteration
	count_probability = 0.0

	#Construct library as a list
	library = []
	for card in decklist.keys():
		library += [card] * decklist[card]
	llog(library)
	

	for iterator in range(num_hands):
		
		if(iterator % 1000 == 0):
			print(f'We are now on hand number {iterator}.')
		llog("")
		llog("------------Welcome to a new iteration!------------")
		
		#Construct a random opening hand
		#Here, random.sample takes a random sample of 7 cards from library without replacement
		#Feeding that sample into "Counter" gives a dictionary with the number drawn for each cardtype
		opening_hand = Counter(random.sample(library, 7))
		log("")
		log("The opening hand is:" + str(opening_hand))
	
		#Determine the set of cards that are best to put on the bottom
		best_bottom = what_to_put_on_bottom(opening_hand, drawfirst, 7 - handsize, 5 * multiplier_for_handsize_iteration)
		log("The best bottom is:" + str(best_bottom))
		
		#Take the bottom part from the hand part
		for card in opening_hand.keys():
			opening_hand[card] = opening_hand[card] - best_bottom[card]
		
		#For a one-card opening hand we auto-keep
		if (handsize == 1):
			succes_prob = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, 50 * multiplier_for_handsize_iteration)
			
		#For a larger opening hand we choose keep or mull based on success probability
		if (handsize > 1):
			succes_prob_when_keep = simulate_one_specific_hand(opening_hand, best_bottom, drawfirst, 50 * multiplier_for_handsize_iteration)
			succes_prob_when_mull = success_probability[handsize - 1]
			succes_prob = max(succes_prob_when_keep, succes_prob_when_mull)
		count_probability += succes_prob
		
		log("Succes_prob = "+ str(succes_prob))
		
	return count_probability / num_hands

'''
hand = {
	'Carrion Feeder': 1,
	'Gravecrawler': 0,
	'Insolent Neonate': 1,
	'Stitchers Supplier': 0,
	'Bloodghast': 1,
	'Satyr Wayfinder': 0,
	'Vengevine': 0,
	'Hogaak': 1,
	'Faithless Looting': 1,
	'Interactive': 0,
	'Bloodstained Mire': 1,
	'City of Brass': 1
}

bottom = {
	'Carrion Feeder': 0,
	'Gravecrawler': 0,
	'Insolent Neonate': 0,
	'Stitchers Supplier': 0,
	'Bloodghast': 0,
	'Satyr Wayfinder': 0,
	'Vengevine': 0,
	'Hogaak': 0,
	'Faithless Looting': 0,
	'Interactive': 0,
	'Bloodstained Mire': 0,
	'City of Brass': 0
}
drawfirst = True
num_iterations = 1000

number = simulate_one_specific_hand(hand, bottom, drawfirst, num_iterations)
print( number ) 
'''


final_prob_for_7 = 0
for drawfirst in [True, False]:
	success_probability = [None] * 10
	for handsize in range(1,8):
		print(f'We will now simulate handsize {handsize} when drawfirst is {drawfirst}.')
		success_probability[handsize] = simulate_one_handsize(handsize,drawfirst)
		print(f'The success probability for handsize {handsize} when drawfirst is {drawfirst}: { success_probability[handsize] * 100 :.2f} %.') 
		if (handsize == 7):
			final_prob_for_7 += success_probability[handsize]
print(f'So when you sit down and have yet to roll the die, the number is {final_prob_for_7 * 50:.2f} %.')

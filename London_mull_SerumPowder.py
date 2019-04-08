import random

def log(s):
    if DEBUG:
        print(s)

DEBUG = False
mulligan_to = 4
max_mulls = 7 - mulligan_to    
num_iterations = 10 ** 6
on_draw = True

for mull_style in ['London', 'Vancouver']:
	print("----> We run the numbers for the " + mull_style + " mulligan.")
	count_temple = 0
	scourge_exiled = 0
	cards_in_hand_when_keep = 0
	for iteration in range(num_iterations):
		log("==========================")
		if(iteration % 100000 == 0 and iteration>0):
			print ("Iteration number "+str(iteration)+". Current prob: "+ str(round(100 * count_temple / iteration,2))+"%")
		decklist = {
			'Temple': 4, 
			'Powder': 4, 
			'Scourge': 4,
			'Cavern': 3,
			'Other': 45
		}
		number_mulls = 0
		mull_type = 'Regular'

		while True:
			cards_in_hand = {
				'Temple': 0, 
				'Powder': 0, 
				'Scourge': 0,
				'Cavern': 0,
				'Other': 0,
			}
			if (mull_type == 'Regular' and mull_style == 'London'):
				we_need_to_put_cards_on_bottom = True
				deck = []
				for card in decklist.keys():
					deck += [card] * decklist[card]
				random.shuffle(deck)
				number_cards_to_draw = 7
			elif (mull_type == 'Regular' and mull_style == 'Vancouver'):
				we_need_to_put_cards_on_bottom = False
				deck = []
				for card in decklist.keys():
					deck += [card] * decklist[card]
				random.shuffle(deck)
				number_cards_to_draw = 7 - number_mulls
			elif (mull_type == 'Via Powder'):
				number_cards_to_draw = 7 - number_mulls
				we_need_to_put_cards_on_bottom = False
		
			log(deck)
			for _ in range(number_cards_to_draw):
				cards_in_hand[deck.pop(0)] += 1
			description = str(cards_in_hand['Temple']) + " Temple, " + str(cards_in_hand['Powder']) + " Powder, " + str(cards_in_hand['Scourge']) + " Scourge, "
			description += str(cards_in_hand['Cavern']) + " Cavern, " + str(cards_in_hand['Other']) + " Other."
			log("We have an opening hand with " + description)
			if (number_mulls >= 7):
				log("Stop!")
				break
			elif (cards_in_hand['Temple'] >= 1):
				count_temple += 1
				log("Temple!")
				cards_in_hand_when_keep += 7 - number_mulls
				if (on_draw and cards_in_hand['Cavern'] > 0 and cards_in_hand['Scourge'] > 0):
					scourge_exiled += 1
					log("Exile Scourge to Cavern!")
				break
			elif (cards_in_hand['Temple'] == 0 and cards_in_hand['Powder'] == 0 and number_mulls < max_mulls):
				number_mulls += 1
				mull_type = 'Regular'
				log("Reg mull! number_mulls: "+str(number_mulls))
			elif (cards_in_hand['Temple'] == 0 and cards_in_hand['Powder'] == 0 and number_mulls >= max_mulls):
				cards_in_hand_when_keep += 7 - number_mulls
				log("Stop!")
				break
			elif (cards_in_hand['Temple'] == 0 and cards_in_hand['Powder'] > 0):
				mull_type = 'Via Powder'
				put_on_bottom = {
					'Temple': 0,
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
				description = "We bottomed " + str(put_on_bottom['Powder']) + " Powders, " + str(put_on_bottom['Cavern']) + " Caverns, "
				description += str(put_on_bottom['Other']) + " other cards, and " + str(put_on_bottom['Scourge']) + " Scourges."
				log("Powder mull! " + description)
				description = "We exiled "+ str(cards_in_hand['Powder'] - put_on_bottom['Powder']) + " Powders, "+ str(cards_in_hand['Cavern'] - put_on_bottom['Cavern']) + " Caverns, "
				description += str(cards_in_hand['Other'] - put_on_bottom['Other']) + " other cards, and "+ str(cards_in_hand['Scourge'] - put_on_bottom['Scourge']) + " Scourges."
				log(description)
									
	print('Probability to keep at least one Eldrazi Temple: ' + str(round(100 * count_temple / num_iterations,2))+"%")
	print('Expected number of Eternal Scourge exiled: ' + str(round(scourge_exiled / num_iterations,3)))
	print('Expected number of cards in hand when keeping: ' + str(round(cards_in_hand_when_keep / num_iterations,2)))
	print()





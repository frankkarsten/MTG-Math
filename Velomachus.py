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

def velomachus_prob(warp_hits, mastery_hits, warp_in_library, mastery_in_library, library_size):
	"""Determines the probability of hitting a certain number of Time Warps and Mizzix Mastery
	in the top 7 with Velomachus Lorehold"""
	if warp_hits + mastery_hits > 7 or warp_in_library + mastery_in_library > library_size:
		print("Input error!")
		return 0
	else:
		deck = {
			'Time Warp': warp_in_library,
			'Mizzix Mastery': mastery_in_library,
			'Other': library_size - warp_in_library - mastery_in_library
		}
		needed = {
			'Time Warp': warp_hits,
			'Mizzix Mastery': mastery_hits,
			'Other': 7 - warp_hits - mastery_hits
		}
		return multivariate_hypgeom(deck, needed)

def build_state_space_and_transition_matrix(deck):
	#State space is the union of {"0 extra turns", "1 extra turns", "2 extra turns", "3 extra turns"} and all viable (E, W, M, G, N) where:
	#E in {0, 1, 2, 3} is the number of extra turns--capped at 3 cause then you'd have won
	#W in {0, 1, ..., deck['Time Warp']} is the number of Time Warps (or Savor the Moments) remaining in library
	#M in {0, 1, ..., deck['Mizzix Mastery']} is the number Mizzix Mastery remaining in library
	#G in {True, False} indicates whether or not there is a Time Warp in the graveyard--more than 1 doesn't matter cause 3 extra turns max
	#N in {45, 52, 59} is the number of cards remaining in the deck. It's one-to-one with E, included only for clarity

	state_space = ["0 extra turns", "1 extra turns", "2 extra turns", "3 extra turns"]
	
	for E in [0, 1, 2]:
		for W in range(max(0, deck['Time Warp'] - 7 * E), deck['Time Warp']) if E > 0 else [deck['Time Warp']]:
			for M in range(deck['Mizzix Mastery'] + 1) if E > 0 else [deck['Mizzix Mastery']]:
				for G in [True, False] if E > 1 else [True] if E == 1 else [False]:
					state_space.append((E, W, M, G, 59 - 7 * E))
				
	transition_matrix = {}
	for s_from in state_space:
		for s_to in state_space:
			
			#Check for absorbing states
			from_absorbing_state = True if "extra turns" in s_from else False
			to_absorbing_state = True if "extra turns" in s_to else False
			
			#Check if this is a feasible turn transition, e.g., from 1 extra turn to 2 extra turns, not from 0 to 2 or from 2 to 1
			from_extra_turns = int(s_from[0]) if from_absorbing_state else s_from[0]
			to_extra_turns = int(s_to[0]) if to_absorbing_state else s_to[0]
			if to_absorbing_state and ((to_extra_turns == 3 and from_extra_turns == 2) or (to_extra_turns == from_extra_turns)):
				feasible_turn = True
			elif (not to_absorbing_state) and to_extra_turns == from_extra_turns + 1:
				feasible_turn = True
			else:
				feasible_turn = False
	
			#Check if this is a feasible Warp transition, e.g., from 4 to 2 Warps in library, not from 2 to 4
			if from_absorbing_state or to_absorbing_state:
				feasible_warp = True
			else:
				from_warp = s_from[1]
				to_warp = s_to[1]
				feasible_warp = True if to_warp in range(from_warp - 7, from_warp + 1) else False
	
			#Check if this is a feasible Mastery transition, e.g., from 2 to 1 Mastery in library, not from 1 to 2
			if from_absorbing_state or to_absorbing_state:
				feasible_mastery = True
			else:
				from_mastery = s_from[2]
				to_mastery = s_to[2]
				feasible_mastery = True if to_mastery in range(from_mastery - 7 + from_warp - to_warp, from_mastery + 1) else False
				
			#Check if this is a feasible graveyard transition
			if from_absorbing_state or to_absorbing_state:
				feasible_graveyard = True
			else:
				warp_already_in_gy = s_from[3]
				warp_in_gy_afterwards = s_to[3]
				warp_put_in_gy = from_warp > to_warp
				warp_removed_from_gy = (from_warp == to_warp) and (from_mastery > to_mastery) and warp_already_in_gy
				if warp_put_in_gy and warp_in_gy_afterwards == True:
					feasible_graveyard = True
				elif warp_removed_from_gy and warp_already_in_gy == True and warp_in_gy_afterwards == False:
					feasible_graveyard = True
				else:
					feasible_graveyard = False
			
			if feasible_warp and feasible_turn and feasible_mastery and feasible_graveyard:
				if from_absorbing_state:
					#Absorbing states don't go anywhere else
					transition_matrix[(s_from,s_to)] = 1 if s_from == s_to else 0
				else:
					warp_in_library = s_from[1]
					mastery_in_library = s_from[2]
					warp_in_gy = s_from[3]
					library_size = s_from[4]
					transition_matrix[(s_from,s_to)] = 0
					max_number_of_mastery_to_possibly_hit = min(mastery_in_library, 7)
					max_number_of_warps_to_possibly_hit = min(warp_in_library, 7)
					if to_absorbing_state and to_extra_turns < 3:
						#This happens when we can't hit an extra turn
						#Because we didn't hit a Time Warp
						warp_hits = 0
						#And, for any Mastery we might hit in the top 7, there's nothing to flash back yet
						for mastery_hits in [0] if warp_in_gy else range(max_number_of_mastery_to_possibly_hit + 1):
							transition_matrix[(s_from,s_to)] += velomachus_prob(warp_hits, mastery_hits, warp_in_library, mastery_in_library, library_size)
					if to_absorbing_state and to_extra_turns == 3:
						#This happens when we do hit an extra turn
						for warp_hits in range(max_number_of_warps_to_possibly_hit + 1):
							for mastery_hits in range(max_number_of_mastery_to_possibly_hit + 1):
								extra_turn_hit = True if warp_hits > 0 or (mastery_hits > 0 and warp_in_gy) else False
								if extra_turn_hit:
									transition_matrix[(s_from,s_to)] += velomachus_prob(warp_hits, mastery_hits, warp_in_library, mastery_in_library, library_size)
					if not to_absorbing_state:
						warp_hits = s_from[1] - s_to[1]
						mastery_hits = s_from[2] - s_to[2]
						transition_matrix[(s_from,s_to)] = velomachus_prob(warp_hits, mastery_hits, warp_in_library, mastery_in_library, library_size)
	
			else:
				transition_matrix[(s_from,s_to)] = 0	
	return (state_space, transition_matrix)

def give_results(deck, verbose=True):
	state_space, transition_matrix = build_state_space_and_transition_matrix(deck)
	print("---Outcomes for deck", deck)
	
	probability_distribution_over_state_space = [{s: 0 for s in state_space} for t in [0,1,2,3]]
	#So e.g. probability_distribution_over_state_space[1][s] gives the probability of being in state s after the 1st Velomachus trigger
	#Now set the starting state
	probability_distribution_over_state_space[0][(0, deck['Time Warp'], deck['Mizzix Mastery'], False, 59)] = 1
	
	for velomachus_trigger in [1, 2, 3]:
		print("We now transition to trigger number", velomachus_trigger)
		for s_from in state_space:
			for s_to in state_space:
				probability_distribution_over_state_space[velomachus_trigger][s_to] += probability_distribution_over_state_space[velomachus_trigger - 1][s_from] * transition_matrix[(s_from,s_to)] 
		for key, value in probability_distribution_over_state_space[velomachus_trigger].items():
			if verbose:
				print(key,value)
			elif velomachus_trigger==3 and "extra turns" in key:
				print(key,value)

modern_deck = {
	'Time Warp': 8,
	'Mizzix Mastery': 0,
	'Other': 51,
}

give_results(modern_deck)

for Savor in [0, 1, 2, 3]:
	modern_deck = {
		'Time Warp': 4 + Savor,
		'Mizzix Mastery': 0,
		'Other': 55 - Savor,
	}

	give_results(modern_deck, verbose=False)


historic_deck = {
	'Time Warp': 4,
	'Mizzix Mastery': 4,
	'Other': 51,
}

give_results(historic_deck)

for Mastery in [0, 1, 2, 3]:
	historic_deck = {
		'Time Warp': 4,
		'Mizzix Mastery': Mastery,
		'Other': 55 - Mastery,
	}

	give_results(historic_deck, verbose=False)

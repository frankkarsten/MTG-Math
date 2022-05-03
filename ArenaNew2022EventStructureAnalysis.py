import numpy as np

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
	
def binom_prob(n, k, p):
	"""	
	Parameters:
		n - Number of independent trials
		k - Number of successes
		p - Probability of success in each trial
	Returns - The binomial probability of getting exactly k successes
	"""
	return binom(n, k) * ( p ** k ) * ( ( 1- p ) ** ( n - k) )

def record_prob(p, Wmax, Lmax, W, L):
	"""	
	Parameters:
		p - The probability to win a round
		Wmax, Lmax - You play an event until Wmax wins or Wmax losses, whichever comes first
		W, L - The record you're interested in
	Returns - The probability to end the event with W wins and L losses. It must hold that either Wmax = W or Lmax = L.
	"""
	if W < Wmax and L == Lmax:
		#We first win W rounds and lose L - 1 rounds in any order, then lose the last round
		return binom_prob(W + Lmax - 1, W, p) * (1 - p)
	elif W == Wmax and L < Lmax:
		#We first win W - 1 rounds and lose L rounds in any order, then win the last round
		return binom_prob(Wmax + L - 1, Wmax - 1, p) * p
	else:
		#This isn't a feasible record
		return 0

def match_win_prob(G):
	"""	
	Parameters:
		G - The game win rate
	Returns - The probability to win a best-of-three match, assuming constant game win rate
	"""
	return G * G + 2 * G * G * (1 - G)

def prob_max_wins(G, bestof, max_wins, max_losses):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
		max_wins, max_losses - You play an event until Wmax wins or Wmax losses, whichever comes first
	Returns - The probability to reach the maximum number of wins in the event
	"""
	round_win_prob = G if bestof == 1 else match_win_prob(G)
	answer = 0
	for losses in range(max_losses):
		answer += record_prob(round_win_prob, max_wins, max_losses, max_wins, losses)
	return answer

def expected_payout(G, bestof, max_wins, max_losses, payout_dist):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
		max_wins, max_losses - You play an event until Wmax wins or Wmax losses, whichever comes first
		payout_dist - a dictionary that, for 0<=W<=max_wins gives the payout payout_dist[W] for ending with W wins
	Returns - The expected earnings in the event, in gems if payout_dist was also in gems
	"""	
	expectation = 0
	round_win_prob = G if bestof == 1 else match_win_prob(G)
	#Determine contribution for records with max losses
	for wins in range(max_wins):
		record_probability = record_prob(round_win_prob, max_wins, max_losses, wins, max_losses)
		expectation += record_probability * payout_dist[wins]
	#Determine contribution for records with max wins
	for losses in range(max_losses):
		record_probability = record_prob(round_win_prob, max_wins, max_losses, max_wins, losses)
		expectation += record_probability * payout_dist[max_wins]
	return expectation

gem_per_dollar = 200
ArenaChampionship_dollar = 6250

print()
print("---------Qualifier Weekend")
print()

max_wins_QW = 7
max_losses_QW = 2
bestof = 3
gems_QW_Day2 = {
	0: 250,
	1: 500,
	2: 1000,
	3: 1500,
	4: 2000,
	5: 2500,
	6: 3000,
	7: 5000
}
gems_QW_Day1 = {
	0: 500,
	1: 1000,
	2: 3000,
	3: 5000,
	4: 7500,
	5: 10000,
	6: 15000,
	7: 20000
}

all_game_winrates_floating = np.arange(0.10, 0.901, 0.001)
reasonable_game_winrates_floating = np.arange(0.20, 0.801, 0.001)
#all_game_winrates_floating should be [0.100, 0.101, ..., 0.900] but due to floating point imprecision, some entries may be like 0.800000000001
all_game_winrates = []
for G in all_game_winrates_floating:
	all_game_winrates.append(round(G,3))
reasonable_game_winrates = []
for G in reasonable_game_winrates_floating:
	reasonable_game_winrates.append(round(G,3))
output_game_winrates = [.44, .46, .48, .50, .52, .54, .56, .58, .60]

totalEV = {}
#This dictionary will eventually hold the value totalEV[G] in gems for a player with game win rate G in a Qualifier Weekend

for G in all_game_winrates:
	if G in output_game_winrates:
		print(f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):")
	
	qualification_prob_Day2 = prob_max_wins(G, bestof, max_wins_QW, max_losses_QW)
	Gem_EV_Day2 = expected_payout(G, bestof, max_wins_QW, max_losses_QW, gems_QW_Day2)
	if G in output_game_winrates:
		print(f"In Day 2: {qualification_prob_Day2*100: .2f}% to qualify and gem EV of{Gem_EV_Day2: .0f}.")
	
	qualification_prob_Day1 = prob_max_wins(G, bestof, max_wins_QW, max_losses_QW) * qualification_prob_Day2
	Gem_EV_Day1 = expected_payout(G, bestof, max_wins_QW, max_losses_QW, gems_QW_Day1)
	totalEV[G] = Gem_EV_Day1 + prob_max_wins(G, bestof, max_wins_QW, max_losses_QW) * Gem_EV_Day2
	totalEV[G] += qualification_prob_Day1 * ArenaChampionship_dollar * gem_per_dollar
	totalEV_in_dollar = totalEV[G] / gem_per_dollar
	if G in output_game_winrates:
		print(f"In Day 1: {qualification_prob_Day1*100: .2f}% to qualify and gem EV of{Gem_EV_Day1: .0f}. Total EV ${totalEV_in_dollar :.0f}.")

print()
print("---------Qualifier Play-In")
print()

max_wins_bo1 = 6
max_losses_bo1 = 2
max_wins_bo3 = 4
max_losses_bo3 = 1
gems_PlayIn_bo1 = {
	0: 500,
	1: 1000,
	2: 1500,
	3: 3000,
	4: 4500,
	5: 6000,
	6: 6000
}
gems_PlayIn_bo3 = {
	0: 500,
	1: 2000,
	2: 4500,
	3: 6000,
	4: 6000
}

#Since it's rebuy, we're also interested in the number of expected number of games required to earn the max wins, for which we need some functions

def expected_games(G, outcome):
	"""	
	Parameters:
		G - The game win rate
		outcome - 'win' or 'loss'
	Returns - The expected number of games played in a best-of-three match with the given outcome
	"""
	if outcome == 'win':
		prob_2_0 = G * G
		prob_2_1 = 2 * G * G * (1 - G)
		prob_match_win = prob_2_0 + prob_2_1
		return ( 2 * prob_2_0 + 3 * prob_2_1 ) / prob_match_win
	if outcome == 'loss':
		prob_0_2 = (1 - G) * (1 - G)
		prob_1_2 = 2 * G * (1 - G) * ( 1 - G)
		prob_match_loss = prob_0_2 + prob_1_2
		return ( 2 * prob_0_2 + 3 * prob_1_2 ) / prob_match_loss

def expected_games_success(G, bestof, max_wins, max_losses):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
		max_wins, max_losses - You play an event until Wmax wins or Wmax losses, whichever comes first
	Returns - The expected number of games played when you WIN the maximum number of rounds
	"""	
	expectation = 0
	success_prob = prob_max_wins(G, bestof, max_wins, max_losses)
	if bestof == 1:
		for losses in range(max_losses):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of wins
			record_probability = record_prob(G, max_wins, max_losses, max_wins, losses) / success_prob
			nr_games = max_wins + losses
			expectation += record_probability * nr_games
	if bestof == 3:
		for losses in range(max_losses):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of wins
			record_probability = record_prob(match_win_prob(G), max_wins, max_losses, max_wins, losses) / success_prob
			nr_games = max_wins * expected_games(G, 'win') + losses * expected_games(G, 'loss')
			expectation += record_probability * nr_games
	return expectation

def expected_games_failure(G, bestof, max_wins, max_losses):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
		max_wins, max_losses - You play an event until Wmax wins or Wmax losses, whichever comes first
	Returns - The expected number of games played when you LOSE the maximum number of rounds
	"""	
	expectation = 0
	failure_prob = 1 - prob_max_wins(G, bestof, max_wins, max_losses)
	if bestof == 1:
		for wins in range(max_wins):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of losses
			record_probability = record_prob(G, max_wins, max_losses, wins, max_losses) / failure_prob
			nr_games = wins + max_losses
			expectation += record_probability * nr_games
	if bestof == 3:
		for wins in range(max_wins):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of losses
			record_probability = record_prob(match_win_prob(G), max_wins, max_losses, wins, max_losses) / failure_prob
			nr_games = wins * expected_games(G, 'win') + max_losses * expected_games(G, 'loss')
			expectation += record_probability * nr_games
	return expectation

def expected_games_until_qualification(G, bestof, max_wins, max_losses):
	"""	
	Parameters:
		G - The game win rate, should be larger than 0 and smaller than 1
		bestof - Either 1 or 3
	Returns - The expected number of games played until earning a Day 2 qualification
		Denoting this quantity by E, it's derived by solving:
		E = (exp_games_failure + E) * failure_prob + exp_games_success * success_prob
	"""	
	success_prob = prob_max_wins(G, bestof, max_wins, max_losses)
	failure_prob = 1 - prob_max_wins(G, bestof, max_wins, max_losses)
	exp_games_failure = expected_games_failure(G, bestof, max_wins, max_losses)
	exp_games_success = expected_games_success(G, bestof, max_wins, max_losses)
	
	return (failure_prob * exp_games_failure + success_prob * exp_games_success) / success_prob

break_even_point_reached_bo1 = False
break_even_point_reached_bo3 = False
entry_fee = 4000
playin_point_value_in_gems = {}
#This dictionary will hold the value playin_point_value_in_gems[G] in gems for a player with game win rate G in the Qualifier Weekend

for G in all_game_winrates:
	if G in output_game_winrates:
		print(f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):")
	
	bestof = 1
	qualification_prob = prob_max_wins(G, bestof, max_wins_bo1, max_losses_bo1)
	Gem_EV = expected_payout(G, bestof, max_wins_bo1, max_losses_bo1, gems_PlayIn_bo1)
	exp_games = expected_games_until_qualification(G, bestof, max_wins_bo1, max_losses_bo1)
	totalEV_PlayIn = Gem_EV + qualification_prob * totalEV[G]
	if G in output_game_winrates:
		print(f"In Bo1: {qualification_prob*100: .1f}% to qualify and gem EV of{Gem_EV: .0f}. Needs {exp_games :.0f} games. Total EV ${totalEV_PlayIn/gem_per_dollar :.2f}.")
	if totalEV_PlayIn > entry_fee and not break_even_point_reached_bo1:
		print(f"Break-even in Bo1 at game win rate {G}")
		break_even_point_reached_bo1 = True
		
	bestof = 3
	qualification_prob = prob_max_wins(G, bestof, max_wins_bo3, max_losses_bo3)
	Gem_EV = expected_payout(G, bestof, max_wins_bo3, max_losses_bo3, gems_PlayIn_bo3)
	exp_games = expected_games_until_qualification(G, bestof, max_wins_bo3, max_losses_bo3)
	totalEV_PlayIn = Gem_EV + qualification_prob * totalEV[G]
	
	playin_point_value_in_gems[G] = min(totalEV_PlayIn, 4000) / 20
	if G in output_game_winrates:
		print(f"In Bo3: {qualification_prob*100: .1f}% to qualify and gem EV of{Gem_EV: .0f}. Needs {exp_games :.0f} games. Total EV ${totalEV_PlayIn/gem_per_dollar :.2f}.")
	if totalEV_PlayIn > entry_fee and not break_even_point_reached_bo3:
		print(f"Break-even in Bo3 at game win rate {G}")
		break_even_point_reached_bo3 = True


print()
print("---------Arena Open")
print()

max_wins_bo1 = 7
max_losses_bo1 = 3
max_wins_bo3 = 4
max_losses_bo3 = 1
gems_ArenaOpen_Day1_bo1 = {
	0: 0,
	1: 0,
	2: 0,
	3: 0,
	4: 0,
	5: 1000,
	6: 2500,
	7: 0
}
gems_ArenaOpen_Day1_bo3 = {
	0: 0,
	1: 1000,
	2: 3000,
	3: 5000,
	4: 0
}
max_wins_Day2 = 8
max_losses_Day2 = 2
entry_fee = 5000
break_even_point_reached_bo1 = False
break_even_point_reached_bo3 = False

for G in all_game_winrates:
	if G in output_game_winrates:
		print(f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):")

	bestof = 3
	#Six or more wins on Day 2 of an Arena Open now also grants a Qualifier Weekend token
	gems_ArenaOpen_Day2 = {
		0: 5000,
		1: 5000,
		2: 5000,
		3: 7500,
		4: 10000,
		5: 25000,
		6: 1000 * gem_per_dollar + totalEV[G],
		7: 2000 * gem_per_dollar + totalEV[G],
		8: 2500 * gem_per_dollar + totalEV[G]
	}
	Total_EV_Day2 = expected_payout(G, bestof, max_wins_Day2, max_losses_Day2, gems_ArenaOpen_Day2)
	if G in output_game_winrates:
		print(f"In Day 2: Effective total EV in gems of{Total_EV_Day2: .0f}.")

	bestof = 1
	qualification_prob = prob_max_wins(G, bestof, max_wins_bo1, max_losses_bo1)
	Gem_EV = expected_payout(G, bestof, max_wins_bo1, max_losses_bo1, gems_ArenaOpen_Day1_bo1)
	exp_games = expected_games_until_qualification(G, bestof, max_wins_bo1, max_losses_bo1)
	totalEV_Day1 = Gem_EV + qualification_prob * Total_EV_Day2
	if G in output_game_winrates:
		print(f"In Bo1: {qualification_prob*100: .1f}% to qualify and gem EV of{Gem_EV: .0f}. Needs {exp_games :.0f} games. Total EV ${totalEV_Day1/gem_per_dollar :.0f}.")
	if totalEV_Day1 > entry_fee and not break_even_point_reached_bo1:
		print(f"Break-even in Bo1 at game win rate {G}")
		break_even_point_reached_bo1 = True
	
	bestof = 3
	qualification_prob = prob_max_wins(G, bestof, max_wins_bo3, max_losses_bo3)
	Gem_EV = expected_payout(G, bestof, max_wins_bo3, max_losses_bo3, gems_ArenaOpen_Day1_bo3)
	exp_games = expected_games_until_qualification(G, bestof, max_wins_bo3, max_losses_bo3)
	totalEV_Day1 = Gem_EV + qualification_prob * Total_EV_Day2
	if G in output_game_winrates:
		print(f"In Bo3: {qualification_prob*100: .1f}% to qualify and gem EV of{Gem_EV: .0f}. Needs {exp_games :.0f} games. Total EV ${totalEV_Day1/gem_per_dollar :.0f}.")
	if totalEV_Day1 > entry_fee and not break_even_point_reached_bo3:
		print(f"Break-even in Bo3 at game win rate {G}")
		break_even_point_reached_bo3 = True

print()
print("---------Traditional Drafts")
print()

#We'll need to specify some pack values
pack_value_in_gems = 150
draft_pack_value_in_gems = 85

#We'll look at a wider range of winrates
output_game_winrates = [.40, .42, .44, .46, .48, .50, .52, .54, .56, .58, .60, .62, .64, .66, .68, .70]
bestof = 3
nr_rounds = 3

draft_packs_per_event = 3
gems_TradDraft = {
	0: 100,
	1: 250,
	2: 1000,
	3: 2500
}
entry_fee = 1500
break_even_point_reached = False

#It's always exactly three rounds, so we'll need a different way to calculate records.

for G in reasonable_game_winrates:
	
	extra_value_TradDraft = {
		0: 1 * pack_value_in_gems,
		1: 1 * pack_value_in_gems,
		2: 3 * pack_value_in_gems,
		3: 6 * pack_value_in_gems + 2 * playin_point_value_in_gems[round(G - 0.1, 3)]
	}
	
	expected_gems = 0
	expected_total_value = draft_packs_per_event * draft_pack_value_in_gems
	for wins in [0, 1, 2, 3]:
		record_probability = binom_prob(nr_rounds, wins, match_win_prob(G))
		expected_gems += record_probability * gems_TradDraft[wins]
		expected_total_value += record_probability * (gems_TradDraft[wins] + extra_value_TradDraft[wins])
	
	if G in output_game_winrates:
		output_string = f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):"
		output_string += f" {expected_gems:.0f} expected pure gems and {expected_total_value:.0f} gems in total value."
		print(output_string)
	if expected_gems > entry_fee and not break_even_point_reached:
		print(f"Break-even at game win rate {G} (match winrate {match_win_prob(G):.3f})")
		break_even_point_reached = True
	
print()
print("---------Premier Drafts")
print()		
		
bestof = 1
max_wins = 7
max_losses = 3
draft_packs_per_event = 3
gems_PremierDraft = {
	0: 50,
	1: 100,
	2: 250,
	3: 1000,
	4: 1400,
	5: 1600,
	6: 1800,
	7: 2200
}
extra_value_PremierDraft = {
	0: 1 * pack_value_in_gems,
	1: 1 * pack_value_in_gems,
	2: 2 * pack_value_in_gems,
	3: 2 * pack_value_in_gems,
	4: 3 * pack_value_in_gems,
	5: 4 * pack_value_in_gems,
	6: 5 * pack_value_in_gems,
	7: 6 * pack_value_in_gems
}

entry_fee = 1500
break_even_point_reached = False

for G in reasonable_game_winrates:
	
	expected_gems = expected_payout(G, bestof, max_wins, max_losses, gems_PremierDraft)
	expected_total_value = expected_gems + draft_packs_per_event * draft_pack_value_in_gems
	expected_total_value += expected_payout(G, bestof, max_wins, max_losses, extra_value_PremierDraft)

	if G in output_game_winrates:
		output_string = f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):"
		output_string += f" {expected_gems:.0f} expected pure gems and {expected_total_value:.0f} gems in total value."
		print(output_string)
	if expected_gems > entry_fee and not break_even_point_reached:
		print(f"Break-even at game win rate {G} (match winrate {match_win_prob(G):.3f})")
		break_even_point_reached = True

print()
print("---------Quick Drafts")
print()		
		
bestof = 1
max_wins = 7
max_losses = 3
draft_packs_per_event = 3
gems_QuickDraft = {
	0: 50,
	1: 100,
	2: 200,
	3: 300,
	4: 450,
	5: 650,
	6: 850,
	7: 950
}
extra_value_QuickDraft = {
	0: 1.2 * pack_value_in_gems,
	1: 1.22 * pack_value_in_gems,
	2: 1.24 * pack_value_in_gems,
	3: 1.26 * pack_value_in_gems,
	4: 1.30 * pack_value_in_gems,
	5: 1.35 * pack_value_in_gems,
	6: 1.40 * pack_value_in_gems,
	7: 2 * pack_value_in_gems
}

entry_fee = 750
break_even_point_reached = False

for G in reasonable_game_winrates:
	
	expected_gems = expected_payout(G, bestof, max_wins, max_losses, gems_QuickDraft)
	expected_total_value = expected_gems + draft_packs_per_event * draft_pack_value_in_gems
	expected_total_value += expected_payout(G, bestof, max_wins, max_losses, extra_value_QuickDraft)

	if G in output_game_winrates:
		output_string = f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):"
		output_string += f" {expected_gems:.0f} expected pure gems and {expected_total_value:.0f} gems in total value."
		print(output_string)
	if expected_gems > entry_fee and not break_even_point_reached:
		print(f"Break-even at game win rate {G} (match winrate {match_win_prob(G):.3f})")
		break_even_point_reached = True

print()
print("---------Sealed Events")
print()		
		
bestof = 1
max_wins = 7
max_losses = 3
gems_Sealed = {
	0: 200,
	1: 400,
	2: 600,
	3: 1200,
	4: 1400,
	5: 1600,
	6: 2000,
	7: 2200
}

entry_fee = 2000
draft_packs_per_event = 6
extra_value_Sealed = 3 * pack_value_in_gems
break_even_point_reached = False

for G in all_game_winrates:
	
	expected_gems = expected_payout(G, bestof, max_wins, max_losses, gems_Sealed)
	expected_total_value = expected_gems + draft_packs_per_event * draft_pack_value_in_gems + extra_value_Sealed
	
	if G in output_game_winrates:
		output_string = f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):"
		output_string += f" {expected_gems:.0f} expected pure gems and {expected_total_value:.0f} gems in total value."
		print(output_string)
	if expected_gems > entry_fee and not break_even_point_reached:
		print(f"Break-even at game win rate {G} (match winrate {match_win_prob(G):.3f})")
		break_even_point_reached = True

print()
print("---------Bo1 Constructed Events")
print()		
		
bestof = 1
max_wins = 7
max_losses = 3
gems_Bo1Constructed = {
	0: 25,
	1: 50,
	2: 75,
	3: 200,
	4: 300,
	5: 400,
	6: 450,
	7: 500
}

entry_fee = 375
break_even_point_reached = False

for G in reasonable_game_winrates:

	extra_value_Bo1Constructed = {
		0: 0,
		1: 0,
		2: 1 * pack_value_in_gems,
		3: 1 * pack_value_in_gems,
		4: 1 * pack_value_in_gems,
		5: 2 * pack_value_in_gems,
		6: 2 * pack_value_in_gems,
		7: 3 * pack_value_in_gems + 1 * playin_point_value_in_gems[round(G - 0.1, 3)]
	}

	expected_gems = expected_payout(G, bestof, max_wins, max_losses, gems_Bo1Constructed)
	expected_total_value = expected_gems + expected_payout(G, bestof, max_wins, max_losses, extra_value_Bo1Constructed)

	if G in output_game_winrates:
		output_string = f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):"
		output_string += f" {expected_gems:.0f} expected pure gems and {expected_total_value:.0f} gems in total value."
		print(output_string)
	if expected_gems > entry_fee and not break_even_point_reached:
		print(f"Break-even at game win rate {G} (match winrate {match_win_prob(G):.3f})")
		break_even_point_reached = True

print()
print("---------Bo3 Constructed Events")
print()

bestof = 3
nr_rounds = 5

gems_Bo3Constructed = {
	0: 50,
	1: 100,
	2: 150,
	3: 600,
	4: 800,
	5: 1000
}
entry_fee = 750
break_even_point_reached = False

#It's always exactly five rounds, so we'll need a different way to calculate records.

for G in reasonable_game_winrates:
	
	extra_value_Bo3Constructed = {
		0: 1 * pack_value_in_gems,
		1: 1 * pack_value_in_gems,
		2: 2 * pack_value_in_gems,
		3: 2 * pack_value_in_gems,
		4: 2 * pack_value_in_gems,
		5: 3 * pack_value_in_gems + 4 * playin_point_value_in_gems[round(G - 0.1, 3)]
	}
	
	expected_gems = 0
	expected_total_value = 0
	for wins in [0, 1, 2, 3, 4, 5]:
		record_probability = binom_prob(nr_rounds, wins, match_win_prob(G))
		expected_gems += record_probability * gems_Bo3Constructed[wins]
		expected_total_value += record_probability * (gems_Bo3Constructed[wins] + extra_value_Bo3Constructed[wins])
	
	if G in output_game_winrates:
		output_string = f"For game winrate {G:.2f} (match winrate {match_win_prob(G):.3f}):"
		output_string += f" {expected_gems:.0f} expected pure gems and {expected_total_value:.0f} gems in total value."
		print(output_string)
	if expected_gems > entry_fee and not break_even_point_reached:
		print(f"Break-even at game win rate {G} (match winrate {match_win_prob(G):.3f})")
		break_even_point_reached = True
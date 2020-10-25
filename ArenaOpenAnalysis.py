import numpy as np
from matplotlib import pyplot as plt

#Let's define some values for Day 1. Keys represent bestof
max_wins = {1: 7, 3: 4}
max_losses = {1: 3, 3: 1}

#Keys are tuples of the form (bestof, wins)
Day_1_gems = {
	(1, 0): 0,
	(1, 1): 0,
	(1, 2): 0,
	(1, 3): 400,
	(1, 4): 800,
	(1, 5): 1200,
	(1, 6): 1600,
	(1, 7): 2000,
	(3, 0): 0,
	(3, 1): 1000,
	(3, 2): 2500,
	(3, 3): 5000,
	(3, 4): 5000
}

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
		return (binom_prob(Wmax + L - 1, Wmax - 1, p) * p)
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

def qualification_prob(G, bestof):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
	Returns - The probability to earn a Day 2 qualification in an Arena Open 
	"""
	round_win_prob = G if bestof == 1 else match_win_prob(G)
	answer = 0
	for losses in range(max_losses[bestof]):
		answer += record_prob(round_win_prob, max_wins[bestof], max_losses[bestof], max_wins[bestof], losses)
	return answer

#Determine and plot the probabilities to earn a Day 2 qualification
x_axis = np.arange(0.40, 0.701, 0.001)
y_axis = np.empty(301)
fig, ax = plt.subplots()
for bestof in [1,3]:
	for x in range(301):
		y_axis[x] = qualification_prob(0.40+x/1000, bestof)
	ax.plot(x_axis, y_axis, label='best-of-'+str(bestof))
	ax.set(xlabel='Game win rate', ylabel='Day 2 qualification probability',
		   title='Arena Open: Probability to earn a Day 2 qualification')
	ax.set_xticklabels(['{:.0%}'.format(x) for x in ax.get_xticks()])
	ax.set_yticklabels(['{:.0%}'.format(y) for y in ax.get_yticks()])
	ax.grid(True)
	plt.legend()
	plt.xlim(.4,.7)
	plt.ylim(0,.48)
fig.savefig("Day_2_qualification_probability.png")

print("\n")
print(f'Probability to qualify in a Bo1 event for a 50% win rate player: {qualification_prob(0.5,1) * 100: .1f}%') 
print(f'Expected Bo1 events till qualification for a 50% win rate player: {1/qualification_prob(0.5,1) : .1f}') 
print(f'Probability to qualify in a Bo3 event for a 50% win rate player: {qualification_prob(0.5,3) * 100: .1f}%') 
print(f'Expected Bo1 events till qualification for a 50% win rate player: {1/qualification_prob(0.5,3) : .1f}') 

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

def expected_games_event(G, bestof):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
	Returns - The expected number of games played in one event
	"""	
	expectation = 0
	W = max_wins[bestof]
	success_prob = qualification_prob(G, bestof)
	round_win_prob = G if bestof == 1 else match_win_prob(G)
	games_per_round_win = 1 if bestof == 1 else expected_games(G, 'win')
	games_per_round_loss = 1 if bestof == 1 else expected_games(G, 'loss')
	for wins in range(max_wins[bestof]):
		record_probability = record_prob(round_win_prob, max_wins[bestof], max_losses[bestof], wins, max_losses[bestof])
		nr_games = wins * games_per_round_win + max_losses[bestof] * games_per_round_loss
		expectation += record_probability * nr_games
	for losses in range(max_losses[bestof]):
		record_probability = record_prob(round_win_prob, max_wins[bestof], max_losses[bestof], max_wins[bestof], losses)
		nr_games = max_wins[bestof] * games_per_round_win + losses * games_per_round_loss
		expectation += record_probability * nr_games
	return expectation
	
def expected_games_success(G, bestof):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
	Returns - The expected number of games played when you WIN the maximum number of rounds
	"""	
	expectation = 0
	W = max_wins[bestof]
	success_prob = qualification_prob(G, bestof)
	if bestof == 1:
		for losses in range(max_losses[bestof]):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of wins
			record_probability = record_prob(G, W, max_losses[bestof], W, losses) / success_prob
			nr_games = W + losses
			expectation += record_probability * nr_games
	if bestof == 3:
		for losses in range(max_losses[bestof]):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of wins
			record_probability = record_prob(match_win_prob(G), W, max_losses[bestof], W, losses) / success_prob
			nr_games = W * expected_games(G, 'win') + losses * expected_games(G, 'loss')
			expectation += record_probability * nr_games
	return expectation

def expected_games_failure(G, bestof):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
	Returns - The expected number of games played when you LOSE the maximum number of rounds
	"""	
	expectation = 0
	L = max_losses[bestof]
	failure_prob = 1 - qualification_prob(G, bestof)
	if bestof == 1:
		for wins in range(max_wins[bestof]):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of losses
			record_probability = record_prob(G, max_wins[bestof], L, wins, L) / failure_prob
			nr_games = wins + L
			expectation += record_probability * nr_games
	if bestof == 3:
		for wins in range(max_wins[bestof]):
			#Consider the probability of achieving this record, conditional on reaching the maximum number of losses
			record_probability = record_prob(match_win_prob(G), max_wins[bestof], L, wins, L) / failure_prob
			nr_games = wins * expected_games(G, 'win') + L * expected_games(G, 'loss')
			expectation += record_probability * nr_games
	return expectation

def expected_games_until_qualification(G, bestof):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3
	Returns - The expected number of games played until earning a Day 2 qualification
		Denoting this quantity by E, it's derived by solving:
		E = (exp_games_failure + E) * failure_prob + exp_games_success * success_prob
	"""	
	success_prob = qualification_prob(G, bestof)
	failure_prob = 1 - qualification_prob(G, bestof)
	exp_games_failure = expected_games_failure(G, bestof) if G < 1.0 else 0
	exp_games_success = expected_games_success(G, bestof)
	
	return (failure_prob * exp_games_failure + success_prob * exp_games_success) / success_prob

print("\n")
print(f'Expected nr games per Bo1 event for a 50% win rate player: {expected_games_event(0.5,1): .1f}') 
print(f'Expected nr games per Bo3 event for a 50% win rate player: {expected_games_event(0.5,3): .1f}') 

#Determine and plot the expected number of games to earn a Day 2 qualification
x_axis = np.arange(0.40, 0.701, 0.001)
y_axis = np.empty(301)
fig, ax = plt.subplots()
for bestof in [1,3]:
	for x in range(301):
		y_axis[x] = expected_games_until_qualification(0.40+x/1000, bestof)
	ax.plot(x_axis, y_axis, label='best-of-'+str(bestof))
	ax.set(xlabel='Game win rate', ylabel='Expected number of games',
		   title='Arena Open: Expected number of games to earn a Day 2 qualification')
	ax.set_xticklabels(['{:.0%}'.format(x) for x in ax.get_xticks()])
	ax.set_yticklabels(['{:.0f}'.format(y) for y in ax.get_yticks()])
	ax.grid(True)
	plt.xlim(.4,.7)
	plt.ylim(0,250)
	plt.legend()
fig.savefig("Day_2_qualification_nr_games.png")

print("\n")
print(f'Expected nr games per qualification via Bo1, 50% win rate: {expected_games_until_qualification(0.5,1): .1f}') 
print(f'Expected nr games per qualification via Bo3, 50% win rate: {expected_games_until_qualification(0.5,3): .1f}') 
print("\n")

#Let's define some values for Day 2. Keys represent wins
Day_2_gems = {
	0: 0,
	1: 2000,
	2: 4000,
	3: 6000,
	4: 10000,
	5: 20000,
	6: 0,
	7: 0
}

Day_2_dollars = {
	0: 0,
	1: 0,
	2: 0,
	3: 0,
	4: 0,
	5: 0,
	6: 1000,
	7: 2000
}

dollar_per_gem = 0.005

def expected_dollar_Day2(G):
	"""	
	Parameters:
		G - The game win rate
	Returns - The expected earnings (in dollar, with gems translated to dollars) on Day 2
	Note - For Day 2, it's play until 7 wins or 2 losses
	"""	
	expectation = 0
	p = match_win_prob(G)
	for wins in [0, 1, 2, 3, 4, 5, 6]:
		record_probability = record_prob(p, 7, 2, wins, 2)
		dollar_earnings = Day_2_gems[wins] * dollar_per_gem + Day_2_dollars[wins]
		expectation += record_probability * dollar_earnings
	for losses in [0, 1]:
		record_probability = record_prob(p, 7, 2, 7, losses)
		dollar_earnings = Day_2_gems[7] * dollar_per_gem + Day_2_dollars[7]
		expectation += record_probability * dollar_earnings
	return expectation

def expected_profit_Day1(G, bestof):
	"""	
	Parameters:
		G - The game win rate
		bestof - Either 1 or 3, represents the type of event entered
	Returns - The expected profit (in dollar, with gems translated to dollars) on both Day 1 AND Day 2, minus entry fee
	"""	
	expectation = 0
	round_win_prob = G if bestof == 1 else match_win_prob(G)
	for wins in range(max_wins[bestof]):
		record_probability = record_prob(round_win_prob, max_wins[bestof], max_losses[bestof], wins, max_losses[bestof])
		dollar_earnings = Day_1_gems[(bestof, wins)] * dollar_per_gem
		expectation += record_probability * dollar_earnings
	for losses in range(max_losses[bestof]):
		record_probability = record_prob(round_win_prob, max_wins[bestof], max_losses[bestof], max_wins[bestof], losses)
		dollar_earnings = Day_1_gems[(bestof,max_wins[bestof])] * dollar_per_gem + expected_dollar_Day2(G)
		expectation += record_probability * dollar_earnings
	return expectation - 20

#Determine and plot the expected number of games to earn a Day 2 qualification
x_axis = np.arange(0.40, 0.701, 0.001)
y_axis = np.empty(301)
fig, ax = plt.subplots()
for bestof in [1,3]:
	for x in range(301):
		y_axis[x] = expected_profit_Day1(0.40+x/1000, bestof)
	ax.plot(x_axis, y_axis, label='best-of-'+str(bestof))
	ax.set(xlabel='Game win rate', ylabel='Expected profit',
		   title='Arena Open: Expected profit as a function of game win rate')
	ax.set_xticklabels(['{:.0%}'.format(x) for x in ax.get_xticks()])
	ax.set_yticklabels(['${:.0f}'.format(y) for y in ax.get_yticks()])
	ax.grid(True)
	ax.axhline(linewidth=2, color='k')
	plt.legend()
	plt.xlim(.4,.7)
fig.savefig("Expected_profit_full.png")

#Let's zoom in
x_axis = np.arange(0.40, 0.701, 0.001)
y_axis = np.empty(301)
fig, ax = plt.subplots()
for bestof in [1,3]:
	for x in range(301):
		y_axis[x] = expected_profit_Day1(0.40+x/1000, bestof)
	ax.plot(x_axis, y_axis, label='best-of-'+str(bestof))
	ax.set(xlabel='Game win rate', ylabel='Expected profit',
		   title='Arena Open: Expected profit as a function of game win rate')
	ax.set_xticklabels(['{:.0%}'.format(x) for x in ax.get_xticks()])
	ax.set_yticklabels(['${:.0f}'.format(y) for y in ax.get_yticks()])
	ax.grid(True)
	ax.axhline(linewidth=2, color='k')
	plt.legend()
	plt.xlim(.4,.55)
	plt.ylim(-20,20)
fig.savefig("Expected_profit_zoomed.png")

#Also determine the break-even and intersection points
bo1 = np.empty(3001)
bo3 = np.empty(3001)
for x in range(1,3001):
	bo1[x] = expected_profit_Day1(0.40+x/10000, 1)
	if bo1[x] >= 0 and bo1[x - 1] < 0:
		print(f'Break even in best-of-1 at: {(0.40+x/10000)*100: .1f}% win rate.') 
	bo3[x] = expected_profit_Day1(0.40+x/10000, 3)
	if bo3[x] >= 0 and bo3[x - 1] < 0:
		print(f'Break even in best-of-3 at: {(0.40+x/10000)*100: .1f}% win rate.') 
	if bo1[x] >= bo3[x] and bo1[x - 1] < bo3[x - 1]:
		print(f'Intersection at: {(0.40+x/10000)*100: .1f}% win rate.') 

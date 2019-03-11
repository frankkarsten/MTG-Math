import random

deck = {
	'Key card': 4,
	'Other': 56
}

def log(s):
    if DEBUG:
        print(s)

DEBUG = False 

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


ProbDist_KeyCard_in7 = []
#ProbDist_KeyCard_in7[i] will give the probability of drawing i KeyCards in 7 cards from the 60-card deck
for KeyCard in [0, 1, 2, 3, 4]:
	needed = {}
	needed['Key card'] = KeyCard
	needed['Other'] = 7 - KeyCard
	ProbDist_KeyCard_in7.append(multivariate_hypgeom(deck, needed))

for max_mulligans in range(4):
	#ProbDist_KeyCard_aftermulls[i] will give the probability of keeping a hand with i KeyCards after resolving mulligans to at most max_mulligans
	ProbDist_KeyCard_aftermulls = []
	ProbDist_KeyCard_aftermulls.append(ProbDist_KeyCard_in7[0] ** (max_mulligans + 1))
	log(f'When willing to mull down to {7 - max_mulligans}, Prob of keeping 0 key cards is {100 * ProbDist_KeyCard_aftermulls[0]:.2f}%.')
	for nrKeyCard in [1, 2, 3, 4]:
		ProbDist_KeyCard_aftermulls.append((1 - ProbDist_KeyCard_aftermulls[0]) * ProbDist_KeyCard_in7[nrKeyCard] / (1 - ProbDist_KeyCard_in7[0]))
		log(f'When willing to mull down to {7 - max_mulligans}, Prob of keeping {nrKeyCard} key cards is {100 * ProbDist_KeyCard_aftermulls[nrKeyCard]:.2f}%.')
	#Note that the distribution is the same for 4 Nature's Claim and for 4 Leylines as your key cards
	totalprob = 0
	for nrClaim in range (4 + 1):
		for nrLeyline in range(4 + 1):
			if (nrLeyline > nrClaim):
				log(f'Prob of {nrClaim} Claims and {nrKeyCard} KeyCards is is {100 * ProbDist_KeyCard_aftermulls[nrClaim] * ProbDist_KeyCard_aftermulls[nrLeyline]:.2f}%.')
				totalprob += ProbDist_KeyCard_aftermulls[nrClaim] * ProbDist_KeyCard_aftermulls[nrLeyline]
	print(f'Suppose that both players are willing to mull down to {7 - max_mulligans} cards.')
	print(f'Then P[Opp draws more Leylines than we draw Claims] = {100 * totalprob:.2f}%.')

Mardu = {
	'Leyline': 4,
	'Other': 56
}

Dredge = {
	'Claim': 4,
	'Other': 56
}

def simulate_Leyline_vs_Claim(max_mulls):
	"""	
	Returns - a number that approximates via simulation the probability of drawing more Leylines than Claims
	Assumes that players are willing to mulligan down to max_mulls
	"""
	num_iterations = 10 ** 5
	count_Mardu_wins = 0
	for _ in range(num_iterations):
		
		number_mulls = 0
		while True:
			decklist_Dredge = []
			for card in Dredge.keys():
				decklist_Dredge += [card] * Dredge[card]
			random.shuffle(decklist_Dredge)
			
			hand = {
				'Claim': 0,
				'Other': 0
			}
			
			for _ in range(7):
				hand[decklist_Dredge.pop(0)] += 1
			if (hand['Claim']>0 or number_mulls == max_mulls):
				Claims = hand['Claim']
				break
			else:
				number_mulls += 1
		
		number_mulls = 0
		while True:
			decklist_Mardu = []
			for card in Mardu.keys():
				decklist_Mardu += [card] * Mardu[card]
			random.shuffle(decklist_Mardu)
			
			hand = {
				'Leyline': 0,
				'Other': 0
			}
			
			for _ in range(7):
				hand[decklist_Mardu.pop(0)] += 1
			if (hand['Leyline']>0 or number_mulls == max_mulls):
				Leylines = hand['Leyline']
				break
			else:
				number_mulls += 1
		
		if Leylines > Claims:
			count_Mardu_wins += 1
	return count_Mardu_wins/num_iterations

print ("Now we use a simulation to check.")

for max_mulls in range(4):
	print ( "If both players are willing to mull down to "+str(7 - max_mulls)+": "+str(simulate_Leyline_vs_Claim(max_mulls)) )

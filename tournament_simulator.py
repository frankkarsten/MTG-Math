from matplotlib import pyplot as plt
import numpy as np

#The model needs 4 inputs: decks, matchups, metagame, and nr_rounds
decks = ["Rock", "Paper", "Scissors"]

#Matchups are specified in the form deck1, deck2: P(deck 1 wins)
matchups = {
	("Rock", "Paper"): 0,
	("Paper", "Scissors"): 0,
	("Scissors", "Rock"): 0
}

metagame = {
	"Rock": 0.50,
	"Paper": 0.25,
	"Scissors": 0.25
}

nr_rounds = 16

def complete_matchups(matchups):
	"""
	For a given matchup dictionary, this adds converse matchups 
	(given P[deck 1 beats deck 2], derive P[deck 2 vs deck 1])
	and it adds mirror matches. 
	"""
	
	for (deck1, deck2), winrate in matchups.copy().items():
		matchups[(deck2, deck1)] = 1 - winrate

	for deck in decks:
		matchups[(deck, deck)] = 0.5
	
	if sum(metagame.values()) != 1:
		print("Warning! This metagame does not add up to 100%!")

def winrate(meta, deck):
	"""
	We're playing deck and our opponent is drawn from dictionary {meta}.
	For all opp_deck, the value meta[opp_deck] provides the fraction of players
	in the tournament who are at our current record and running opp_deck.
	These values typically won't add up to 1 because not everyone has our record.
	This function returns our expected probability to win the match.
	"""
	fraction_at_record = sum(meta.values())
	answer = 0
	for opp_deck in decks:
		answer += matchups[(deck, opp_deck)] * meta[opp_deck] / fraction_at_record
	return answer

def run_tournament(decks, matchups, metagame, nr_rounds):
	"""
	Returns a dictionary called meta. For all integer rnd <= nr_rounds and W <= rnd,
	meta[(rnd, W)] stores the metagame in the event at "W" wins after round "rnd"
	Specifically, meta[(rnd, W)] is a dictionary such that meta[(rnd, W)][deck]
	is the fraction of players on deck in the event at "W" wins after round "rnd"
	The undefeated metagame is then given by meta[(rnd, rnd)].
	"""
	#Initalize the starting meta
	meta = {
		(0,0): metagame.copy()
	}
	for rnd in range(1, nr_rounds + 1):
		#Ex.: If nr_rounds = 3 then we play rounds {1, 2, 3}
		for W in range(rnd + 1):
			#Ex.: If we play rnd 2 then we can reach {0, 1, 2} wins
			#We can reach 0 wins by losing at 0 wins
			#We can reach 1 win by either winning at 0 wins or losing at 1 win
			#We can reach 2 wins by winning at 1 win
			meta[(rnd, W)] = {}
			for deck in decks:
				#Initialize at 0
				meta[(rnd, W)][deck] = 0
				if W - 1 >= 0:
				#Winning from W - 1 wins
					wr = winrate(meta[(rnd - 1, W - 1)], deck)
					meta[(rnd, W)][deck] += meta[(rnd - 1, W - 1)][deck] * wr
				if W < rnd:
				#Losing from W wins
				#Note that it's possible that W - 1 >= 0 AND W < rnd, e.g., hitting a 1-1 record
					wr = winrate(meta[(rnd - 1, W)], deck)
					meta[(rnd, W)][deck] += meta[(rnd - 1, W)][deck] * (1 - wr)
	return meta

def plot_meta(filename, max_y = 1):
	"""
	After the tournament has been run and the entire meta distribution is obtained, this plot
	shows the probability of going undefeated (reaching nr_rounds wins and 0 losses) for all decks.
	"""
	x_axis = range(1, nr_rounds + 1)
	fig, ax = plt.subplots()
	for deck in decks:
		y_axis = [meta[(rnd, rnd)][deck] / sum(meta[(rnd, rnd)].values()) for rnd in x_axis]
		ax.plot(x_axis, y_axis, label=deck, marker='o')
	ax.set(xlabel='At the end of round number', ylabel='Percent of undefeated metagame',
			   title='Undefeated metagame during the tournament')
	plt.xticks(x_axis)
	plt.yticks(np.arange(11)/(10 / max_y))
	#If max_y = 0.5, this gives ticks at [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])
	ax.set_xticklabels(['{}'.format(x) for x in ax.get_xticks()])
	ax.set_yticklabels(['{:.0%}'.format(y) for y in ax.get_yticks()])
	ax.grid(True)
	plt.legend()
	plt.ylim(0, max_y)
	fig.savefig(filename)

def success_prob(deck):	
	"""
	After the tournament has been run to obtain the entire meta distribution
	at all records, this returns the probability of going undefeated, i.e.,
	nr_rounds wins and 0 losses for an individual player when playing deck.
	"""
	success_prob = 1
	for rnd in range(1, nr_rounds + 1):
		success_prob *= winrate(meta[(rnd - 1, rnd - 1)], deck)
	return success_prob

#Run the numbers for 16-round Rock-Paper-Scissors
complete_matchups(matchups)
meta = run_tournament(decks, matchups, metagame, nr_rounds)
for deck in decks:
	print(f"Success prob with {deck}: {success_prob(deck) * 100: .4f}%.")
print("BTW, what's the 15-1 metagame like?")
for deck in decks:
	print(f"{deck:10} : {meta[(16,15)][deck]:.4%}")
plot_meta("Metagame_RPS.png")

#Define the values for the Standard example

decks = ["Gruul Adventures", "Dimir Rogues", "Mono-Green Food", "Temur Adventures", "Dimir Control", "Selesnya Adventures", "Other"]

matchups = {
	("Gruul Adventures", "Dimir Rogues"): .55,
	("Gruul Adventures", "Mono-Green Food"): .43,
	("Gruul Adventures", "Temur Adventures"): .58,
	("Gruul Adventures", "Other"): .56,
	("Dimir Rogues", "Mono-Green Food"): .48,
	("Dimir Rogues", "Temur Adventures"): .66,
	("Dimir Rogues", "Other"): .49,
	("Mono-Green Food", "Temur Adventures"): .45,
	("Mono-Green Food", "Other"): .55,
	("Temur Adventures", "Other"): .56,
	("Dimir Control", "Gruul Adventures"): .44,
	("Dimir Control", "Dimir Rogues"): .52,
	("Dimir Control", "Mono-Green Food"): .44,
	("Dimir Control", "Temur Adventures"): .43,
	("Dimir Control", "Other"): .58,
	("Selesnya Adventures", "Gruul Adventures"): .57,
	("Selesnya Adventures", "Dimir Rogues"): .35,
	("Selesnya Adventures", "Mono-Green Food"): .48,
	("Selesnya Adventures", "Temur Adventures"): .71,
	("Selesnya Adventures", "Dimir Control"): .56,
	("Selesnya Adventures", "Other"): .58
}

metagame = {
	"Gruul Adventures": 0.21,
	"Dimir Rogues": 0.12,
	"Mono-Green Food": 0.15,
	"Temur Adventures": 0.13,
	"Dimir Control": .10,
	"Selesnya Adventures": .01,
	"Other": 1 - 0.21 - 0.12 - 0.15 - 0.13 - 0.10 - 0.01
}

nr_rounds = 8

#Run the numbers for the 8-round Standard example
complete_matchups(matchups)
meta = run_tournament(decks, matchups, metagame, nr_rounds)
for deck in decks:
	print(f"Success prob with {deck}: {success_prob(deck) * 100: .2f}%.")
print("BTW, what's the 7-1 metagame like?")
for deck in decks:
	print(f"{deck:20} : {meta[(8,7)][deck]:.4%}")
plot_meta("Metagame_Standard.png", max_y = 0.5)

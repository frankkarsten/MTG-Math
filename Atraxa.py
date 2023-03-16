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

def determine_hit_prob(number_hits):
    """    
    Parameters:
        number_hits - Should be between 0 or 10. Represents the number of cards put into your hand with Atraxa.
    Returns - a number that represents the probability of hitting <number_hits> different card types in your top 10.
    """
    hit_prob = 0
    
    #Eight nested for loops for eight card types isn't the cleanest solution, but it works
    for artifact in range(min(11, deck['artifact']) +1):
        for battle in range(min(11, deck['battle']) +1):
            for creature in range(min(11, deck['creature']) +1):
                for enchantment in range(min(11, deck['enchantment']) +1):
                    for instant in range(min(11, deck['instant']) +1):
                        for land in range(min(11, deck['land']) +1):
                            for planeswalker in range(min(11, deck['planeswalker']) +1):
                                for sorcery in range(min(11, deck['sorcery']) +1):
                                    total_cards = artifact + battle + creature + enchantment + instant + land + planeswalker + sorcery
                                    hits =  min(artifact, 1) + min(battle,1) + min(creature, 1) + min(enchantment, 1) + min(instant, 1) + min(land, 1) + min(planeswalker, 1) + min(sorcery, 1)
                                    if (total_cards == 10 and hits == number_hits):
                                        needed = {}
                                        needed['artifact'] = artifact
                                        needed['battle'] = battle
                                        needed['creature'] = creature
                                        needed['enchantment'] = enchantment
                                        needed['instant'] = instant
                                        needed['land'] = land
                                        needed['planeswalker'] = planeswalker
                                        needed['sorcery'] = sorcery
                                        hit_prob += multivariate_hypgeom(deck, needed)
    return hit_prob

#List a deck as a dictionary of types, minus one Atraxa, which is on the stack
#So the sum of values for deck should normally add up to 59

deck = {
    'artifact':4,
    'battle': 0,
    'creature': 11,
    'enchantment': 4,
    'instant': 8,
    'land': 14,
    'planeswalker': 0,
    'sorcery': 18
}

#Now let's print the relevant numbers for this deck

number_words = {
    1: "One card",
    2: "Two cards",
    3: "Three cards",
    4: "Four cards",
    5: "Five cards",
    6: "Six cards",
    7: "Seven cards",
    8: "Eight cards"
}

print("The distribution of the number of cards put into your hand by Atraxa is as follows:")
expected_hits = 0
for number_hits in range(1, 8):
    hit_prob = determine_hit_prob(number_hits)
    print(f'{number_words[number_hits]}: {hit_prob * 100:.1f}%')
    expected_hits += number_hits * hit_prob
print(f'Expected value: {expected_hits:.2f} cards')
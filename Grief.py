#NEED TO ADJUST
deck = {
    'Land': 20,
    'Grief': 4,
    'Fury': 4,
    'Undying': 6,
    'BR': 3,
    'Black': 12,
    'Red': 11
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

scammed_Grief_prob_play = 0
scammed_Grief_prob_draw = 0
scammed_Grief_or_Fury_prob_play = 0
scammed_Grief_or_Fury_prob_draw = 0
Fury_prob = 0

for Land in range(min(deck['Land'], 7) +1):
    for Grief in range(min(deck['Grief'], 7) +1):
         for Fury in range(min(deck['Fury'], 7) +1):
                for Undying in range(min(deck['Undying'], 7) +1):
                    for BR in range(min(deck['BR'], 7) +1):
                            for Black in range(min(deck['Black'], 7) +1):
                                for Red in range(min(deck['Red'], 7) +1):
                                    cards_drawn = Land + Grief + Fury + Undying + BR + Black + Red
                                    if (cards_drawn == 7):

                                        black_pitch_spells = BR + Black + max((Grief - 1), 0) + max((Undying - 1), 0)
                                        red_pitch_spells = BR + Red + max((Fury - 1), 0)
    
                                        needed = {}
                                        needed['Land'] = Land
                                        needed['Grief'] = Grief
                                        needed['Fury'] = Fury
                                        needed['Undying'] = Undying
                                        needed['BR'] = BR
                                        needed['Black'] = Black
                                        needed['Red'] = Red
                                        hand_prob = multivariate_hypgeom(deck, needed)
                                
                                        scammed_Grief = (Land >= 1 and Grief >= 1 and Undying >= 1 and black_pitch_spells >= 1)
                                        scammed_Fury = (Land >= 1 and Fury >= 1 and Undying >= 1 and red_pitch_spells >= 1)

                                        if scammed_Grief:
                                            scammed_Grief_prob_play += hand_prob
                                            scammed_Grief_prob_draw += hand_prob
                                            
                                        if (Land >= 1 and Grief == 0 and Undying >= 1 and black_pitch_spells >= 1):
                                            prob_to_topdeck_Grief = deck['Grief'] / 53
                                            scammed_Grief_prob_draw += hand_prob * prob_to_topdeck_Grief
                                            
                                        if (Land >= 1 and Grief >= 1 and Undying == 0 and black_pitch_spells >= 1):
                                            prob_to_topdeck_Undying = deck['Undying'] / 53
                                            scammed_Grief_prob_draw += hand_prob * prob_to_topdeck_Undying
                                            
                                        if (Land >= 1 and Grief >= 1 and Undying >= 1 and black_pitch_spells == 0):
                                            prob_to_topdeck_Pitch = (deck['Grief'] - Grief + deck['Undying'] - Undying + BR + Black) / 53
                                            scammed_Grief_prob_draw += hand_prob * prob_to_topdeck_Pitch

                                        if scammed_Grief or scammed_Fury:
                                            scammed_Grief_or_Fury_prob_play += hand_prob
                                            scammed_Grief_or_Fury_prob_draw += hand_prob
                                        else:
                                            #Is Grief an out?
                                            if (Land >= 1 and Grief == 0 and Undying >= 1 and black_pitch_spells >= 1) or (Land >= 1 and Grief >= 1 and Undying >= 1 and black_pitch_spells == 0):
                                                prob_to_topdeck_Grief = deck['Grief'] / 53                                
                                                scammed_Grief_or_Fury_prob_draw += hand_prob * prob_to_topdeck_Grief
                                            #Is Fury an out?
                                            if (Land >= 1 and Fury == 0 and Undying >= 1 and red_pitch_spells >= 1) or (Land >= 1 and Fury >= 1 and Undying >= 1 and red_pitch_spells == 0):
                                                prob_to_topdeck_Fury = deck['Fury'] / 53                                
                                                scammed_Grief_or_Fury_prob_draw += hand_prob * prob_to_topdeck_Fury
                                            #Is Undying an out?
                                            need_Undying_to_cast = (Land >= 1 and Undying == 0 and ((Grief >= 1 and black_pitch_spells >= 1) or (Fury >= 1 and red_pitch_spells >= 1)))
                                            need_Undying_to_pitch = (Land >= 1 and Undying == 1 and Grief == 1 and black_pitch_spells == 0)                                                    
                                            if (need_Undying_to_cast or need_Undying_to_pitch):
                                                prob_to_topdeck_Undying = deck['Undying'] / 53                                
                                                scammed_Grief_or_Fury_prob_draw += hand_prob * prob_to_topdeck_Undying
                                            #Is BR an out?
                                            Elemental_but_no_pitch_possible = (Grief == 1 and black_pitch_spells == 0) or (Fury == 1 and red_pitch_spells == 0)
                                            if (Land >= 1 and Elemental_but_no_pitch_possible and Undying >= 1):
                                                prob_to_topdeck_BR = deck['BR'] / 53                                
                                                scammed_Grief_or_Fury_prob_draw += hand_prob * prob_to_topdeck_BR
                                            #Is Black an out?
                                            if (Land >= 1 and Grief == 1 and Undying == 1 and black_pitch_spells == 0):
                                                prob_to_topdeck_Black = deck['Black'] / 53                                
                                                scammed_Grief_or_Fury_prob_draw += hand_prob * prob_to_topdeck_Black
                                            #Is Red an out?
                                            if (Land >= 1 and Fury == 1 and Undying == 1 and red_pitch_spells == 0):
                                                prob_to_topdeck_Red = deck['Red'] / 53                                
                                                scammed_Grief_or_Fury_prob_draw += hand_prob * prob_to_topdeck_Red

print(f'Probability of turn one scammed Grief on the play: {scammed_Grief_prob_play * 100:.1f}%.')
no_scammed_Grief_prob_play = 1 - scammed_Grief_prob_play
print(f'With aggressive mulligans to 6, this probability is: {(1 - no_scammed_Grief_prob_play *  no_scammed_Grief_prob_play) * 100:.1f}%.')
print(f'With aggressive mulligans to 5, this probability is: {(1 - no_scammed_Grief_prob_play *  no_scammed_Grief_prob_play * no_scammed_Grief_prob_play ) * 100:.1f}%.')
print(f'With aggressive mulligans to 4, this probability is: {(1 - no_scammed_Grief_prob_play *  no_scammed_Grief_prob_play * no_scammed_Grief_prob_play * no_scammed_Grief_prob_play ) * 100:.1f}%.')
print(f'Probability of turn one scammed Grief on the draw: {scammed_Grief_prob_draw * 100:.1f}%.')
print('-'*30)

print(f'Probability of turn one scammed Grief or Fury on the play: {scammed_Grief_or_Fury_prob_play * 100:.1f}%.')
no_scammed_Grief_or_Fury_prob_play = 1 - scammed_Grief_or_Fury_prob_play
print(f'With aggressive mulligans to 6, this probability is: {(1 - no_scammed_Grief_or_Fury_prob_play *  no_scammed_Grief_or_Fury_prob_play) * 100:.1f}%.')
print(f'With aggressive mulligans to 5, this probability is: {(1 - no_scammed_Grief_or_Fury_prob_play *  no_scammed_Grief_or_Fury_prob_play * no_scammed_Grief_or_Fury_prob_play ) * 100:.1f}%.')
print(f'With aggressive mulligans to 4, this probability is: {(1 - no_scammed_Grief_or_Fury_prob_play *  no_scammed_Grief_or_Fury_prob_play * no_scammed_Grief_or_Fury_prob_play * no_scammed_Grief_or_Fury_prob_play ) * 100:.1f}%.')
print(f'Probability of turn one scammed Grief or Fury on the draw: {scammed_Grief_or_Fury_prob_draw * 100:.1f}%.')
print('-'*30)


#I will assume that we want to cast a Force without paying its mana cost on our opponent’s second turn.
#There are no mulligans. So then we have seen 8 cards.
#Given this, I want to look at all possible 8-card sequences of Forces (F), ...
#...other blue cards to pitch (P), and non-blue cards (C), such as FPCCCFPPC, ...
#...assign a probability to each, sum up the probabilities for all combinations ...
#...with at least one F and either at least one P or another F, and then...
# divide that by the sum of probabilities for all combinations with at least one F.
# This is just a garden variety conditional cumulative multivariate hypergeometric.

handsize = 8

print("=====")
print('For each deck, we give two probabilities. First is holding a pitcher or another Force, conditional on holding Force. Second is having a choice between what blue card to pitch.')

#Consider decks with 4 Forces
for Pitcher_deck in range(23):
    #Consider decks with 0-22 pitchers (cards of the same color that you can 'pitch' to cast a Force)
    #Total number of cards in the deck is 60
    deck = {
        'Force': 4,
        'Pitcher': Pitcher_deck,
        'Other': 60-4-Pitcher_deck
    }
    #Combo_Success_prob will sum up the probabilities for all combinations with >=1 Force and either >=2 Force or >=1 pitcher
    Combo_Success_prob = 0
    #Choice_prob will sum up the probabilities for all combinations with >=1 Force and either >=2 pitcher or (>=1 pitcher and >=2 Force)
    Choice_prob = 0
    #Force_prob will sum up the probabilities for all combinations with >=1 Force
    Force_prob = 0
    for Force in [1, 2, 3, 4]: 
        #Hence, the presence of at least one Force is guaranteed
        for Pitcher in range(Pitcher_deck +1):
            #So if, e.g., we have Pitcher_deck = 4 Pitchers in our deck, then this range is the set [0, 1, 2, 3, 4]
            if Force + Pitcher <= handsize:
                #We can't consider combinations with, say, 9 Pitchers as those would exceed the number of cards drawn
                needed = {}
                needed['Force'] = Force
                needed['Pitcher'] = Pitcher
                needed['Other'] = handsize - Force - Pitcher
                probability = multivariate_hypgeom(deck, needed)
                if Pitcher >= 1 or Force >= 2:
                    #We have either a Pitcher or another Force to pay for the alternative cost
                    Combo_Success_prob += probability
                if Pitcher >= 2 or (Force >= 2 and Pitcher >= 1):
                    #We have a choice what to exile to pay for the alternative cost
                    Choice_prob += probability
                #In any case, this was a combination of cards with at least one Force
                Force_prob += probability

    print(f'Deck with 4 Forces and {Pitcher_deck} pitchers; probability : {(Combo_Success_prob/Force_prob)* 100:.1f}, {(Choice_prob/Force_prob)* 100:.1f}%.')

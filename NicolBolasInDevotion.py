import random
from collections import Counter

num_simulations = 10000000

def put_cards_on_bottom(hand, spells_remaining_to_bottom):
    """    
    Parameters:
        hand - A dictionary, with the same cardnames as in decklist, with number drawn
        spells_remaining_to_bottom - The number of spells to bottom after a mulligan (must be <= number of spells in hand)
    Returns - nothing, it just adjusts the opening hand value
    """
    #First bottom other spells
    Bottomable_other_spell = min(hand['Other spell'], spells_remaining_to_bottom)
    hand['Other spell'] -= Bottomable_other_spell
    spells_remaining_to_bottom -= Bottomable_other_spell

    #Then bottom excess Nicol Bolas beyond the first
    if hand['Nicol Bolas'] >= 2:
        Bottomable_nicol = min(hand['Nicol Bolas'] - 1, spells_remaining_to_bottom)
        hand['Nicol Bolas'] -= Bottomable_nicol
        spells_remaining_to_bottom -= Bottomable_nicol

    #Then bottom excess Storm the Festivals beyond the first
    if hand['Storm the Festival'] >= 2:
        Bottomable_storm = min(hand['Storm the Festival'] - 1, spells_remaining_to_bottom)
        hand['Storm the Festival'] -= Bottomable_storm
        spells_remaining_to_bottom -= Bottomable_storm

    #Then bottom excess lands beyond the fifth
    if hand['Forest or Elf'] >= 6:
        Bottomable_forest = min(hand['Forest or Elf'] - 5, spells_remaining_to_bottom)
        hand['Forest or Elf'] -= Bottomable_forest
        spells_remaining_to_bottom -= Bottomable_forest

    #Then bottom excess Oath of Nissa beyond the first
    if hand['Oath of Nissa'] >= 2:
        Bottomable_oath = min(hand['Oath of Nissa'] - 1, spells_remaining_to_bottom)
        hand['Oath of Nissa'] -= Bottomable_oath
        spells_remaining_to_bottom -= Bottomable_oath

    #In the unlikely situation that we still have to bottom more, bottom lands
    Bottomable_forest = min(hand['Forest or Elf'], spells_remaining_to_bottom)
    hand['Forest or Elf'] -= Bottomable_forest
    spells_remaining_to_bottom -= Bottomable_forest


def run_one_sim(decklist):    
    keephand = False 
    
    for handsize in [7, 6, 5, 4]:
        #We may mull 7, 6, or 5 cards and keep every 4-card hand
        #Once we actually keep, the variable keephand will be set to True
        if not keephand:
            
            #Construct library as a list
            library = []
            for card in decklist.keys():
                library += [card] * decklist[card]
            random.shuffle(library)

            #Construct a random opening hand
            hand = {
                'Forest or Elf': 0,
                'Storm the Festival': 0,
                'Nicol Bolas': 0,
                'Oath of Nissa': 0,
                'Other spell': 0
            }
            
            for _ in range(7):
                card_drawn = library.pop(0)
                hand[card_drawn] += 1

            if handsize == 7:
                #Do we keep?
                if (hand['Forest or Elf'] >= 2 and hand['Forest or Elf'] <= 5):
                    keephand = True

            if handsize == 6:
                #We have to bottom.
                put_cards_on_bottom(hand, 1)
                #Do we keep?
                if (hand['Forest or Elf'] >= 2 and hand['Forest or Elf'] <= 4):
                    keephand = True

            if handsize == 5:
                #We have to bottom.
                put_cards_on_bottom(hand, 2)
                #Do we keep?
                if (hand['Forest or Elf'] >= 2 and hand['Forest or Elf'] <= 4):
                    keephand = True

            if handsize == 4:
                #We have to bottom.
                put_cards_on_bottom(hand, 3)
                #Do we keep?
                keephand = True
    
    oath_on_battlefield = False
    lands_on_battlefield = 0
    bolas_on_battlefield = False
    six_mana_by_turn_5 = False
                
    for turn in [1, 2, 3, 4, 5, 6]:
        #Draw step
        draw_a_card = True if (turn == 1 and random.random() < 0.5) or (turn > 1) else False
        if (draw_a_card):
            card_drawn = library.pop(0)
            hand[card_drawn] += 1
            
        #Play a land if possible
        land_played = False
        if hand['Forest or Elf'] > 0:
            lands_on_battlefield += 1
            hand['Forest or Elf'] -= 1
            land_played = True
        mana_available = lands_on_battlefield

        #On turn 4, 5 and 6, we assume to always have an extra mana via, say, Wolfwillow Haven or Nykthos
        if turn in [4, 5, 6]:
            mana_available += 1

        #Play Nicol Bolas if possible
        if mana_available >= 5 and hand['Nicol Bolas'] > 0 and oath_on_battlefield:
            bolas_on_battlefield = True
            hand['Nicol Bolas'] -= 1
            mana_available -= 5

        #Play Oath of Nissa if possible, then dig for Bolas or land
        if mana_available >= 1 and hand['Oath of Nissa'] > 0:
            hand['Oath of Nissa'] -= 1
            oath_on_battlefield = True
            top_three_cards = []
            for _ in range(3):
                top_three_cards.append(library.pop(0))
            #Take Nicol Bolas if possible
            if "Nicol Bolas" in top_three_cards:
                hand["Nicol Bolas"] += 1
            elif "Forest or Elf" in top_three_cards:
                hand['Forest or Elf'] += 1 
            #Play a land if we hit one and didn't have a land for the turn before
            if not land_played and hand['Forest or Elf'] > 0:
                lands_on_battlefield += 1
                hand['Forest or Elf'] -= 1
                land_played = True
                mana_available += 1
            #Cast Nicol Bolas if possible
            if mana_available >= 5 and hand['Nicol Bolas'] > 0 and oath_on_battlefield:
                bolas_on_battlefield = True
                hand['Nicol Bolas'] -= 1
                mana_available -= 5

        #Play Storm the Festival if possible
        if mana_available >= 6 and hand['Storm the Festival'] > 0:
            hand['Storm the Festival'] -= 1
            top_five_cards = []
            for _ in range(5):
                top_five_cards.append(library.pop(0))
            #Take Nicol Bolas if possible
            if "Nicol Bolas" in top_five_cards:
                bolas_on_battlefield = True
            elif "Oath of Nissa" in top_five_cards:
                #Normally it'll just be one, but we might grab two Oaths
                number_oaths = min(Counter(top_five_cards)['Oath of Nissa'], 2)
                for _ in range(number_oaths):
                    #Yeah, yeah, literally copy-pasting code from earlier is a bad practice. I'm lazy today
                    oath_on_battlefield = True
                    top_three_cards = []
                    for _ in range(3):
                        top_three_cards.append(library.pop(0))
                    #Take Nicol Bolas if possible
                    if "Nicol Bolas" in top_three_cards:
                        hand["Nicol Bolas"] += 1
                    elif "Forest or Elf" in top_three_cards:
                        hand['Forest or Elf'] += 1 
                    #Play a land if we hit one and didn't have a land for the turn before
                    if not land_played and hand['Forest or Elf'] > 0:
                        lands_on_battlefield += 1
                        hand['Forest or Elf'] -= 1
                        land_played = True
                        mana_available += 1
                    #Cast Nicol Bolas if possible
                    if mana_available >= 5 and hand['Nicol Bolas'] > 0 and oath_on_battlefield:
                        bolas_on_battlefield = True
                        hand['Nicol Bolas'] -= 1
                        mana_available -= 5
            #While theoretically we could grab some lands, this is unlikely to happen in practice
            #Realistically you'd take some expensive permanent, so I'll ignore the land option for now
            
        #On turn 5, check if we hit all of our land drops so far
        if turn == 5 and lands_on_battlefield == 5:
            six_mana_by_turn_5 = True

    if six_mana_by_turn_5 and bolas_on_battlefield:
        Outcome = 'BOLAS IN PLAY'
    elif six_mana_by_turn_5 and (not bolas_on_battlefield) and hand["Nicol Bolas"] > 0 and oath_on_battlefield:
        #Should only happen if we awkwardly hit Bolas with Oath of Nissa grabbed off of a turn-6 Storm the Festival
        #We'll count this as a success as well
        Outcome = 'BOLAS IN PLAY'
    elif six_mana_by_turn_5 and (not bolas_on_battlefield) and hand["Nicol Bolas"] > 0 and (not oath_on_battlefield):
        Outcome = 'UNCASTABLE BOLAS'
    elif six_mana_by_turn_5 and (not bolas_on_battlefield) and hand["Nicol Bolas"] == 0:
        Outcome = 'IGNORE'
    elif not six_mana_by_turn_5:
        Outcome = 'IGNORE'
    else:
        print("This is literally impossible. The simulation is drunk.")
    return Outcome

decklist = {
    'Forest or Elf': 33,
    'Storm the Festival': 4,
    'Nicol Bolas': 2,
    'Oath of Nissa': 4,
    'Other spell': 17
}


print("-----------------")
print(decklist)    
print('')    

total_relevant_games = 0.0
total_favorable_games_bolas_on_battlefield = 0.0
total_unfavorable_games_stuck_in_hand = 0.0
    
for _ in range(num_simulations):
    Outcome = run_one_sim(decklist)
    if (Outcome == "BOLAS IN PLAY"):
        total_relevant_games += 1
        total_favorable_games_bolas_on_battlefield +=1
    if (Outcome == "UNCASTABLE BOLAS"):
        total_relevant_games += 1
        total_unfavorable_games_stuck_in_hand += 1
    if (Outcome == "IGNORE"):
        pass

print("Conditional probability to control Nicol Bolas by turn 6:" +str(round(total_favorable_games_bolas_on_battlefield / total_relevant_games * 100.0 ,1))+"%.")
print("Conditional probability to be stuck with an uncastable Nicol Bolas in hand on turn 6:" +str(round(total_unfavorable_games_stuck_in_hand / total_relevant_games * 100.0 ,1))+"%.")

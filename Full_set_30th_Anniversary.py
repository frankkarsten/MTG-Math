import random

#Original Beta has 75 nonland commons
#Two fewer commons because no Weakness or Earthbind
#One more common because of Sol Ring, treated as separate from its uncommon version
#Rares are split between 103 non-duals and 10 duals
nr_commons = 74
nr_uncommons = 95
nr_rares = 103
nr_duals = 10

#Assumption for simplicity: With 3 basics/pack, you'll easily have all 5 basics in no time--they are disregarded
#Assumption for simplicity: Tokens don't count towards set completion--they are disregarded
#Assumption for collectors: You just want at least one of each card, regardless of whether it's retro or normal frame

nr_simulations = 50000
outcomes = []

for _ in range(nr_simulations):

	#We have a dictionary with 'Common 0', 'Common 1', etc. as keys and the number of copies we've opened thus far as values
    cards = {}
    for i in range(nr_commons):
        cards['Common ' + str(i)] = 0
    for i in range(nr_uncommons):
        cards['Uncommon ' + str(i)] = 0
    for i in range(nr_rares):
        cards['Rare ' + str(i)] = 0
    for i in range(nr_rares, nr_rares + nr_duals):
        cards['Dual ' + str(i)] = 0

    nr_packs_opened = 0
    set_complete = False
		
    while not set_complete:
        nr_packs_opened += 1

        #Get a random rare
        #In my modeling, we have 'Rare 0', 'Rare 1', ..., 'Rare 101', followed by 'Dual 102', 'Dual 103', ... 'Dual 111'
        #But dual lands appear twice as frequently, so we'' treat 112-121 as extra duals and draw a uniformly random number from {0, 1, ..., 121}
        #This number is stored in rare_nr
        rare_nr = random.randrange(nr_rares + 2 * nr_duals)
        if rare_nr < nr_rares:
            cards['Rare '+ str(rare_nr)] += 1
        elif rare_nr >= nr_rares and rare_nr < nr_rares + nr_duals:
            cards['Dual '+ str(rare_nr)] += 1
        elif rare_nr >= nr_rares + nr_duals:
            #If it's, say, 115, then this means the same card as 'Dual 105'.
            cards['Dual '+ str(rare_nr - nr_duals)] += 1

        #Get three random, different uncommons
        uncommon_nr_list = []
        for _ in range(3):
            while len(uncommon_nr_list) < 3:
                uncommon_nr = random.randrange(nr_uncommons)
                if uncommon_nr not in uncommon_nr_list:
                    uncommon_nr_list.append(uncommon_nr)
                    cards['Uncommon '+ str(uncommon_nr)] += 1

        #Get seven random, different commons
        common_nr_list = []
        for _ in range(7):
            while len(common_nr_list) < 7:
                common_nr = random.randrange(nr_commons)
                if common_nr not in common_nr_list:
                    common_nr_list.append(common_nr)
                    cards['Common '+ str(common_nr)] += 1

        #Open the retro frame slot
        if (random.random() <= 0.3):
            #Get a random rare, lazily copy-pasting code from earlier
            rare_nr = random.randrange(nr_rares + 2 * nr_duals)
            if rare_nr < nr_rares:
                cards['Rare '+ str(rare_nr)] += 1
            elif rare_nr >= nr_rares and rare_nr < nr_rares + nr_duals:
                cards['Dual '+ str(rare_nr)] += 1
            elif rare_nr >= nr_rares + nr_duals:
                cards['Dual '+ str(rare_nr - nr_duals)] += 1
        else:
            #Assumption for simplicity: If the retro card frame slot doesn't have a rare, then it has an uncommon
            #The actual distribution for non-rares was not listed in the announcement, so I'm being generous here
            #Impact of this assumption will be small because collecting the rares will almost always be the bottleneck
            uncommon_nr = random.randrange(nr_uncommons)
            cards['Uncommon '+ str(uncommon_nr)] += 1

        #Check if we're set complete
        if all([cards[i] > 0 for i in cards.keys()]):
            set_complete = True 

	#Add the number of packs opened in this iteration to the list of outcomes
    outcomes.append(nr_packs_opened)

print(sum(outcomes)/nr_simulations)
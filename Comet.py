import random
 
for nr_dice_per_roll in range(1, 8):
#We range the number of Pixie Guides from 0 (1 die per roll) to 8 (9 die per roll)
 
	#In damage_counts[i], for i in {0, 1, ..., 999999}, we'll store the number of simulations where we dealt i total damage via Comet's 4-5 ability
	#In squirrel_counts[i], for i in {0, 1, ..., 999999}, we'll store the number of simulations where we created i total squirrels via Comet's 1-2 ability
	#In activation_counts[i], for i in {0, 1, ..., 999999}, we'll store the number of simulations where we activated Comet i total times in one turn
	#In total_combined_damage_counts[i], for i in {0, 1, ..., 999999}, we'll store the number of sims where we dealt i damage via 4-5 pings or 1-2 squirrels
	#In damage_counts[1000000], we'll store the number of simulations where we dealt >=1000000 total damage via Comet's 4-5 ability.
	#Likewise for squirrel_counts[1000000] and activation_counts[1000000] and total_combined_damage_counts[1000000]
	damage_counts = {key: 0 for key in range(1000001)}
	squirrel_counts = {key: 0 for key in range(1000001)}
	activation_counts = {key: 0 for key in range(1000001)}
	total_combined_damage_counts = {key: 0 for key in range(1000001)}
	
	nr_simulations = 10000000
	for i in range(nr_simulations):
	#Ten million simulations per number of Pixie Guides
	 
		loyalty = 5
		damage = 0
		squirrels = 0
		total_combined_damage = 0
		total_activations = 0
		remaining_activations = 1
		
		#Keep rolling until Comet is dead, we no longer have activations, or we exceed one million damage
		#We could keep rolling after one million damage, but this'll take too long practically, especially if go infinite
		while loyalty > 0 and remaining_activations > 0 and damage < 1000000:
			highest_roll = max([random.randint(1, 6) for i in range(nr_dice_per_roll)])
			remaining_activations -= 1
			total_activations += 1
			if highest_roll == 6:
				remaining_activations += 2
				loyalty += 1
			elif highest_roll in [4, 5]:
				damage += loyalty
				loyalty -= 2
			elif highest_roll == 3:
				loyalty -= 1
			else:
				squirrels += 2
				loyalty += 2
			 
		#Store the results of this simulation 
		if damage >= 1000000:
			damage_counts[1000000] += 1
		else:
			damage_counts[damage] += 1

		if squirrels >= 1000000:
			squirrel_counts[1000000] += 1
		else:
			squirrel_counts[squirrels] += 1

		if squirrels + damage >= 1000000:
			total_combined_damage_counts[1000000] += 1
		else:
			total_combined_damage_counts[squirrels + damage] += 1
		
		if total_activations >= 1000000:
			activation_counts[1000000] += 1
		else:
			activation_counts[total_activations] += 1
	
	print(f'===RESULTS FOR {nr_dice_per_roll} DICE PER ROLL')
	print(f"Expected damage: {sum([i * damage_counts[i] / nr_simulations for i in range(1000001)]):.3f}")
	print(f"Expected squirrels: {sum([i * squirrel_counts[i] / nr_simulations for i in range(1000001)]):.3f}")
	print(f"Expected total combined damage: {sum([i * total_combined_damage_counts[i] / nr_simulations for i in range(1000001)]):.3f}")
	print(f"Expected activations: {sum([i * activation_counts[i] / nr_simulations for i in range(1000001)]):.3f}")

	cumulative_prob = 0	
	for total_combined_dmg in range(20):
		cumulative_prob += total_combined_damage_counts[total_combined_dmg] / nr_simulations
		print(f"P({total_combined_dmg} combined damage via pings and squirrels: {100* total_combined_damage_counts[total_combined_dmg] / nr_simulations: .3f}%")
	print(f"P(>={20} combined damage via pings and squirrels: {100*( 1 - cumulative_prob): .3f}%")
	
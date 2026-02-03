POPULATION_SIZE = 40
NUMBER_OF_GENERATIONS = 100
MUTATION_RATE = 0.05

from random import choice, random, sample, randrange
from src.Feature import Measurement, CATEGORY
from src.Simulation import Simulation

class Gene:
	def __init__(self, feature):
		self.category, self.subcategory, self.feature = feature
		self.weight = round(random() * choice([-1, 1]) * 0.5, 6)

	def enhance(self):
		# Increase Feature Weight
		self.weight = round(self.weight + random() * 0.1, 6)

	def degrade(self):
		# Decrease Feature Weight
		self.weight = round(self.weight - random() * 0.1, 6)

	def randomShift(self):
		self.weight = round(self.weight + random() * choice([-1, 1]) * 0.5, 6)

	def clone(self):
		# Make a Copy of Gene
		feature = self.category, self.subcategory, self.feature
		gene = Gene(feature)
		gene.weight = self.weight
		return gene

class Chromosome:
	def __init__(self, gene_set):
		self.genes = gene_set

	@property
	def subcategories(self):
		return [gene.subcategory for gene in self.genes]

class Cell:
	def __init__(self, alpha, beta):
		self.chromosomes = [alpha, beta]

	def __lt__(self, cell):
		# Just to make things work when sorting in a list paired with a number
		return choice([True, False])

	def estimate(self, grid):
		# Trait-Based Function to Estimate Value of State
		measurements = Measurement.measure(grid)

		estimation = 0
		for chromosome in self.chromosomes:
			for i in range(7):
				gene = chromosome.genes[i]
				estimation += measurements[gene.feature] * gene.weight

		return round(estimation, 6)

	def replace(self, feature):
		for chromosome in self.chromosomes:
			for index, gene in enumerate(chromosome.genes):
				if gene.feature == feature:
					chromosome.genes[index] = Gene(CATEGORY[index](refuse=gene.subcategory))

	def meiosis(self):
		alpha, beta = self.chromosomes
		gametes = [[],[],[],[]]
		for index in range(7):
			genes = [
				alpha.genes[index].clone(),
				beta.genes[index].clone(),
				alpha.genes[index].clone(),
				beta.genes[index].clone()
			]

			order = sample(genes, 4)

			for i in range(4):
				gene = order[i]
				gametes[i].append(gene)

		return gametes

class Algorithm:
	def __init__(self, master, piece_sequences):
		self.master = master

		self.piece_sequences = piece_sequences

		self.sequence_index = 0
		self.end_of_sequences = len(self.piece_sequences)

		self.population_index = 0
		self.end_of_population = POPULATION_SIZE

		self.generation_index = 0
		self.end_of_generations = NUMBER_OF_GENERATIONS

		self.performances = []

		self.total = 0

	def crowdsource(self):
		# Compare Performance to Traits Across All Cells
		ratings = {}
		for index in range(POPULATION_SIZE):
			cell = self.population[index]
			performance = self.performances[index]

			for chromosome in cell.chromosomes:
				total_weight = 0
				for gene in chromosome.genes:
					total_weight += abs(gene.weight)

				for gene in chromosome.genes:
					effect = round(performance * (abs(gene.weight) / total_weight), 6)
					if gene.feature in ratings:
						ratings[gene.feature].append(effect)
					else:
						ratings[gene.feature] = [effect]

		trait_values = []
		for key in ratings:
			score = round(sum(ratings[key]) / len(ratings[key]), 6)
			trait_values.append([score, gene.feature])

		return trait_values

	def adapt(self, trait_values):
		# Swap Low Performing Gene with New Gene
		minimum = trait_values[0]
		for trait in trait_values:
			if abs(trait[0]) <= abs(minimum[0]):
				minimum = trait

		weakest_link = minimum[1]
		for cell in self.population:
			cell.replace(weakest_link)

	def aggregate(self, trait_values):
		# Adjust Existing Traits
		for cell in self.population:
			for chromosome in cell.chromosomes:
				for trait in trait_values:
					for gene in chromosome.genes:
						if gene.feature == trait[1]:
							if trait[0] > 0:
								gene.enhance()
							elif trait[0] < 0:
								gene.degrade()

	def reproduce(self):
		# Select Pairs of Cells Based on Performance Ratings
		ordered_chaos = list(zip(self.performances, self.population))
		ordered_chaos.sort()

		quarter = POPULATION_SIZE // 4
		
		ordered_population = [i[1] for i in ordered_chaos]
		# Extract best 25%
		top_25_percent = ordered_population[-quarter:]
		# Extract middle 50%
		middle_50_percent = ordered_population[quarter:-quarter]

		elite = sample(top_25_percent, quarter)
		commoner = sample(middle_50_percent, quarter)

		offspring = []
		for index in range(quarter):
			# For Each Cell, Generate 4 Gametes
			sperms = elite[index].meiosis()
			eggs = commoner[index].meiosis()
			# Select Gametes from Each Cell and Combine to Produce New Cell
			for i in range(4):
				offspring.append(Cell(Chromosome(sperms[i]), Chromosome(eggs[i])))

		self.population = offspring

	def mutate(self):
		# Alter Value of Random Trait
		for cell in self.population:
			chance = random()
			if chance < MUTATION_RATE:
				gene_number = randrange(7)
				for chromosome in cell.chromosomes:
					chromosome.genes[gene_number].randomShift()

	def outerLoop(self):
		if self.generation_index == self.end_of_generations:
			print("ALGORITHM COMPLETE")
			return
		
		print(str.format("Generation: {}", self.generation_index))
		self.middleLoop()
		#print("\n")

	def middleLoop(self):
		if self.population_index == self.end_of_population:
			trait_values = self.crowdsource()
			self.adapt(trait_values)
			self.aggregate(trait_values)
			self.reproduce()
			self.mutate()

			self.generation_index += 1
			self.performances = []
			self.population_index = 0
			self.outerLoop()
			return
		
		self.innerLoop()


	def innerLoop(self):
		if self.sequence_index == self.end_of_sequences:
			print(str.format("  Strategy: {} >> Average Score: {}", self.population_index, self.total//self.end_of_sequences))
			
			self.performances.append(round(self.total / self.end_of_sequences, 6))

			self.population_index += 1
			self.sequence_index = 0
			self.total = 0
			self.middleLoop()
			return
		
		cell = self.population[self.population_index]
		piece_sequence = self.piece_sequences[self.sequence_index]
		Simulation(self.master, self, piece_sequence, cell).run()
		self.sequence_index += 1

	def run(self):
		self.population = []
		for i in range(POPULATION_SIZE):
			alpha = Chromosome([Gene(CATEGORY[i]()) for i in range(7)])
			refusal_set = alpha.subcategories
			beta = Chromosome([Gene(CATEGORY[i](refusal_set[i])) for i in range(7)])
			self.population.append(Cell(alpha, beta))

		self.outerLoop()

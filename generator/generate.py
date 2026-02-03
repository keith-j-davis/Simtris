import sys
import math
import random
import textwrap

def generate(number_of_games, minimum_drops, maximum_drops):
	filename = str.format("Random{}-{}-{}.tetris", number_of_games, minimum_drops, maximum_drops)
	with open(filename, "w") as page:
		for game in range(int(number_of_games)):
			if game > 0:
				page.write("$")
			
			n = random.randrange(int(minimum_drops), int(maximum_drops) + 1)

			sequence = ""
			number_of_iterations = math.ceil(n/7)
			for i in range(number_of_iterations):
				bag = ["1", "2", "3", "4", "5", "6", "7"]
				while bag:
					size = len(bag)
					index = math.floor(random.random() * size)
					selection = bag.pop(index)
					sequence += selection

			lines = textwrap.wrap(sequence[:n], 80)
			for line in lines:
				page.write(line + "\n")

if __name__ == "__main__":
	number_of_games = 8
	minimum_drops = 256
	maximum_drops = 256
	generate(8, 256, 256)
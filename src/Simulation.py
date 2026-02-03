MINIMUM_VALUE = float("-inf")

ROWS = 20
COLUMNS = 10

WAIT = 20

I = lambda: [[[20,3],[20,4],[20,5],[20,6]], [[21,5],[20,5],[19,5],[18,5]]]
O = lambda: [[[21,4],[21,5],[20,4],[20,5]],]
T = lambda: [[[21,4],[20,3],[20,4],[20,5]], [[21,4],[20,4],[20,5],[19,4]], [[20,3],[20,4],[20,5],[19,4]], [[21,4],[20,3],[20,4],[19,4]]]
S = lambda: [[[21,4],[21,5],[20,3],[20,4]], [[21,4],[20,4],[20,5],[19,5]]]
Z = lambda: [[[21,3],[21,4],[20,4],[20,5]], [[21,5],[20,4],[20,5],[19,4]]]
J = lambda: [[[21,3],[20,3],[20,4],[20,5]], [[21,4],[21,5],[20,4],[19,4]], [[20,3],[20,4],[20,5],[19,5]], [[21,4],[20,4],[19,3],[19,4]]]
L = lambda: [[[21,5],[20,3],[20,4],[20,5]], [[21,4],[20,4],[19,4],[19,5]], [[20,3],[20,4],[20,5],[19,3]], [[21,3],[21,4],[20,4],[19,4]]]

BOARD = lambda: [[0,0,0,0,0,0,0,0,0,0] for row in range(ROWS)]
PIECE = {1: I, 2: O, 3: T, 4: S, 5: Z, 6: J, 7: L}

SINGLE = 100
DOUBLE = 300
TRIPLE = 500
TETRIS = 800

CLEAR = {0: 0, 1: SINGLE, 2: DOUBLE, 3: TRIPLE, 4:TETRIS}

HARD_DROP = 2

from copy import deepcopy
from random import choice

class Simulation:
	def __init__(self, master, algorithm, piece_sequence, cell):
		self.master = master
		self.algorithm = algorithm

		self.grid = BOARD()
		self.pieces = list(piece_sequence)
		self.cell = cell

		self.score = 0
		self.lines_cleared = 0
		self.pieces_played = 0

	def collision(self, coordinate_set):
		for coordinate in coordinate_set:
			row, column = coordinate
			if row < 0 or column < 0 or column >= COLUMNS:
				return True
			if row >= ROWS:
				continue
			if self.grid[row][column] > 0:
				return True
		return False

	def drop(self, coordinate_set):
		coordinate_set = deepcopy(coordinate_set)
		translation = 0

		legal = True
		while legal:
			for coordinate in coordinate_set:
				coordinate[0] -= 1

			translation += 1

			if self.collision(coordinate_set):
				legal = False

		for coordinate in coordinate_set:
			coordinate[0] += 1

		translation -= 1

		return coordinate_set, translation

	def consider(self, piece):
		possible_futures = []
		for coordinate_set in piece:
			if self.collision(coordinate_set):
				break
			else:
				possible_futures.append(self.drop(coordinate_set))

			for direction in [-1, 1]:
				translation = 0

				legal = True
				while legal:
					for coordinate in coordinate_set:
						coordinate[1] += direction

					translation += direction

					if self.collision(coordinate_set):
						legal = False
					else:
						possible_futures.append(self.drop(coordinate_set))

				for coordinate in coordinate_set:
					coordinate[1] -= translation
					
		return possible_futures

	def transition(self, coordinate_set, key):
		grid = deepcopy(self.grid)

		loss_condition = False
		for coordinate in coordinate_set:
			row, column = coordinate
			if row >= ROWS:
				loss_condition = True
				continue
			grid[row][column] = key

		return grid, loss_condition

	def inventory(self, grid):
		lines = []
		for row in range(ROWS):
			count = 0
			for column in range(COLUMNS):
				key = grid[row][column]
				if key > 0:
					count += 1
				else:
					break

			if count == 10:
				lines.append(row)

		return lines

	def clear(self, grid, lines):
		for row in range(ROWS - 1, -1, -1):
			if row in lines:
				for r in range(row, ROWS - 1):
					for column in range(COLUMNS):
						grid[r][column] = grid[r+1][column]

				for column in range(COLUMNS):
					grid[ROWS - 1][column] = 0

		return grid

	def estimate(self, grid):
		return self.cell.estimate(grid)

	def utility(self, lines, distance):
		return CLEAR[len(lines)] + distance * HARD_DROP

	def update(self):
		self.master.render(self.grid)

	def callback(self):
		self.master.retrieve(self.score, self.lines_cleared, self.pieces_played, self.cell)
		self.algorithm.total += self.score
		self.algorithm.innerLoop()

	def loop(self):
		if not self.pieces:
			return self.callback()

		key = int(self.pieces.pop(0))
		piece = PIECE[key]()

		possible_futures = self.consider(piece)

		if not possible_futures:
			return self.callback()

		solution = None
		estimate = MINIMUM_VALUE
		game_over = True
		points = 0
		clears = 0
		for future in possible_futures:
			coordinate_set, distance = future

			state, loss_condition = self.transition(coordinate_set, key)

			lines = self.inventory(state)
			if lines:
				state = self.clear(state, lines)

			estimation = self.estimate(state)
			utility = self.utility(lines, distance)

			update_solution = False
			if not game_over and loss_condition:
				update_solution = False
			elif solution == None or (game_over and not loss_condition) or estimation > estimate:
				update_solution = True
			elif estimation == estimate:
				update_solution = choice([True, False])

			if update_solution:
				solution = state
				estimate = estimation
				game_over = loss_condition
				points = utility
				clears = len(lines)

		self.grid = solution
		self.score += points
		self.lines_cleared += clears
		self.pieces_played += 1
		self.update()
		
		if game_over:
			return self.callback()

		self.master.after(WAIT, self.loop)

	def run(self):
		self.loop()

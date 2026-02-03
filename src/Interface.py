ROWS = 20
COLUMNS = 10

SIZE = 32

WIDTH = 1 + (COLUMNS * SIZE)
HEIGHT = 1 + (ROWS * SIZE)

BG = "#111111"
FG = "#888888"

CYAN = "cyan"
YELLOW = "yellow"
PURPLE = "purple"
GREEN = "#00FF00"
RED = "red"
BLUE = "blue"
ORANGE = "orange"

COLOR = {
	0: BG, 1: CYAN, 2: YELLOW, 3: PURPLE, 4: GREEN, 5: RED, 6: BLUE, 7: ORANGE
}

from tkinter import Tk, Menu, Canvas
import tkinter.filedialog as filedialog
from src.Algorithm import Algorithm

class Renderer(Canvas):
	def __init__(self, master):
		super().__init__(master, width=WIDTH, height=HEIGHT, bg=BG)

		self.images = []
		for row in range(ROWS):
			self.images.append([])
			for column in range(COLUMNS):
				x = 2 + (column * SIZE)
				y = 2 + ((ROWS - (row + 1)) * SIZE)
				bounding_box = [x, y, x + SIZE, y + SIZE]
				image = self.create_rectangle(bounding_box, fill=BG, outline=FG)
				self.images[row].append(image)

	def render(self, grid):
		for row in range(ROWS):
			for column in range(COLUMNS):
				image = self.images[row][column]
				color = COLOR[grid[row][column]]
				self.itemconfig(image, fill=color)

class Interface(Tk):
	def __init__(self):
		super().__init__()

		self.renderer = Renderer(self)
		self.renderer.pack()

	def load(self, filename):
		with open(filename, "r") as file:
			sequences = file.read().replace("\n", "").split("$")

		Algorithm(self, sequences).run()

	def render(self, grid):
		self.renderer.render(grid)

	def retrieve(self, score, lines_cleared, pieces_played, cell):
		with open("log.txt", "a") as file:
			file.write("Policy:\n")
			alpha, beta = cell.chromosomes
			for i in range(7):
				alpha_gene = alpha.genes[i]
				beta_gene = beta.genes[i]
				file.write(str.format("--{}--\n", alpha_gene.category))
				file.write(str.format("  {:<28}: {:>9.6f}\n", alpha_gene.feature, alpha_gene.weight))
				file.write(str.format("  {:<28}: {:>9.6f}\n", beta_gene.feature, beta_gene.weight))
			file.write(str.format("Score: {}\n", score))
			file.write(str.format("Lines Cleared: {}\n", lines_cleared))
			file.write(str.format("Pieces Played: {}\n\n", pieces_played))

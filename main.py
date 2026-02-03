from src.Interface import Interface

class Application(Interface):
	def __init__(self):
		super().__init__()

		self.title("Experiment")
		self.resizable(False, False)

	def run(self):
		self.after(0, self.load("data/Random8-256-256.tetris"))
		self.mainloop()

if __name__ == "__main__":
	Application().run()

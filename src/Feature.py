ROWS=20
COLUMNS=10

OCCUPIED="OCCUPIED"
UNOCCUPIED="UNOCCUPIED"
HOLES="HOLES"
OCCUPANCY_RATIO="OCCUPANCY_RATIO"
UNINHABITABLE="UNINHABITABLE"
WEIGHTED_OCCUPIED="WEIGHTED_OCCUPIED"
MEAN_WEIGHTED_OCCUPIED="MEAN_WEIGHTED_OCCUPIED"

OCCUPIED_ROWS="OCCUPIED_ROWS"
MEAN_OCCUPIED_PER_ROW="MEAN_OCCUPIED_PER_ROW"
OCCUPIED_COLUMNS="OCCUPIED_COLUMNS"
MEAN_OCCUPIED_PER_COLUMN="MEAN_OCCUPIED_PER_COLUMN"
WEIGHTED_OCCUPIED_ROW="WEIGHTED_OCCUPIED_ROW"
MEAN_WEIGHTED_OCCUPIED_ROW="MEAN_WEIGHTED_OCCUPIED_ROW"

DEPTH="DEPTH"
MEAN_DEPTH="MEAN_DEPTH"
MAX_DEPTH="MAX_DEPTH"
ACCESSIBILITY="ACCESSIBILITY"
MEAN_ACCESSIBILITY="MEAN_ACCESSIBILITY"
MAX_ACCESSIBILITY="MAX_ACCESSIBILITY"

COVER="COVER"
MEAN_COVER="MEAN_COVER"
MAX_COVER="MAX_COVER"
OVERCAST="OVERCAST"
MEAN_OVERCAST="MEAN_OVERCAST"
MAX_OVERCAST="MAX_OVERCAST"

CONTACT="CONTACT"
MEAN_CONTACT="MEAN_CONTACT"
OCCUPIED_CLUSTERS="OCCUPIED_CLUSTERS"
UNOCCUPIED_CLUSTERS="UNOCCUPIED_CLUSTERS"
HOLE_CLUSTERS="HOLE_CLUSTERS"
MAX_HOLE_CLUSTER="MAX_HOLE_CLUSTER"
MEAN_HOLE_CLUSTER="MEAN_HOLE_CLUSTER"

MAX_HEIGHT="MAX_HEIGHT"
HEIGHT="HEIGHT"
MEAN_HEIGHT="MEAN_HEIGHT"
FILL="FILL"
MAX_HEIGHT_DIFFERENCE="MAX_HEIGHT_DIFFERENCE"
ROUGHNESS="ROUGHNESS"
MEAN_ROUGHNESS="MEAN_ROUGHNESS"

TOWER_LEVELS="TOWER_LEVELS"
TOWERS="TOWERS"
MAX_TOWER_OVERSHADOW="MAX_TOWER_OVERSHADOW"
MEAN_TOWER_LEVELS="MEAN_TOWER_LEVELS"
WELL_LEVELS="WELL_LEVELS"
WELLS="WELLS"
MAX_WELL_DEPTH="MAX_WELL_DEPTH"
MEAN_WELL_DEPTH="MEAN_WELL_DEPTH"
PLAINS="PLAINS"
MAX_PLAIN_WIDTH="MAX_PLAIN_WIDTH"

from random import choice

class Measurement:
	@staticmethod
	def normalize(value, minimum, maximum):
		return round((value - minimum) / (maximum - minimum), 6)

	@staticmethod
	def measure(grid):
		occupied = 0
		occupied_row_list = [False]*ROWS
		occupied_column_list = [False]*COLUMNS
		contact = 0
		depth = 0
		max_depth = 0
		accessibility = 0
		max_accessibility = 0
		cover = 0
		max_cover = 0
		overcast = 0
		max_overcast = 0
		column_heights = [0]*COLUMNS
		column_towers = [0]*COLUMNS
		column_wells = [0]*COLUMNS
		weighted_occupied = 0
		for row in range(ROWS):
			for column in range(COLUMNS):
				value = grid[row][column]
				if value > 0:
					occupied += 1
					occupied_row_list[row] = True
					occupied_column_list[column] = True
					weighted_occupied += row

					for coord in [(row+1,column),(row-1,column),(row,column+1),(row,column-1)]:
						r, c = coord
						if r >= 0 and r < ROWS and c >= 0 and c < COLUMNS:
							v = grid[r][c]
							if v > 0:
								contact += 1

					north = row+1
					temp_depth = 0
					while north < ROWS and grid[north][column] > 0:
						temp_depth += 1
						north += 1

					depth += temp_depth
					if temp_depth > max_depth:
						max_depth = temp_depth

					north = row+1
					temp_accessibility = 0
					while north < ROWS and grid[north][column] == 0:
						temp_accessibility += 1
						north += 1

					accessibility += temp_accessibility
					if temp_accessibility > max_accessibility:
						max_accessibility = temp_accessibility

					north = row+1
					temp_cover = 0
					while north < ROWS:
						if grid[north][column] > 0:
							temp_cover += 1
						north += 1

					cover += temp_cover
					if temp_cover > max_cover:
						max_cover = temp_cover

					south = row-1
					temp_overcast = 0
					while south >= 0 and grid[south][column] == 0:
						temp_overcast += 1
						south -= 1

					overcast += temp_overcast
					if temp_overcast > max_overcast:
						max_overcast = temp_overcast

					temp_height = row+1
					if temp_height > column_heights[column]:
						column_heights[column] = temp_height

					west = column-1
					east = column+1
					if west >= 0 and east < COLUMNS:
						west_val = grid[row][west]
						east_val = grid[row][east]
						if west_val == 0 and east_val == 0:
							north = row+1
							covered = False
							while north < ROWS:
								if grid[north][west] > 0:
									covered = True
									break
								if grid[north][east] > 0:
									covered = True
									break
								north += 1
							if not covered:
								column_towers[column] += 1

					if west < 0:
						west_val = 1
						east_val = grid[row][east]
					elif east >= COLUMNS:
						west_val = grid[row][west]
						east_val = 1
					else:
						west_val = grid[row][west]
						east_val = grid[row][east]

					if west_val > 0 and east_val > 0 and temp_cover == 0:
						column_wells[column] += 1

		unoccupied = 200 - occupied
		occupied_rows = sum(occupied_row_list)
		occupied_columns = sum(occupied_column_list)

		if occupied == 0:
			mean_occupied_per_row = 0
			mean_occupied_per_column = 0
			mean_contact = 0
			mean_depth = 0
			mean_accessibility = 0
			mean_cover = 0
			mean_overcast = 0
		else:
			mean_occupied_per_row =  occupied / occupied_rows
			mean_occupied_per_column = occupied / occupied_columns
			mean_contact = contact / occupied
			mean_depth = depth / occupied
			mean_accessibility = accessibility / occupied
			mean_cover = cover / occupied
			mean_overcast = overcast / occupied

		values = []
		coordinates = []
		for row in range(ROWS):
			for column in range(COLUMNS):
				values.append(grid[row][column])
				coordinates.append([row, column])

		occupied_clusters = 0
		unoccupied_clusters = 0
		hole_clusters = 0
		holes = 0
		max_hole_cluster = 0
		while not all(item == -1 for item in values):
			ind, value = next([ind, val] for ind, val in enumerate(values) if val >= 0)
			cluster_coords = [coordinates[ind]]
			values[ind] = -1
			reaches_sky = False
			index = 0

			while index < len(cluster_coords):
				row, column = cluster_coords[index]
				for coord in [(row+1,column),(row-1,column),(row,column+1),(row,column-1)]:
					r, c = coord
					if r >= 0 and r < ROWS and c >= 0 and c < COLUMNS:
						i = r * COLUMNS + c
						v = values[i]
						if value == v:
							cluster_coords.append(coordinates[i])
							values[i] = -1
							if r == ROWS - 1:
								reaches_sky = True
				index += 1

			if value > 0:
				occupied_clusters += 1
			else:
				unoccupied_clusters += 1
				if not reaches_sky:
					hole_clusters += 1
					temp_holes = len(cluster_coords)
					holes += temp_holes
					if temp_holes > max_hole_cluster:
						max_hole_cluster = temp_holes

		if holes == 0:
			mean_hole_cluster = 0
		else:
			mean_hole_cluster = holes / hole_clusters

		height = 0
		max_height = 0
		for h in column_heights:
			height += h
			if h > max_height:
				max_height = h

		roughness = 0
		max_height_difference = 0
		for i, h in enumerate(column_heights[:COLUMNS-1]):
			next_height = column_heights[i+1]
			difference = abs(h - next_height)
			roughness += difference
			if difference > max_height_difference:
				max_height_difference = difference

		towers = 0
		tower_levels = 0	
		max_tower_overshadow = 0
		for i in range(1, COLUMNS-1):
			levels = column_towers[i]
			if levels > 0:
				towers += 1
				tower_levels += levels

				left = column_heights[i-1]
				center = column_heights[i]
				right = column_heights[i+1]
				tower_overshadow = ((center - left) + (center - right)) / 2
				if tower_overshadow > max_tower_overshadow:
					max_tower_overshadow = tower_overshadow

		if tower_levels == 0:
			mean_tower_levels = 0
			fill = 1
		else:
			mean_tower_levels = tower_levels / towers
			fill = height / occupied

		wells = 0
		well_levels = 0
		max_well_depth = 0
		for i in range(COLUMNS):
			levels = column_wells[i]
			if levels > 0:
				wells += 1
				well_levels += levels

				center = column_heights[i]
				if i == 0:
					right = column_heights[i+1]
					well_depth = right - center
				elif i == COLUMNS - 1:
					left = column_heights[i-1]
					well_depth = left - center
				else:
					left = column_heights[i-1]
					right = column_heights[i+1]
					well_depth = ((left - center) + (right - center)) / 2

				if well_depth > max_well_depth:
					max_well_depth = well_depth

		if well_levels == 0:
			mean_well_depth = 0
		else:
			mean_well_depth = well_levels / wells

		plains = 0
		max_plain_width = 0
		is_plains = False
		for i in range(1, COLUMNS):
			prior = column_heights[i-1]
			current = column_heights[i]
			if prior == current:
				if not is_plains:
					is_plains = True
					plain_width = 1
				if plains == 0:
					plains = 1
				plains += 1
				plain_width += 1
				if plain_width > max_plain_width:
					max_plain_width = plain_width
			else:
				is_plains = False

		weighted_occupied_row = 0
		for i, row in enumerate(occupied_row_list):
			if row:
				weighted_occupied_row += i+1

		if occupied == 0:
			mean_weighted_occupied_row = 0
			mean_weighted_occupied = 0
		else:
			mean_weighted_occupied_row = weighted_occupied_row / occupied_rows
			mean_weighted_occupied = weighted_occupied / occupied

		return {
			OCCUPIED: Measurement.normalize(occupied, 0, ROWS*COLUMNS-ROWS),
			UNOCCUPIED: Measurement.normalize(unoccupied, ROWS, ROWS*COLUMNS),
			HOLES: Measurement.normalize(holes, 0, 171),
			OCCUPANCY_RATIO: Measurement.normalize(occupied / unoccupied, 0, COLUMNS-1),
			UNINHABITABLE: Measurement.normalize(holes / unoccupied, 0, 0.994186),
			WEIGHTED_OCCUPIED: Measurement.normalize(weighted_occupied, 0, 1890),
			MEAN_WEIGHTED_OCCUPIED: Measurement.normalize(mean_weighted_occupied, 0, 16.266667),
			OCCUPIED_ROWS: Measurement.normalize(occupied_rows, 0, ROWS),
			MEAN_OCCUPIED_PER_ROW: Measurement.normalize(mean_occupied_per_row, 0, COLUMNS-1),
			OCCUPIED_COLUMNS: Measurement.normalize(occupied_columns, 0, COLUMNS),
			MEAN_OCCUPIED_PER_COLUMN: Measurement.normalize(mean_occupied_per_column, 0, ROWS),
			WEIGHTED_OCCUPIED_ROW: Measurement.normalize(weighted_occupied_row, 0, 210),
			MEAN_WEIGHTED_OCCUPIED_ROW: Measurement.normalize(mean_weighted_occupied_row, 0, 10.5),
			DEPTH: Measurement.normalize(depth, 0, 1710),
			MEAN_DEPTH: Measurement.normalize(mean_depth, 0, 9.5),
			MAX_DEPTH: Measurement.normalize(max_depth, 0, ROWS-1),
			ACCESSIBILITY: Measurement.normalize(accessibility, 0, 189),
			MEAN_ACCESSIBILITY: Measurement.normalize(mean_accessibility, 0, ROWS-1),
			MAX_ACCESSIBILITY: Measurement.normalize(max_accessibility, 0, ROWS-1),
			COVER: Measurement.normalize(cover, 0, 1710),
			MEAN_COVER: Measurement.normalize(mean_cover, 0, 9.5),
			MAX_COVER: Measurement.normalize(max_cover, 0, ROWS-1),
			OVERCAST: Measurement.normalize(overcast, 0, 171),
			MEAN_OVERCAST: Measurement.normalize(mean_overcast, 0, 6.107143),
			MAX_OVERCAST: Measurement.normalize(max_overcast, 0, ROWS-1),
			CONTACT: Measurement.normalize(contact, 0, 662),
			MEAN_CONTACT: Measurement.normalize(mean_contact, 0, 3.677778),
			OCCUPIED_CLUSTERS: Measurement.normalize(occupied_clusters, 0, 100),
			UNOCCUPIED_CLUSTERS: Measurement.normalize(unoccupied_clusters, 1, 100),
			HOLE_CLUSTERS: Measurement.normalize(hole_clusters, 0, 95),
			MAX_HOLE_CLUSTER: Measurement.normalize(max_hole_cluster, 0, 171),
			MEAN_HOLE_CLUSTER: Measurement.normalize(mean_hole_cluster, 0, 171),
			MAX_HEIGHT: Measurement.normalize(max_height, 0, ROWS),
			HEIGHT: Measurement.normalize(height, 0, ROWS*COLUMNS),
			MEAN_HEIGHT: Measurement.normalize(height / COLUMNS, 0, ROWS),
			FILL: Measurement.normalize(fill, 1, 6.428571),
			MAX_HEIGHT_DIFFERENCE: Measurement.normalize(max_height_difference, 0, 20),
			ROUGHNESS: Measurement.normalize(roughness, 0, 180),
			MEAN_ROUGHNESS: Measurement.normalize(roughness / (COLUMNS-1), 0, 20),
			TOWER_LEVELS: Measurement.normalize(tower_levels, 0, 80),
			TOWERS: Measurement.normalize(towers, 0, 4),
			MAX_TOWER_OVERSHADOW: Measurement.normalize(max_tower_overshadow, 0, 20),
			MEAN_TOWER_LEVELS: Measurement.normalize(mean_tower_levels, 0, 20),
			WELL_LEVELS: Measurement.normalize(well_levels, 0, 100),
			WELLS: Measurement.normalize(wells, 0, 5),
			MAX_WELL_DEPTH: Measurement.normalize(max_well_depth, 0, 20),
			MEAN_WELL_DEPTH: Measurement.normalize(mean_well_depth, 0, 20),
			PLAINS: Measurement.normalize(plains, 0, 10),
			MAX_PLAIN_WIDTH: Measurement.normalize(max_plain_width, 0, 10)
		}

class Feature:
	@staticmethod
	def select(category, options, refuse):
		if refuse:
			options.pop(refuse)

		subcategory = choice(list(options.keys()))
		feature = choice(options[subcategory])

		return category, subcategory, feature

	@staticmethod
	def resilience(refuse=None):
		options = {
			"A": [OCCUPIED, UNOCCUPIED, HOLES],
			"B": [OCCUPANCY_RATIO, UNINHABITABLE],
			"C": [WEIGHTED_OCCUPIED, MEAN_WEIGHTED_OCCUPIED]
		}

		return Feature.select("resilience", options, refuse)

	@staticmethod
	def temperament(refuse=None):
		options = {
			"D": [OCCUPIED_ROWS, MEAN_OCCUPIED_PER_ROW],
			"E": [OCCUPIED_COLUMNS, MEAN_OCCUPIED_PER_COLUMN],
			"F": [WEIGHTED_OCCUPIED_ROW, MEAN_WEIGHTED_OCCUPIED_ROW]
		}

		return Feature.select("temperament", options, refuse)

	@staticmethod
	def approachability(refuse=None):
		options = {
			"G": [DEPTH, MEAN_DEPTH, MAX_DEPTH],
			"H": [ACCESSIBILITY, MEAN_ACCESSIBILITY, MAX_ACCESSIBILITY]
		}

		return Feature.select("approachability", options, refuse)

	@staticmethod
	def dominance(refuse=None):
		options = {
			"I": [COVER, MEAN_COVER, MAX_COVER],
			"J": [OVERCAST, MEAN_OVERCAST, MAX_OVERCAST]
		}

		return Feature.select("dominance", options, refuse)

	@staticmethod
	def density(refuse=None):
		options = {
			"K": [CONTACT, MEAN_CONTACT],
			"L": [OCCUPIED_CLUSTERS, UNOCCUPIED_CLUSTERS, HOLE_CLUSTERS],
			"M": [MAX_HOLE_CLUSTER, MEAN_HOLE_CLUSTER]
		}

		return Feature.select("density", options, refuse)

	@staticmethod
	def height(refuse=None):
		options = {
			"N": [MAX_HEIGHT, HEIGHT, MEAN_HEIGHT],
			"O": [FILL],
			"P": [MAX_HEIGHT_DIFFERENCE, ROUGHNESS, MEAN_ROUGHNESS]
		}

		return Feature.select("height", options, refuse)

	@staticmethod
	def texture(refuse=None):
		options = {
			"Q": [TOWER_LEVELS, TOWERS, MAX_TOWER_OVERSHADOW, MEAN_TOWER_LEVELS],
			"R": [WELL_LEVELS, WELLS, MAX_WELL_DEPTH, MEAN_WELL_DEPTH],
			"S": [PLAINS, MAX_PLAIN_WIDTH]
		}

		return Feature.select("texture", options, refuse)

CATEGORY = {
	0: Feature.resilience,
	1: Feature.temperament,
	2: Feature.approachability,
	3: Feature.dominance,
	4: Feature.density,
	5: Feature.height,
	6: Feature.texture
}

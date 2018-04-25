from Optimization import Optimizer
import numpy as np

""" test_dim
	Tests the simulation for increasing grid dimensions
"""
def test_dim():
	o = Optimizer()
	vecs = []
	scores = []
	for dim in range(10, 110, 10):
		best_vecs = []
		best_scores = []
		for _ in range(1):
			best_vec, best_score = o.optimize(dim)
			best_vecs.append(best_vec)
			best_scores.append(best_score)
		scores.append(np.mean(best_scores))
		vecs.append((np.mean([v[0] for v in best_vecs]), np.mean([v[1] for v in best_vecs]), np.mean([v[2] for v in best_vecs])))
	print('Optimal Scores: ', scores)
	print('Optimal Vectors: ', vecs)


""" test_masks
	Tests the simulation by varying number of masks
	Outputs the number of people infected at the end of the simulation
"""
def test_masks():
	o = Optimizer()
	res = []
	for masks in range(10, 110, 10):
		res.append(np.mean([o.run(masks=masks, doses=0, vaccines=0) for _ in range(3)]))
	print('Results for Varying Masks: ', res)

""" test_doses
	Tests the simulation by varying number of doses
	Outputs the number of people infected at the end of the simulation
"""
def test_doses():
	o = Optimizer()
	res = []
	for doses in range(10, 110, 10):
		res.append(np.mean([o.run(masks=0, doses=doses, vaccines=0) for _ in range(3)]))
	print('Results for Varying Doses: ', res)

""" test_vaccines
	Tests the simulation by varying number of vaccines
	Outputs the number of people infected at the end of the simulation
"""
def test_vaccines():
	o = Optimizer()
	res = []
	for vaccines in range(10, 110, 10):
		res.append(np.mean([o.run(masks=0, doses=0, vaccines=vaccines) for _ in range(3)]))
	print('Results for Varying Vaccines: ', res)


def main():

	# Test the variation of several different parameters

	# Find optimal scores with increasing dimension
	test_dim()

	# Find no of infected people with varying masks
	test_masks()

	# Find no of infected people with varying doses
	test_doses()
    
	# Find no of infected people with varying vaccines
	test_vaccines()


if __name__ == '__main__':
    main()
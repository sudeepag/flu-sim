from Optimization import Optimizer
import numpy as np

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


def test_masks():
	o = Optimizer()
	res = []
	for masks in range(10, 110, 10):
		res.append(np.mean([o.run(masks=masks, doses=0, vaccines=0) for _ in range(3)]))
	print('Results for Varying Masks: ', res)

def test_doses():
	o = Optimizer()
	res = []
	for doses in range(10, 110, 10):
		res.append(np.mean([o.run(masks=0, doses=doses, vaccines=0) for _ in range(3)]))
	print('Results for Varying Doses: ', res)

def test_vaccines():
	o = Optimizer()
	res = []
	for masks in range(10, 110, 10):
		res.append(np.mean([o.run(masks=0, doses=0, vaccines=vaccines) for _ in range(3)]))
	print('Results for Varying Vaccines: ', res)


def main():

	# Test the variation of several different parameters
	# Find optimal scores with increasing dimension
	# test_dim()

	test_masks()

	test_doses()

	test_vaccines()


if __name__ == '__main__':
    main()
import numpy as np
import pytest
from sklearn.cluster import DBSCAN
from ampligraph.discovery.discovery import discover_facts, \
    generate_candidates, _setdiff2d, find_clusters
from ampligraph.latent_features import ComplEx

def test_discover_facts():

    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model = ComplEx(batches_count=1, seed=555, epochs=2, k=5)

    with pytest.raises(ValueError):
        discover_facts(X, model)

    model.fit(X)

    with pytest.raises(ValueError):
        discover_facts(X, model, strategy='error')

    with pytest.raises(ValueError):
        discover_facts(X, model, strategy='random_uniform', target_rel='error')



def test_generate_candidates():

    X = np.array([['a', 'y', 'i'],
                  ['b', 'y', 'j'],
                  ['c', 'y', 'k'],
                  ['d', 'y', 'l'],
                  ['e', 'y', 'm'],
                  ['f', 'y', 'n'],
                  ['g', 'y', 'o'],
                  ['h', 'y', 'p']])

    # Not sure this should be an error
    # with pytest.raises(ValueError):
    #     generate_candidates(X, strategy='error', target_rel='y',
    #                         max_candidates=4)


    # with pytest.raises(ValueError):
    #     generate_candidates(X, strategy='random_uniform', target_rel='y',
    #  max_candidates=0)

    # Test
    gen = generate_candidates(X, strategy='random_uniform', target_rel='y',
                              max_candidates=4, consolidate_sides=False)
    Xhat = next(gen)

    # Max_candidates shape ..
    assert Xhat.shape == (4, 3)

    gen = generate_candidates(X, strategy='random_uniform', target_rel='y',
                              max_candidates=4, consolidate_sides=False)
    Xhat = next(gen)

    # Consolidate sides=False only has characters a-g on LHS, i-p on RHS
    assert np.all(np.isin(Xhat[:, 0],
                          np.array(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])))
    assert np.all(np.isin(Xhat[:, 2],
                          np.array(['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p'])))

    gen = generate_candidates(X, strategy='random_uniform', target_rel='y',
                              max_candidates=10, consolidate_sides=True)
    Xhat = next(gen)

    # Check that any of the head or tail entities from X has been found
    # on the OTHER side of the candidates
    # Chance that this test fails with probability:
    assert np.logical_or(
        np.any(np.isin(Xhat[:, 2],
                       np.array(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']))),
        np.all(np.isin(Xhat[:, 0],
                       np.array(['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']))))


def test_setdiff2d():

    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])

    Y = np.array([['a', 'z', 'b'],
                  ['b', 'z', 'a'],
                  ['a', 'z', 'c'],
                  ['c', 'z', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])

    ret1 = np.array([['a', 'y', 'b'],
                     ['b', 'y', 'a'],
                     ['a', 'y', 'c'],
                     ['c', 'y', 'a']])

    ret2 = np.array([['a', 'z', 'b'],
                     ['b', 'z', 'a'],
                     ['a', 'z', 'c'],
                     ['c', 'z', 'a']])

    assert np.array_equal(ret1, _setdiff2d(X, Y))
    assert np.array_equal(ret2, _setdiff2d(Y, X))

    # i.e., don't use it as setdiff1d
    with pytest.raises(RuntimeError):
        X = np.array([1, 2, 3, 4, 5, 6])
        Y = np.array([1, 2, 3, 7, 8, 9])
        _setdiff2d(X, Y)

def test_find_clusters():
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'x', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model = ComplEx(k=2, batches_count=2)
    model.fit(X)
    clustering_algorithm = DBSCAN(min_samples=1)

    expected_clusters = np.array([0, 1, 2, 3, 4, 5, 6, 7])

    labels = find_clusters(X, model, clustering_algorithm)
    assert np.array_equal(labels, expected_clusters)
    labels = find_clusters(X, model, clustering_algorithm, entities_subset=[])
    assert np.array_equal(labels, expected_clusters)
    labels = find_clusters(X, model, clustering_algorithm, relations_subset=[])
    assert np.array_equal(labels, expected_clusters)

    labels = find_clusters(X, model, clustering_algorithm, entities_subset=['a', 'b'])
    assert labels.shape == (2,)
    labels = find_clusters(X, model, clustering_algorithm, relations_subset=['x'])
    assert labels.shape == (7,)
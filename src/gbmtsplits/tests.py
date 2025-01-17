# Unit test for gbmt-splits
import os
import pandas as pd
from unittest import TestCase

from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator

from .split import GloballyBalancedSplit
from .clustering import RandomClustering, MaxMinClustering, LeaderPickerClustering, MurckoScaffoldClustering


class TestSplits(TestCase):

    test_data_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')
    seed = 2022
    time_limit = 10

    def test_random_split(self):

        data = pd.read_csv(self.test_data_path)
        ncols = data.shape[1]
        clustering = RandomClustering(seed=self.seed)
        splitter = GloballyBalancedSplit(
            sizes = [0.9, 0.1], 
            clustering_method = clustering,
            time_limit_seconds=self.time_limit,
        )
        data = splitter(data)

        assert data.shape[1] == ncols + 2
        assert data.Split.nunique() == 2

    def test_dissimilarity_maxmin_split(self):
            
        data = pd.read_csv(self.test_data_path)
        ncols = data.shape[1]
        clustering = MaxMinClustering(seed=self.seed, n_clusters=10)
        splitter = GloballyBalancedSplit(
            sizes = [0.7, 0.1, 0.1, 0.1], 
            clustering_method = clustering,
            time_limit_seconds=self.time_limit,
        )
        data = splitter(data)

        assert data.shape[1] == ncols + 2
        assert data.Split.nunique() == 4

    def test_dissimilarity_leader_split(self):
            
        data = pd.read_csv(self.test_data_path)
        ncols = data.shape[1]
        clustering = LeaderPickerClustering(
            fp_calculator=GetMorganGenerator(radius=2, fpSize=1024),
            similarity_threshold=0.6)
        splitter = GloballyBalancedSplit(
            clustering_method = clustering,
            time_limit_seconds=self.time_limit,
        )
        data = splitter(data)

        assert data.shape[1] == ncols + 2
        assert data.Split.nunique() == 3

    def test_murcko_scaffold_split(self):
    
        data = pd.read_csv(self.test_data_path)
        ncols = data.shape[1]
        clustering = MurckoScaffoldClustering()
        splitter = GloballyBalancedSplit(
            clustering_method = clustering,
            time_limit_seconds=self.time_limit,
            min_distance=False
        )
        data = splitter(data)

        assert data.shape[1] == ncols + 1
        assert data.Split.nunique() == 3

    def test_multiple_random_splits(self):

        data = pd.read_csv(self.test_data_path)
        ncols = data.shape[1]
        clustering = RandomClustering(seed=self.seed)
        splitter = GloballyBalancedSplit(
            clustering_method = clustering,
            time_limit_seconds=self.time_limit,
            n_splits=3
        )
        data = splitter(data)

        assert data.shape[1] == ncols + (3 * 2)
        for i in range(3):
            assert data[f'Split_{i}'].nunique() == 3
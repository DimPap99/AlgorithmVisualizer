import random
from Algorithms.Registry import Registry

# weights go from MIN_WEIGHT to MAX_WEIGHT, or from -MAX_WEIGHT for the algorithms that handle negative weights
MIN_WEIGHT, MAX_WEIGHT = 1, 99


# Every weight distribution is a WeightDistribution subclass with a display name and its parameters with their
# default values, which registers it automatically. Subclasses implement sample(), which draws one weight.
# Usage: weights = WeightDistribution.get("Gaussian")({'mean': 10, 'std': 3}).weights(graph.nodes_dict)
class WeightDistribution(Registry):
    kind = "weight distribution"

    def __init__(self, params=None):
        self.setParams(params)

    def sample(self):
        raise NotImplementedError

    # returns a weight for every node id, rounded and clamped to [min_weight, MAX_WEIGHT]
    def weights(self, node_ids, min_weight=MIN_WEIGHT):
        min_weight = min(MAX_WEIGHT, max(-MAX_WEIGHT, min_weight))
        return {node_id: min(MAX_WEIGHT, max(min_weight, round(self.sample()))) for node_id in node_ids}


class Uniform(WeightDistribution):
    name = "Uniform"
    params = {'low': 1, 'high': 10}

    def sample(self):
        return random.uniform(self.low, self.high)


class Gaussian(WeightDistribution):
    name = "Gaussian"
    params = {'mean': 10, 'std': 4}

    def sample(self):
        return random.gauss(self.mean, self.std)


# Mostly cheap nodes with a few expensive ones
class Exponential(WeightDistribution):
    name = "Exponential"
    params = {'mean': 5}

    def __init__(self, params=None):
        super().__init__(params)
        if self.mean <= 0:
            raise ValueError("'mean' must be positive")

    def sample(self):
        return random.expovariate(1 / self.mean)


# Every node gets the weight with the given probability, otherwise it costs 1
class Bernoulli(WeightDistribution):
    name = "Bernoulli"
    params = {'probability': 0.3, 'weight': 15}

    def sample(self):
        return self.weight if random.random() < self.probability else 1

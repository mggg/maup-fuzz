import random
import shapely
import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPoint, Polygon
from shapely.ops import voronoi_diagram, unary_union
from gerrychain.graph import adjacency


def generate_random_points(n: int = 100, width: int = 1, height: int = 1) -> MultiPoint:
    points = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(n)]
    return MultiPoint(points)

def generate_geometries_voronoi(points: MultiPoint, width: int = 1, height: int = 1):
    envelope = Polygon([(0,0), (0, width), (height, width), (height, 0)])

    geometries = gpd.GeoSeries(voronoi_diagram(points, envelope=None)).explode() # crop later
    
    geometries = geometries.map(lambda x: x.intersection(envelope))
    geometries.index = geometries.index.droplevel(0)
    return geometries

def random_combine_geometries(geometries, target_num = 50):
    """
    Uniformly sampled merges
    """
    adjacencies = adjacency.queen(geometries)
    indicies = [set([x]) for x in geometries.index]
    while len(indicies) > target_num:
        left_choice, right_choices = random.sample(adjacencies.items(), 1)[0]
        right_choice = random.sample(right_choices.keys(), 1)[0]

        new_indicies = []
        merges = set()
        for index in indicies:
            if left_choice in index or right_choice in index:
                merges |= index
            else:
                new_indicies.append(index)
        new_indicies.append(merges)
        indicies = new_indicies

        del right_choices[right_choice] # should modify in-place
        adjacencies = dict((k, v) for k, v in adjacencies.items() if v)

    assignment = [] # groupby
    for x in geometries.index:
        found = False

        for c, index in enumerate(indicies):
            if x in index and not found:
                assignment.append(c)
                found = True

        if not found:
            raise ValueError("Invariant check failed.")
    assignment = pd.Series(assignment)

    return geometries.groupby(assignment).apply(unary_union), assignment

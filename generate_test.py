import generate
import maup
import secrets
import math
from shapely.geometry import Polygon
import pytest

"""
TODO: run tests many times
"""

@pytest.mark.parametrize('execution_number', range(5))
def test_generate_random_points(execution_number):
    k = secrets.randbelow(100)
    points = generate.generate_random_points(k)
    assert len(points) == k

@pytest.mark.parametrize('execution_number', range(50))
def test_generate_geometries_voronoi(execution_number):
    points = generate.generate_random_points(500)
    geometries = generate.generate_geometries_voronoi(points)
    assert len(geometries) == 500
    assert math.isclose(geometries.unary_union.area, 1)

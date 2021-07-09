#!/usr/bin/env python3
import generate
import random
import maup
import typer
import tqdm
import traceback
import sys
from functools import wraps
from shapely.errors import ShapelyDeprecationWarning
from tblib import pickling_support
import secrets
from shapely import speedups
import pickle
import time

import warnings; warnings.filterwarnings('ignore', "GeoSeries.isna", UserWarning)
import warnings; warnings.filterwarnings('ignore', "", ShapelyDeprecationWarning)

speedups.enable()
app = typer.Typer()
state = {}
pickling_support.install()

def generate_voronoi(n: int = 1000):
    return generate.generate_geometries_voronoi(generate.generate_random_points(n))

def generate_nesting(small_n: int = 10000, big_n: int = 1000):
    small = generate_voronoi(small_n)
    big, grouping = generate.random_combine_geometries(small, big_n)
    return small, big, grouping

def fuzz(func):
    @wraps(func)
    @app.command()
    def decorated(times: int = 0):
        count = 0
        if times > 0:
            pbar = tqdm.tqdm(times)
        else:
            pbar = tqdm.tqdm()
        while times <= 0 or count == times:
            pbar.update()
            try:
                func()
            # except KeyboardInterrupt:
            #     break
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                state["exc_type"] = exc_type
                state["exc_value"] = exc_value
                state["exc_traceback"] = exc_traceback

                with open(f"crashdump-{exc_type.__name__}-{time.time()}-{secrets.token_hex(4)}.pickle", "wb") as f:
                    pickle.dump(state, f)

                print(traceback.print_tb(exc_traceback))

                if exc_type==KeyboardInterrupt:
                    break

            count += 1

@fuzz
def assign_nest(times: int = 0):
    try:
        small, big, grouping = generate_nesting(random.randint(5000, 15000), random.randint(1000, 4999))

        assignment = maup.assign(small, big)
        assert (assignment == grouping).all()
        assert len(assignment) == len(small)

        reverse_assignment = maup.assign(big, small)
        assert len(reverse_assignment) == len(big)
        # TODO: calculate plausibilty of assignment with grouping
    except:
        global state
        state = locals()
        raise

@fuzz
def intersections_lateral():
    """
    Checks that intersections is commutative
    """
    try:
        source = generate_voronoi(random.randint(1000, 1200))
        target = generate_voronoi(random.randint(1000, 1200))
        pieces = maup.intersections(source, target)
        reverse_pieces = maup.intersections(target, source)
        assert len(pieces) == len(reverse_pieces)
    except:
        global state
        state = locals()
        raise

@fuzz
def intersections_nest():
    """
    Checks that intersections returns the more granular geometry when source and target nest
    """
    try:
        source, target, grouping = generate_nesting(random.randint(5000, 15000), random.randint(1000, 4999))
        pieces = maup.intersections(source, target)
        reverse_pieces = maup.intersections(target, source)
        assert len(pieces) == len(reverse_pieces)
        assert len(source) > len(target)
        assert len(pieces) == len(source)
        assert len(reverse_pieces) == len(source)
    except:
        global state
        state = locals()
        raise

@fuzz
def aggregate(times: int = 0):
    pass

@fuzz
def prorate():
    pass

@fuzz
def disaggregate():
    pass

if __name__ == "__main__":
    app()

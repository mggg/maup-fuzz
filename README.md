## maup-fuzzer
A multipurpose fuzzer primarily intended to target `maup`.

## Usage
```
python fuzz.py [function]
```
Currently, you can fuzz:
- `assign-nest` (checks if `maup.assign` works properly on perfectly nested, tiled geometries)
- `intersections-lateral` (checks if `maup.intersections` is commutative on perfectly nested, tiled geometries)
- `intersections-nest` (checks if `maup.intersections` will return the source geometries when source nests perfectly within target geometries)


## Writing your own fuzzer
To write your own fuzzer (or add a new part of `maup` to function), just add the `@fuzz` decorator and save your state in the `state` global variable.

Example:
```python
@fuzz
def fuzzer(some_input):
    try:
        cells = generate_voronoi(1000)  # generate_voronoi generates a random voronoi diagram with 1000 cells
        geometries = random_combine_geometries(cells, target_num=100)) # randomly merge cells to reach the target

        # Do some assertion here. For example:
        assert len(geometries) == 100

    except: # log your error and state if it fails
        global state
        state = locals()  # save all local variables for easy debugging
        raise  # re-raise the error so a crash dump is saved
```

Note that composing `generate_voronoi()` and `random_combine_geometries()` will result in generating polygons, which can be convex. This allows all possible perfect tilings to be generated by composing the two functions together.
For only concave polygons, just use `generate_voronoi()`. 

Anything you set will be stored in `state` will be saved on crashes.

## Debugging crashes
State, traceback objects, and output from `sys.exc_info()` are automatically stored in a pickled Python object when an error is raised.
The pickled Python object will be named `crashdump-$ERROR-$TIME-$UID.pickle` where `$ERROR` is the type of error raised, `$TIME` is the result of `time.time()` and `UID` is a randomly generated string.

This pickle file can be loaded post-mortem like so:
```python
In [1]: import pickle

In [2]: with open("crashdump-KeyboardInterrupt-1625761771.8713498-c773c94b.pickle", "rb") as f:
   ...:     state = pickle.load(f)

In [3]: state.keys()
Out[3]: dict_keys(['times', 'small', 'exc_type', 'exc_value', 'exc_traceback'])
```

As you can see, the local enviroment variables and useful traceback objects are saved.

## Bugs Discovered Thus Far
- `maup.intersections()` creates more geometries than either `source` or `target` when both are perfect tilings and source geometries nest perfectly within target geometries. This is likely due to floating point precision issues as filtering by area above a certain small threshold (0.000001) resolves the issue usually.

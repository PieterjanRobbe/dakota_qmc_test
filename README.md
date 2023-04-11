# README

Some experiments with the Halton and Hammersley sequences implemented in `Dakota`.

```
$ dakota -v
Dakota version 6.17 released Nov. 15 2022.
Repository revision a32262a0e (2022-11-09) built Apr  9 2023 21:06:35.
```

We compare the following sequences:
- random points (3 random seeds)
- Halton sequence (with and without `latinize` option)
- Hammersley sequence (with and without `latinize` option)

We test the performance of these sequences by integrating the `Genz` function `cp1` (corner peak) in `d=64` dimensions.

> `Dakota` actually doesn't allow the Halton points to be used with the `sampling` method. The implementation in `fsu_quasi_mc` is for Design of Computer Experiments. Instead, I used the `HDF5` capabilities of `Dakota` to extract the generated points and model evaluations. 

As we discovered earlier, plain Halton points perform poorly in this case, especially in high dimensions. When used for integration purposes, the points are actually worse than random points. The convergence of the absolute error seems faster, but the constant is very large.

> *side note* `Dakota` gets killed when requesting `samples = 1` and `latinize`?
# ==========================================================
# import statements
import argparse
import os
import numpy as np
import shlex
import subprocess
import tempfile
import h5py

# ==========================================================
# special imports

# ==========================================================
# define defaults
defaults = {
    "template_file": "dakota.in.template",
    "dimension": 1,
    "analysis_components": "os1",
    "nb_of_samples": 1024,
    "method": "random",
    "seed": 1234,
    "latinize": False
}

# ==========================================================
# function to replace keywords
def parse_keywords(**kwargs):
    kwargs = {k: kwargs.get(k, v) for k, v in defaults.items()}
    replace = dict()
    replace["template_file"] = kwargs["template_file"]
    replace["dimension"] = str(kwargs["dimension"])
    replace["analysis_components"] = kwargs["analysis_components"]
    replace["lower_bounds"] = "0 "*kwargs["dimension"]
    replace["upper_bounds"] = "1 "*kwargs["dimension"]
    replace["nb_of_samples"] = str(kwargs["nb_of_samples"])
    if kwargs["method"] in ["random", "lhs"]:
        replace["method"] = "sampling sample_type " + kwargs["method"]
        replace["extra_keys"] = "seed " + str(kwargs["seed"])
    else:
        replace["method"] = "fsu_quasi_mc " + kwargs["method"]
        replace["extra_keys"] = "latinize" if kwargs["latinize"] else ""
    return replace

# ==========================================================
# wrapper for dakota 'genz' example
def dakota_genz(**kwargs):

    # keywords to replace
    replace = parse_keywords(**kwargs)

    # read dakota template file
    with open(replace["template_file"], "r") as io:
        template = io.readlines()

    # within a temp directory, do...
    with tempfile.TemporaryDirectory() as tmp:

        # create input file
        dakota_in = os.path.join(tmp, "dakota.in")
        with open(dakota_in, "w") as io:
            for line in template:
                for k, v in replace.items():
                    search_str = "{" + k + "}"
                    if search_str in line:
                        line = line.replace(search_str, v)
                io.write(line)

        # run dakota
        cmd = "dakota -i dakota.in"
        with open(os.path.join(tmp, "log.dakota.out"), "w") as out:
            with open(os.path.join(tmp, "log.dakota.err"), "w") as err:
                subprocess.run(shlex.split(cmd), stdout=out, stderr=err, cwd=tmp)

        # read output
        file = h5py.File(os.path.join(tmp, "dakota_results.h5"), "r")
        return np.mean(file["methods"]["NO_METHOD_ID"]["sources"]["NO_MODEL_ID"]["responses"]["functions"])

# ==========================================================
# main function
def main():

    # parse arguments
    parser = argparse.ArgumentParser(description="Runs dakota 'Genz' example.")
    parser.add_argument("-t", "--template_file", type=str, default=defaults["template_file"],
        help=f"dakota input file template (default is '{defaults['template_file']}')")
    parser.add_argument("-d", "--dimension", type=int, default=defaults["dimension"],
        help=f"number of dimensions (default is {defaults['dimension']})")
    parser.add_argument("-a", "--analysis_components", type=str, default=defaults["analysis_components"],
        help=f"coefficient decay (default is '{defaults['analysis_components']}', see dakota manual)")
    parser.add_argument("-m", "--method", type=str, default=defaults["method"],
        help=f"choose from 'random', 'lhs', 'halton' or 'hammersly' (default is '{defaults['method']}')")
    parser.add_argument("-n", "--nb_of_samples", type=int, default=defaults["nb_of_samples"],
        help=f"number of samples (default is {defaults['nb_of_samples']})")
    parser.add_argument("-s", "--seed", type=int, default=defaults["seed"],
        help=f"random seed value (default is {defaults['seed']}, only used with 'random' and 'lhs')")
    parser.add_argument("-l", "--latinize", action="store_true",
        help=f"use 'latinize' option in dakota (default is off, only used with 'halton' and 'hammersly')")
    args = parser.parse_args()

    # run dakota_genz
    print(dakota_genz(**vars(args)))

# ==========================================================
# use this script as standalone
if __name__ == "__main__":
    main()
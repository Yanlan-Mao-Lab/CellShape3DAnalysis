# APPLY VOLUME MERGE ANNOTATION
#
# This script applies a webKnossos merger mode annotation
# to a given segmentation layer. The script will output a
# TIFF image sequence.
#
# The --set_zero flag will relabel all non-annotated segments
# to 0.
#
# 1. Download the merger mode NML file.
# 2. Install Python 3 (if you don't have it)
# 3. Install the dependencies of this script:
#    pip install -U wkw wknml wkcuber libtiff
# 4. Run the script from the terminal:
#    python apply_merger_mode.py \
#      /path/to/input_wkw \
#      merger_mode.nml \
#      /path/to/output_tiff
# 5. The script will output a folder with TIFF files
#
# License: MIT, scalable minds
# Norman Rzepka - https://gist.github.com/normanrz

import wkw
import wknml
import re
from argparse import ArgumentParser
from wkcuber.metadata import read_metadata_for_layer
import numpy as np
from libtiff import TIFF
from glob import iglob
from os import path, makedirs

# Prelude
parser = ArgumentParser(description="Apply webKnossos volume merge annotations")
parser.add_argument(
    "--set_zero",
    action="store_true",
    help="Set non-marked segments to zero.",
)
parser.add_argument("input", help="Path to input WKW dataset")
parser.add_argument("--layer_name", "-l", help="Segmentation layer name", default="segmentation")
parser.add_argument("nml", help="Path to NML file")
parser.add_argument("output", help="Path to output tiff files")
args = parser.parse_args()

print("Merging merger mode annotations from {} and {}".format(args.input, args.nml))

# Collect equivalence classes from NML
with open(args.nml, "rb") as f:
  nml = wknml.parse_nml(f)

ds_in = wkw.Dataset.open(path.join(args.input, args.layer_name, "1"))
cube_size = ds_in.header.block_len * ds_in.header.file_len

equiv_classes = [
  set(ds_in.read(node.position, (1,1,1))[0,0,0,0] for node in tree.nodes)
    for tree in nml.trees
]

equiv_map = {}
for klass in equiv_classes:
  base = next(iter(klass))
  for id in klass:
    equiv_map[id] = base

print("Found {} equivalence classes with {} nodes".format(len(equiv_classes), len(equiv_map)))
print(equiv_classes)

# Rewrite segmentation layer
_, _, bbox, origin = read_metadata_for_layer(args.input, args.layer_name)

makedirs(args.output, exist_ok=True)

for z_start in range(origin[2], origin[2] + bbox[2], 32):
  z_end = min(origin[2] + z_start + 32, origin[2] + bbox[2])
  offset = (origin[0], origin[1], z_start)
  size = (bbox[0], bbox[1], z_end - z_start)

  print("Processing cube offset={} size={}".format(offset, size))
  cube_in = ds_in.read(offset, size)[0]

  cube_out = np.zeros(size, dtype=np.uint32)
  if not args.set_zero:
      cube_out[:, :, :] = cube_in
  for from_id, to_id in equiv_map.items():
      cube_out[cube_in == from_id] = to_id
      # print("Applied {} -> {}".format(from_id, to_id))

  for z in range(0, z_end - z_start):
    tif = TIFF.open(path.join(args.output, "{:05d}.tif".format(z + z_start)), mode='w')
    tif.write_image(cube_out[:, :, 0])
    tif.close()
    # print("Wrote section {}".format(z + z_start))
  print("Rewrote cube offset={} size={}".format(offset, size))

# Done
ds_in.close()
print("Rewrote segmentation as tiff sequence to {}".format(args.output))

import filecmp
import json
import os
from os.path import dirname, join
import pytest

import numpy as np
from shutil import rmtree, copytree

from wkw.wkw import WKWException

from wkcuber.api.Dataset import WKDataset, TiffDataset, TiledTiffDataset
from os import path, makedirs

from wkcuber.api.Layer import Layer
from wkcuber.api.Properties.DatasetProperties import TiffProperties, WKProperties
from wkcuber.api.TiffData.TiffMag import TiffReader
from wkcuber.api.bounding_box import BoundingBox
from wkcuber.compress import compress_mag_inplace
from wkcuber.mag import Mag
from wkcuber.utils import get_executor_for_args

from skimage import io
import matplotlib.pyplot as plt

fileName = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/ImageSegmentationPipeline/TestImages/Ricidata/NubG4-UASmyrGFP (Control)/201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK.tif'

# read the image stack
img = io.imread(fileName)

ds = WKDataset.create("/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/ImageSegmentationPipeline/WebKnossos/testOutput/tiff_dataset", scale=(1, 1, 1))
ds.add_layer("color", Layer.COLOR_TYPE)


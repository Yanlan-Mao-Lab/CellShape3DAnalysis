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


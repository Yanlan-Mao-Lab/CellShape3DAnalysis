
from os import path
from tempfile import mkdtemp
import zipfile
import wkw





def read_volume_annotation(filename, offset, shape):
    tmp_dir = mkdtemp()

    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(tmp_dir)

    with zipfile.ZipFile(path.join(tmp_dir, "data.zip"), "r") as zip_ref:
        zip_ref.extractall(path.join(tmp_dir, "segmentation"))

    ds = wkw.Dataset.open(path.join(tmp_dir, "segmentation", "1"))
    return ds.read(offset, shape)[0]


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


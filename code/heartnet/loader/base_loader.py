from os import PathLike
from heartnet.config.base import YamlConfig
import tensorflow as tf
import pathlib
import nibabel as nib
from .preprocess import *


def base_loader(base_dir: PathLike, **kwargs)-> tf.data.Dataset:
    base_dir = pathlib.Path(base_dir)
    images = (base_dir / "images")
    labels = (base_dir / "labels")
    img_ds = tf.data.Dataset.from_tensor_slices(
        [str(i) for i in images.glob("*")]
    )
    label_ds = tf.data.Dataset.from_tensor_slices(
        [str(i) for i in labels.glob("*")]
    )
    dataset = tf.data.Dataset.zip((img_ds, label_ds))

    def load_img(x, y):
        ret_x = nib.load(x.numpy().decode("utf-8")).get_fdata()
        ret_y = nib.load(y.numpy().decode("utf-8")).get_fdata()
        if kwargs.get("augmentations", []):
            for aug in kwargs.get("augmentations", []):
                ret_x, ret_y = aug(ret_x, ret_y)
        return ret_x, ret_y

    def get_img(x, y):
        return tf.py_function(load_img, [x, y], [tf.float32, tf.int32])

    dataset = dataset.map(
        get_img, num_parallel_calls=tf.data.experimental.AUTOTUNE
    )
    return dataset


def load3D(base_dir, output_shape=111, **kwargs):
    dataset = base_loader(base_dir, **kwargs)
    dataset = dataset.map(crop_image_to_shape(output_shape), -1)
    dataset = dataset.map(crop_slices(output_shape), -1)
    return dataset.map(expand_dims, -1)


def load2D(base_dir, **kwargs):
    dataset = base_loader(base_dir, **kwargs)
    dataset = dataset.map(reshape_slices)
    dataset = dataset.map(expand_dims)
    return dataset.flat_map(split_slices)


load_functions = {"UNet": load2D, "UNet3D": load3D}
splits = ["train_folder", "val_folder", "test_folder"]

import tensorflow as tf


def crop_image_to_shape(o):

    def func(img, labels):
        return tf.image.resize_with_crop_or_pad(
            img, o, o
        ), tf.image.resize_with_crop_or_pad(labels, o, o)

    return func


def crop_slices(size):

    def func(x, y):
        offset = (tf.shape(x)[-1] - size) // 2
        return (x[:, :, offset:size + offset], y[:, :, offset:size + offset])

    return func


def reshape_slices(x, y):
    return tf.transpose(x, [2, 0, 1]), tf.transpose(y, [2, 0, 1])


def split_slices(x, y):
    return tf.data.Dataset.from_tensor_slices((x, y))


def expand_dims(x, y):
    return (tf.expand_dims(x, -1), tf.expand_dims(y, -1))


def apply_augmentations(augmentations):

    def func(x, y):
        x, y = x.numpy(), y.numpy()
        for augmentation in augmentations:
            x, y = augmentation(x, y)
        return x, y

    return func

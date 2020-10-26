import numpy as np
from skimage.util.shape import view_as_windows

def estimate_background(img, preset_indices=None, window_shape=(16, 16, 3), step=4):
    img_windows = view_as_windows(img, window_shape, step)
    img_windows_flat = np.reshape(img_windows, (img_windows.shape[0]*img_windows.shape[1], img_windows.shape[3], img_windows.shape[4],  img_windows.shape[5]))
    if preset_indices is None:
        s_windows = np.sum(img_windows_flat, axis=(1, 2, 3))
        indices = np.argsort(s_windows) # ascending 
        a = int(img_windows_flat.shape[0]*0.0001)
        low_indices = indices[-a:]
    else:
        low_indices = preset_indices
    low_patches = img_windows_flat[low_indices]
    bg_mean = np.mean(low_patches, axis=(0, 1, 2))
    return bg_mean, low_indices
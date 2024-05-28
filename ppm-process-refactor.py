import os
import numpy as np
from skimage import io, img_as_float, img_as_ubyte, exposure
from tkinter.filedialog import askdirectory
from tkinter import Tk
from utils import estimate_background

def load_images(path):
    return [os.path.join(path, f) for f in sorted(os.listdir(path))]

def read_image(file, bg_path=None, bg_file=None):
    if bg_path and bg_file:
        return img_as_float(io.imread(os.path.join(bg_path, bg_file)))
    return img_as_float(io.imread(file))

def process_images(img_pos, img_neg):
    """ Processes a pair of images, applying background correction and intensity scaling. """
    pos_v = np.sum(img_pos)
    neg_v = np.sum(img_neg)

    if pos_v > neg_v:
        bg_pos_mean, indices = estimate_background(img_pos)
        bg_neg_mean, _ = estimate_background(img_neg, preset_indices=indices)
    else:
        bg_neg_mean, indices = estimate_background(img_neg)
        bg_pos_mean, _ = estimate_background(img_pos, preset_indices=indices)

    # Normalize background correction factors
    bg_pos_max = np.max(bg_pos_mean)
    bg_neg_max = np.max(bg_neg_mean)
    bg_pos_mean /= bg_pos_max
    bg_neg_mean /= bg_neg_max

    # Apply correction
    cor_img_pos = np.clip(img_pos * bg_pos_mean, 0, 1)
    cor_img_neg = np.clip(img_neg * bg_neg_mean, 0, 1)

    # Differential image processing for feature enhancement
    diff_img = exposure.rescale_intensity(np.abs(cor_img_pos - cor_img_neg), in_range=(0.05, 0.5), out_range=(0, 1))
    
    return diff_img

def save_processed_images(images, result_path, img_name):
    for name, img in images.items():
        io.imsave(os.path.join(result_path, f"{img_name}_{name}.tif"), img_as_ubyte(img))

def setup_directories():
    root = Tk()
    root.withdraw()  # Hide the root window
    dirname = askdirectory(initialdir=os.getcwd(), title='Please select a directory')
    root.destroy()

    base_paths = ['bg', '+5', '-5', 'bf', 'results']
    paths = {bp: os.path.join(dirname, bp) for bp in base_paths}
    os.makedirs(paths['results'], exist_ok=True)
    return paths
    
def main():
    paths = setup_directories()
    files_pos = load_images(paths['+5'])
    files_neg = load_images(paths['-5'])

    for pos_file, neg_file in zip(files_pos, files_neg):
        img_name = os.path.splitext(os.path.basename(pos_file))[0]
        img_pos = read_image(pos_file)
        img_neg = read_image(neg_file)
        processed_img = process_images(img_pos, img_neg)
        save_processed_images(processed_img, paths['results'], img_name)
        print(f'Result saved for: {img_name}')

if __name__ == "__main__":
    main()

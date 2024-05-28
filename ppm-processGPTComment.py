import numpy as np
from skimage.util.shape import view_as_windows
from skimage import io, color, img_as_float, img_as_ubyte, exposure
import glob, os
import matplotlib.pyplot as plt
import tkinter
from tkinter.filedialog import askdirectory
from utils import estimate_background
import matplotlib.pyplot as plt
from PIL import Image

def main():
    # Setup the graphical user interface for directory selection using tkinter
    root = tkinter.Tk()
    dirname = askdirectory(parent=root, initialdir=os.getcwd(), title='Please select a directory')
    dataset_base = dirname  # Base directory for the dataset

    # Define paths for the images based on their polarization and type
    bg_path = os.path.join(dataset_base, 'bg')  # Background images
    pos_path = os.path.join(dataset_base, '+5')  # +5 degree polarized images
    neg_path = os.path.join(dataset_base, '-5')  # -5 degree polarized images
    bf_path = os.path.join(dataset_base, 'bf')  # Brightfield images
    result_path = os.path.join(dataset_base, 'results')  # Directory to save results
    os.makedirs(result_path, exist_ok=True)  # Ensure the results directory exists

    # Check if necessary image directories exist, print error if they do not
    if not os.path.exists(pos_path) and os.path.exists(neg_path):
        print('Negative or positive image folders not found')
    root.destroy()  # Close the tkinter window

    # Gather all image files from each directory and sort them
    file_pos = [os.path.join(pos_path, f) for f in os.listdir(pos_path)]
    file_pos.sort()
    file_neg = [os.path.join(neg_path, f) for f in os.listdir(neg_path)]
    file_neg.sort()
    file_bf = [os.path.join(bf_path, f) for f in os.listdir(bf_path)]
    file_bf.sort()
    if len(file_neg) == 0 or len(file_pos) == 0 or len(file_neg) != len(file_pos):
        print('Negative or positive images not matched')

    # Process each set of images
    for i in range(len(file_pos)):
        img_name = os.path.basename(file_pos[i]).split('.')[0]  # Extract the base name of the image

        # Read background images if they exist, otherwise read the specified polarized images
        if os.path.exists(bg_path):
            img_pos = img_as_float(io.imread(os.path.join(bg_path, 'b+5.tif')))
            img_neg = img_as_float(io.imread(os.path.join(bg_path, 'b-5.tif')))
        else:
            img_pos = img_as_float(io.imread(file_pos[i]))
            img_neg = img_as_float(io.imread(file_neg[i]))

        # Calculate the sum of pixel values for the positive and negative images
        pos_v = np.concatenate(img_pos).sum()
        neg_v = np.concatenate(img_neg).sum()

        # Background estimation and correction based on the greater sum of pixel values
        if pos_v > neg_v:
            bg_pos_mean, indices = estimate_background(img_pos)
            bg_neg_mean, _ = estimate_background(img_neg, preset_indices=indices)
        else:
            bg_neg_mean, indices = estimate_background(img_neg)
            bg_pos_mean, _ = estimate_background(img_pos, preset_indices=indices)

        # Calculate the scaling factors and normalize the background means
        bg_pos_max = np.max(bg_pos_mean)
        bg_neg_max = np.max(bg_neg_mean)
        a_pos = max(bg_pos_max, bg_neg_max) / bg_pos_max
        a_neg = max(bg_pos_max, bg_neg_max) / bg_neg_max
        bg_pos_mean = bg_pos_max / bg_pos_mean
        bg_neg_mean = bg_neg_max / bg_neg_mean

        # Correct the images based on the background estimation
        cor_img_pos = np.clip(img_pos * bg_pos_mean * a_pos, 0, 1)
        cor_img_neg = np.clip(img_neg * bg_neg_mean * a_neg, 0, 1)

        # Calculate mean values after correction and apply intensity scaling
        pos_c_v = np.concatenate(img_pos).mean()
        neg_c_v = np.concatenate(img_neg).mean()
        if neg_c_v > pos_c_v:
            pos_neg = exposure.rescale_intensity(np.clip(cor_img_pos - cor_img_neg, 0, 1), in_range=(0.05, 0.5), out_range=(0, 1))
            neg_pos = exposure.rescale_intensity(np.clip(cor_img_neg - cor_img_pos, 0, 1), in_range=(0.05, 0.5), out_range=(0, 1))
        else:
            neg_pos = exposure.rescale_intensity(np.clip(cor_img_neg - cor_img_pos, 0, 1), in_range=(0.05, 0.5), out_range=(0, 1))
            pos_neg = exposure.rescale_intensity(np.clip(cor_img_pos - cor_img_neg, 0, 1), in_range=(0.05, 0.5), out_range=(0, 1))

        # Combine the processed images, save them, and overlay with brightfield
        result_img = np.clip(pos_neg + neg_pos, 0, 1)
        io.imsave(os.path.join(result_path, img_name+'-5'+'.tif'), img_as_ubyte(neg_pos))
        io.imsave(os.path.join(result_path, img_name+'+5'+'.tif'), img_as_ubyte(pos_neg))
        io.imsave(os.path.join(result_path, img_name+'_result'+'.tif'), img_as_ubyte(result_img))
        print('Result saved for: '+ img_name)
        io.imsave(os.path.join(result_path, img_name+'_color.tif'), img_as_ubyte(result_img))
        gray = np.amax(result_img, 2)  # Convert result to grayscale
        io.imsave(os.path.join(result_path, img_name+'_gray.tif'), img_as_ubyte(gray))

        # Try to overlay the grayscale image with the brightfield image
        try:
            bf_img = img_as_float(io.imread(file_bf[i]))
            green = np.zeros(bf_img.shape)
            green[:, :, 1] = gray  # Set the green channel to the grayscale image
            overlay = np.clip(bf_img + green, 0, 1)  # Overlay and clip to valid range
            io.imsave(os.path.join(result_path, img_name+'_overlay.tif'), img_as_ubyte(overlay))
        except:
            print("Brightfield image not provided!")

if __name__ == "__main__":
    main()

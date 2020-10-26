# Polychromatic polarization microscopy image processing
Polychromatic polarization microscopy is a real-time collagen imaging method in clinical histopathology compatible with brighfield microscopy.

|Brightfield| PPM |
|----------|--------|
|<img src="https://github.com/uw-loci/polychromatic-polarization/blob/master/thumbnails/brightfield.png" width="320">|<img src="https://github.com/uw-loci/polychromatic-polarization/blob/master/thumbnails/ppm.png" width="320">|

## Required packages
Install anaconda/miniconda (https://www.anaconda.com/distribution/) and activate conda base in terminal.  
Create the environment. 
```
  $ conda env create --name ppm --file env.yml
  $ conda activate ppm
  $ pip install pycromanager
```
Jupyter notebook is recommended
```
  $ conda install -c conda-forge jupyterlab
```

## Prepare the image data
* Put positive images and negative images in "data-sample/+5" and "data-sample/-5" folders, respectively.  
* Put brightfield images in "data-sample/bf" (optional).  
**The positive images, negative images, and brightfield images need to have the same name for each sample.**  
* Put background images in "data-sample/bg", named "b-5.tif" and "b+5.tif" (optional). 
These two images are for white-balance correction. The images will be corrected based on estimated values if no background images are provided.  

## Run the processing code
Open ppm-process.ipynb and execute the cells, or run .py in terminal
```  
python ppm-process.py
```
Select the "data-sample" folder in the pop-up window.  
Check outputs in "data-sample/results" folder.
If you use Jupyter Notebook, the results images will also be printed in the notebook. 

# SyntheticLineGenerator 

A synthetic Linegenerator for OCR applications. Based on Belval's TextRecognitionDataGenerator (https://github.com/Belval/TextRecognitionDataGenerator) and NVlabs' ocrodeg (https://github.com/NVlabs/ocrodeg).

Clone this repository and use `pip install -r requirements-hw.txt` 

## How does it work?
In `TextRecognitionDataGenerator`, run `python run.py -c 1000` to get 1000 randomly generated images with a font of your choice. You can set the font in TextRecognitionDataGenerator/fonts, where historic fonts should be placed in the historic-folder. 

In `FontForge`, you will find the .sfd (FontForge projectfile) and .ttf-files for a historic font generated from the 1557-Methodus-Clenardus dataset. Note that "1557-artifically_enhanced_all_chars" contains characters that were not present in the original dataset but have been "composed" of others, e.g. W is composed from 2x V. 

In `text`, you will find .txt-files with all the words from the dataset. For best performance, "shuffled_strings_from_1557_dataset_and_web_clean.txt" should be used as input, as it contains randomly shuffled words from the dataset and is enriched with latin text from the internet. All the words from the 1557-dataset can be found in TextRecognitionGenerator/dicts/hist.txt



## The most important parameters 
The default parameters will make the TextGenerator output all the generated lines in a format with height and margin that fit Calamari (https://github.com/Calamari-OCR/calamari) and 5 words per line. The files will be written to /out. 
For OCR applications, the most important parameters will be listed below. However, there are many more, as you will see when running `python run.py -h`.

- `-i` specify the inputfile. If none is used, words from the hist-dict will be used. 
- `-c` specify the amount of images that are to be generated. Defaults to 1000. 
- `-f` specify the format (==height) of the generated lines. Defaults to `65 px`. 
- `-w` specify the word-count of the generated lines. Defaults to 5 words per line. 
- `-e` specify the extension for the produced images. Defaults to `.png`.  
- `-b` specify the background. Defaults to white. Might be a feature for future extension (e.g. with old vocal sheets). 
- `-m` specify the margins for the text with respect to the border. The format is (upper, left, lower, right). Defaults to a format that is well suited for the 1557-dataset. 
- `-tc` specify the textcolor. Defaults to `#000000` black.
- `-sw` specify the spacing between words. Defaults to 0.5. 
- `-sf` toggle for the show-font prompt. User can see the current font in matplotlib. Only supported for historic fonts. 
- `-ro` toggle for rename-output: When set, the output-files will be given unique hex-filenames instead of incremental filenames. Useful when data from several runs shall be merged. 
- `-rm` toggle for deleting old files in the /out-folder before generating new ones. 
- `-z <path>` toggle for the creation of a zip-file at the end, for easier handling and upload of the generated lines. 

Some minor augmentation features: 
- `-rk` toggle for random skewing of the images, using an angle in the interval `[-x,+x]`, where x is specified with `-k`
- `-rbl` toggle for a random blurring with intensity in the interval `[-x,+x]`, where x is specified with `-bl`


## Data Augmentation 
The script augment_images will apply image augmentation to the given input. The following augmentations will be used: 
- random blobs 
- rotation and rescaling 
- gauﬂian blurring 
- (random noise-) distorsion 

Use `-f` to control the intensity of the augmentation. Use `-s` toggle, if you want the augmented images to be written to their respective separate folders.


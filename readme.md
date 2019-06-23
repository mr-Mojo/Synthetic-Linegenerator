# SyntheticLineGenerator 

A synthetic Linegenerator for OCR applications. Based on Belval's TextRecognitionDataGenerator (https://github.com/Belval/TextRecognitionDataGenerator) and NVlabs' ocrodeg (https://github.com/NVlabs/ocrodeg).

Clone this repository and use `pip install -r requirements-hw.txt` 

## How does it work?
In TextRecognitionDataGenerator, run `python run.py -c 1000` to get 1000 randomly generated images with a font of your choice. You can set the font in TextRecognitionDataGenerator/fonts, where historic fonts should be placed in the historic-folder. 
In FontForge, you will find the .sfd (FontForge projectfile) and .ttf-files for a historic font generated from the 1557-Methodus-Clenardus dataset. Note that "1557-artifically_enhanced_all_chars" contains characters that were not present in the original dataset but have been "composed" of others, e.g. W composed from 2x V. 
In text, you will find .txt-files with all the words from the dataset. For best performance, "shuffled_strings_from_1557_dataset_and_web_clean.txt" should be used as input.


## The most important parameters 
For OCR applications, the most important parameters will be listed below. However, there are many more, as you will see when running `python run.py -h`.


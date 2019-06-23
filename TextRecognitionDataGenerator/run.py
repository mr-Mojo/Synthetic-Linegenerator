import argparse
import os, errno
import random
import string
import math
import uuid
import shutil

from fontTools.ttLib import TTFont


import matplotlib.pyplot as plt 
import matplotlib.font_manager as mfm

import file_parser

from tqdm import tqdm
from string_generator import (
    create_strings_from_dict,
    create_strings_from_file,
    create_strings_from_wikipedia,
    create_strings_randomly
)
from data_generator import FakeTextDataGenerator
from multiprocessing import Pool

def margins(margin):
    margins = margin.split(',')
    if len(margins) == 1:
        return [margins[0]] * 4
    return [int(m) for m in margins]

def parse_arguments():
    """
        Parse the command line arguments of the program.
    """

    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')
    parser.add_argument(
        "--output_dir",
        type=str,
        nargs="?",
        help="The output directory",
        default="out/",
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        nargs="?",
        help="When set, this argument uses a specified text file as source for the text",
        default=""
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        nargs="?",
        help="The language to use, should be fr (French), en (English), es (Spanish), de (German), hist (for historic fonts) or cn (Chinese).",
        default="hist"
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        nargs="?",
        help="The number of images to be created.",
        default=100
    )
    parser.add_argument(
        "-rs",
        "--random_sequences",
        action="store_true",
        help="Use random sequences as the source text for the generation. Set '-let','-num','-sym' to use letters/numbers/symbols. If none specified, using all three.",
        default=False
    )
    parser.add_argument(
        "-let",
        "--include_letters",
        action="store_true",
        help="Define if random sequences should contain letters. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-num",
        "--include_numbers",
        action="store_true",
        help="Define if random sequences should contain numbers. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-sym",
        "--include_symbols",
        action="store_true",
        help="Define if random sequences should contain symbols. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-w",
        "--length",
        type=int,
        nargs="?",
        help="Define how many words should be included in each generated sample. If the text source is Wikipedia, this is the MINIMUM length",
        default=5
    )
    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Define if the produced string will have variable word count (with --length being the maximum)",
        default=False
    )
    parser.add_argument(
        "-f",
        "--format",
        type=int,
        nargs="?",
        help="Define the height of the produced images if horizontal, else the width",
        default=65,
    )
    parser.add_argument(
        "-t",
        "--thread_count",
        type=int,
        nargs="?",
        help="Define the number of thread to use for image generation",
        default=1,
    )
    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        nargs="?",
        help="Define the extension to save the image with",
        default="png",
    )
    parser.add_argument(
        "-k",
        "--skew_angle",
        type=int,
        nargs="?",
        help="Define skewing angle of the generated text. In positive degrees",
        default=0,
    )
    parser.add_argument(
        "-rk",
        "--random_skew",
        action="store_true",
        help="When set, the skew angle will be randomized between the value set with -k and it's opposite",
        default=False,
    )
    parser.add_argument(
        "-wk",
        "--use_wikipedia",
        action="store_true",
        help="Use Wikipedia as the source text for the generation, using this paremeter ignores -r, -n, -s",
        default=False,
    )
    parser.add_argument(
        "-bl",
        "--blur",
        type=int,
        nargs="?",
        help="Apply gaussian blur to the resulting sample. Should be an integer defining the blur radius",
        default=0,
    )
    parser.add_argument(
        "-rbl",
        "--random_blur",
        action="store_true",
        help="When set, the blur radius will be randomized between 0 and -bl.",
        default=False,
    )
    parser.add_argument(
        "-b",
        "--background",
        type=int,
        nargs="?",
        help="Define what kind of background to use. 0: Gaussian Noise, 1: Plain white, 2: Quasicrystal, 3: Pictures",
        default=1,
    )
    parser.add_argument(
        "-hw",
        "--handwritten",
        action="store_true",
        help="Define if the data will be \"handwritten\" by an RNN",
    )
    parser.add_argument(
        "-na",
        "--name_format",
        type=int,
        help="Define how the produced files will be named. 0: [TEXT]_[ID].[EXT], 1: [ID]_[TEXT].[EXT] 2: [ID].[EXT] + one file labels.txt containing id-to-label mappings",
        default=2,
        #file labels.txt will then be parse by file_parser.py to get all the .gt.txt. files 
    )
    parser.add_argument(
        "-d",
        "--distorsion",
        type=int,
        nargs="?",
        help="Define a distorsion applied to the resulting image. 0: None (Default), 1: Sine wave, 2: Cosine wave, 3: Random",
        default=0
    )
    parser.add_argument(
        "-do",
        "--distorsion_orientation",
        type=int,
        nargs="?",
        help="Define the distorsion's orientation. Only used if -d is specified. 0: Vertical (Up and down), 1: Horizontal (Left and Right), 2: Both",
        default=0
    )
    parser.add_argument(
        "-wd",
        "--width",
        type=int,
        nargs="?",
        help="Define the width of the resulting image. If not set it will be the width of the text + 10. If the width of the generated text is bigger that number will be used",
        default=-1
    )
    parser.add_argument(
        "-al",
        "--alignment",
        type=int,
        nargs="?",
        help="Define the alignment of the text in the image. Only used if the width parameter is set. 0: left, 1: center, 2: right",
        default=1
    )
    parser.add_argument(
        "-or",
        "--orientation",
        type=int,
        nargs="?",
        help="Define the orientation of the text. 0: Horizontal, 1: Vertical",
        default=0
    )
    parser.add_argument(
        "-tc",
        "--text_color",
        type=str,
        nargs="?",
        help="Define the text's color, should be either a single hex color or a range in the ?,? format.",
        #default='#282828'
        default='#000000'
    )
    parser.add_argument(
        "-sw",
        "--space_width",
        type=float,
        nargs="?",
        help="Define the width of the spaces between words. 2.0 means twice the normal space width",
        default=0.5
    )
    parser.add_argument(
        "-m",
        "--margins",
        type=margins,
        nargs="?",
        help="Define the margins around the text when rendered. In pixels",
        default=(3,5,3,5) #upper, left, lower, right
    )
    parser.add_argument(
        "-fi",
        "--fit",
        action="store_true",
        help="Apply a tight crop around the rendered text",
        default=False
    )
    parser.add_argument(
        "-sf",
        "--show_font",
        action='store_true'
        help="Show the current font and its available characters before generation of files",
        default=False
    )
    parser.add_argument(
        "-ro",
        "--rename_output",
        action="store_true",
        help="Rename the output, to give a unique filename to the resulting images",
        default=False
    )
    parser.add_argument(
        "-rm",
        "--remove_old",
        action="store_true",
        help="Delete old files that may exist from previous runs",
        default=False
    )
    parser.add_argument(
        "-z",
        "--zip_output",
        action="store_true",
        help="Creates a zipFile with the created png- and gt-Files for easier upload on the server",
        default=False        
    )
# =============================================================================
#     #TODO, not implemented yet 
#     parser.add_argument(
#         "-cs",
#         "--character_spacing",
#         type=float,
#         nargs="?",
#         help="Define the spacing between the characters of a word",
#         default=1.0        
#     )
# =============================================================================

    return parser.parse_args()

def load_dict(lang):
    """
        Read the dictionnary file and returns all words in it.
    """

    lang_dict = []
    with open(os.path.join('dicts', lang + '.txt'), 'r', encoding="utf8", errors='ignore') as d:
        lang_dict = d.readlines()
    return lang_dict

def load_fonts(lang):
    """
        Load all fonts in the fonts directories
    """

    if lang == 'cn':
        return [os.path.join('fonts/cn', font) for font in os.listdir('fonts/cn')]
    elif lang=='hist':
        return [os.path.join('fonts/historic', font) for font in os.listdir('fonts/historic')]
    else:
        return [os.path.join('fonts/latin', font) for font in os.listdir('fonts/latin')]


#this might not look as nice for other fonts with a different number of glyphs
def plot_font(): 
    path = os.path.join('fonts','historic', '1557-true_character_occurence.ttf')
    ttf = TTFont(path, 0, allowVID=0,ignoreDecompileErrors=True,fontNumber=-1)
    prop = mfm.FontProperties(fname=path)
    
    all_chars = [] 
    for x in ttf["cmap"].tables:
        for char in x.cmap.items():
            true_char = chr(char[0])
            all_chars.append(true_char) #all_chars now contains all the characters, format: (unicode, 'char'), e.g. (77, 'M')
    
    final_list = list(dict.fromkeys(all_chars)) #remove duplicate keys 
    final_list[:] = [s for s in final_list if (s.isalpha() or (s in string.punctuation))]      #remove \t,\n,\r, etc
    final_list = final_list[:len(final_list)-1]
    no_of_suplots = math.ceil(math.sqrt(len(final_list)))
    
    
    fig, axs = plt.subplots(no_of_suplots,no_of_suplots, figsize=(8, 8), facecolor='w', edgecolor='k')
    fig.subplots_adjust(hspace = .5, wspace=.001)

    axs = axs.ravel()

    for ax in axs: ax.axis('off')
    for i in range(len(final_list)-2):      #-1 to exclude weird Ê and Ï symbol at the end 
        axs[i].text(0.5,0,s=final_list[i],fontproperties=prop,fontsize=20)
        axs[i].set_title("  " + final_list[i])
        
    fig.tight_layout()
    
    textstr = 'not available: j, k, w, z --- F, J, K, U, V, W, X, Y, Z' 
    plt.text(0.2,0.07, textstr, fontsize=14, transform=plt.gcf().transFigure)
    
    plt.show() 
    ttf.close()


def main():
    """
        Description: Main function
    """



    # Argument parsing
    args = parse_arguments()
    args.count += 1     
    
    # Create font (path) list
    fonts = load_fonts(args.language)

    if args.show_font==True: 
        print('The following font will be used:',fonts[0],'\n')
        char = input('proceed? y(yes), n(no), s(show font)')
        if char=='s' or char=='show font': 
            plot_font()
            char2 = input('proceed? y(yes), n(no)')
            if char2 != 'y': return
        elif char!='y': 
            return 

    # Create the directory if it does not exist.
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Creating word list
    lang_dict = load_dict(args.language)

    curr_dir = os.getcwd()
    os.chdir(args.output_dir)   

    if args.remove_old: 
        answer = input("\n\n-------------------------\n\nWarning. This will delete all png-,zip- and gt.txt files that currently reside in {}. Proceed? (y/n) ".format(os.getcwd()))
        if answer == 'y': 
            for file in os.listdir(os.getcwd()):
                if file.endswith('.png') or file.endswith('.gt.txt') or file.endswith('.zip'): 
                    os.remove(file)
        else: return 

    os.chdir(curr_dir)
    # Creating synthetic sentences (or word)
    strings = []

    if args.use_wikipedia:
        strings = create_strings_from_wikipedia(args.length, args.count, args.language)
    elif args.input_file != '':
        strings = create_strings_from_file(args.input_file, args.count)
    elif args.random_sequences:
        strings = create_strings_randomly(args.length, args.random, args.count,
                                          args.include_letters, args.include_numbers, args.include_symbols, args.language)
        # Set a name format compatible with special characters automatically if they are used
        if args.include_symbols or True not in (args.include_letters, args.include_numbers, args.include_symbols):
            args.name_format = 2
    else:
        strings = create_strings_from_dict(args.length, args.random, args.count, lang_dict)


    string_count = len(strings)

    p = Pool(args.thread_count)
    for _ in tqdm(p.imap_unordered(
        FakeTextDataGenerator.generate_from_tuple,
        zip(
            [i for i in range(0, string_count)],
            strings,
            [fonts[random.randrange(0, len(fonts))] for _ in range(0, string_count)],
            [args.output_dir] * string_count,
            [args.format] * string_count,
            [args.extension] * string_count,
            [args.skew_angle] * string_count,
            [args.random_skew] * string_count,
            [args.blur] * string_count,
            [args.random_blur] * string_count,
            [args.background] * string_count,
            [args.distorsion] * string_count,
            [args.distorsion_orientation] * string_count,
            [args.handwritten] * string_count,
            [args.name_format] * string_count,
            [args.width] * string_count,
            [args.alignment] * string_count,
            [args.text_color] * string_count,
            [args.orientation] * string_count,
            [args.space_width] * string_count,
            [args.margins] * string_count,
            [args.fit] * string_count
        )
    ), total=args.count):
        pass
    p.terminate()



    if args.name_format == 2:
        # Create file with filename-to-label connections
        with open(os.path.join(args.output_dir, "labels.txt"), 'w', encoding="utf8") as f:
            for i in range(string_count):
                file_name = str(i) + "." + args.extension
                f.write("{} {}\n".format(file_name, strings[i]))
                
    #create txt-files for nn groundtruth
    file_parser.parse_labels(args.extension)
    
    #delete 0th file bc it has strange start character that is not displayed in notepad but causes weird glyph in image
    os.chdir(args.output_dir)
    os.remove('0.png')
    os.remove('0.gt.txt')
    os.remove('labels.txt')
    
    
      
    # ------------------ rename all imgs ------------------
    
    if args.rename_output: 
        for file in os.listdir(os.getcwd()):
            
            if file.endswith('.png'): 
                file_name = file.split('.')[0]
                if(len(file_name)) > 10: continue       #important, bc otherwise it will double-find the newly created unique_name.pngs
                txt_file = file_name + '.gt.txt'
                
                unique = str(uuid.uuid4().hex)
                unique_name_png = unique + '.png'
                unique_name_txt = unique + '.gt.txt'
                
                os.rename(file, unique_name_png)
                os.rename(txt_file, unique_name_txt)
                
        
   
    # ------------------ zip images ------------------
    
    if args.zip_output: 
        
        import zipfile 
        
        zip_name = str(uuid.uuid4().hex)+'.zip'
        zip_handler = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        
        for file in os.listdir(os.getcwd()): 
            if not file.endswith('.zip'):
                zip_handler.write(file)
            
        zip_handler.close()
        print("\nCreated Zip-Archive in {}.".format(os.getcwd()))
    
    
    
    
    
    
    
    

if __name__ == '__main__':
    main()

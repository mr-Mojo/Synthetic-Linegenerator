"""
takes "labels.txt" from folder /out, that contains the labels that correspond to the images, and uses these labels to create single .txt files
that can be used as ground truth for the generated images, as they contain the text that is shown on the images. 
"""

import os
import numpy as np 
from fontTools.ttLib import TTFont

#this function takes the 'labels.txt' file that's created by the TextGenerator and parses the content to the respective 
#ground-truth-textfile, .gt.txt for calamari training 
def parse_labels(extension): 
    path_to_current = os.getcwd() 
    path_to_labels = os.path.join(path_to_current,'out','labels.txt')
    
    with open(path_to_labels,'r',encoding='utf8') as textFile: 
        data = textFile.readlines()
        for l in data: 
            file_extension = '.'+extension
            segments = l.split(file_extension)
            segments[1] = segments[1].strip()
            #print(segments[0]," - ",segments[1])
            
            path_for_textfile = os.path.join(path_to_current,'out',segments[0]+'.gt.txt')
            txtFile = open(path_for_textfile,'w',encoding='utf8')
            txtFile.write(segments[1]) 
            txtFile.close()            
    
    
#takes the words from all_strings.txt and randomly shuffles them to create new lines for training 
#this creates whole lines by using the words from the 1557 dataset 
def create_lots_of_strings(string_length,string_count): 
    
    weird_ligs = ['ꝙ','ꝰ','ꝗ̃ ','¶','⸗']
    
    words = [] 
    with open(r'C:\HiWi_6\text\all_strings_1557.txt', encoding='utf8') as textFile: 
        data = textFile.readlines()     
        for i in range(len(data)): 
            line = data[i].strip() 
            words_in_line = line.split(' ')
            for word in words_in_line:
                if word not in words: 
                    for char in word: 
                        if char in weird_ligs: continue
                    words.append(word)
    
    strings = [] 
    
    for i in range(string_count):
        string = '' 
        for i in range(string_length): 
            word = words[np.random.randint(0,len(words))]
            string += (word+ ' ') 
        string += '\n'
        strings.append(string)
    
    #for i in strings: print(i)
    
    outFile = open(r'C:\HiWi_6\text\shuffled_strings_from_1557.txt','w',encoding='utf8')
    for string in strings: outFile.write(string)
    outFile.close() 
    


#this creates new weird words, but somehow it uses chars that are not allowed? 
def create_lots_of_new_random_strings(string_count): 
    
    #get all chars that font supports
    path = r'C:\HiWi_6\TextRecognitionDataGenerator\TextRecognitionDataGenerator\fonts\historic\1557-true_character_occurence.ttf'
    ttf = TTFont(path, 0, allowVID=0,ignoreDecompileErrors=True,fontNumber=-1)
    available_chars = [] 
    for x in ttf["cmap"].tables:
        for char in x.cmap.items():
            true_char = chr(char[0])
            available_chars.append(true_char) 
    
    
    #read all chars from 1557 dataset 
    chars = [] 
    with open(r'C:\HiWi_6\text\all_strings_1557.txt', encoding='utf8') as textFile: 
        data = textFile.readlines()     
        for line in data:
            for char in line: 
                if char not in chars: 
                    chars.append(char)
    
    strings = [] 
    
    #produce string_count diff. strings: 
    for i in range(string_count): 
        s = '' 
        #each string has length random[1,10]
        for j in range(np.random.randint(3,10)): 
            char_to_add = chars[np.random.randint(0,len(chars))]
            if char_to_add not in available_chars: 
                while char_to_add not in available_chars: 
                    char_to_add = chars[np.random.randint(0,len(chars))]
            s += chars[np.random.randint(0,len(chars))]
        s = s.replace(' ','')
        s = s.strip()
        if len(s) > 0: strings.append(s+'\n')
        
    
    
    outFile = open(r'C:\HiWi_6\text\random_strings_from_1557.txt','w',encoding='utf8')
    for string in strings: outFile.write(string)
    outFile.close() 

if __name__ == "__main__": 
    create_lots_of_strings(5,1000)
    #create_lots_of_new_random_strings(1000)
    print('done')

import matplotlib.pyplot as plt 
import scipy.ndimage as ndi
import os,math,random, shutil
import matplotlib.patches as patches
import numpy as np 
from skimage import transform 
from datetime import datetime
import tqdm 
import time, os
import uuid 
import pylab 
import argparse 



parser = argparse.ArgumentParser() 

parser.add_argument(
        "-i",
        "--input_folder",
        type=str,
        nargs="?",
        help="Specify the folder from where the images should be read",
        default=""
    )
parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        nargs="?",
        help="Specify the folder to which the augmented images will be written. If blank, script directory will be used",
        default=""
    )
parser.add_argument(
        "-s",
        "--separate_output",
        action='store_true',
        help="If set, the augmentations will be written to their respective folders, else, all in one folder.",
        default="False"
    )
parser.add_argument(
        "-f",
        "--factor",
        action='store',
        type=float,
        nargs="?",
        help="A factor to increase / decrease augmentation strength. Defaults to one, should be >0",
        default=1.0
    )
parser.add_argument(
        "-r",
        "--rotation_toggle",
        action='store_true',
        help="Argument to switch off rotation as it becomes performance-heavy when factor is high",
        default=False
    )
parser.add_argument(
        "-z",
        "--zip_output",
        action='store_true',
        help="zip the output for easier handling and upload. only applicable if output is not separated by using -s argument",
        default=False
    )



def get_image_paths(path):
    img_paths = [] 
    gt_paths = [] 
    
    plt.rc("image", cmap="gray", interpolation="bicubic")
    
    if not len(os.listdir(path)) >0: 
        print("no images found")
        return
    
    #write all img paths 
    for file in os.listdir(path):
        
        if file.endswith(".png"):
            img_paths.append(os.path.join(path, file))
        if file.endswith(".txt"):
            if not file.startswith("labels"):
                gt_paths.append(os.path.join(path,file))
        
    return img_paths, gt_paths


def scale_and_rotate(img_paths, gt_paths, target_dir, fct): 
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.chdir(target_dir)
    
    #read all imgs from path, set filename to current time, store and copy gt file 
    
    print("\nscaling and rotating {} images:".format(len(img_paths)))
    for i in tqdm.tqdm(range(len(img_paths))):
        filename = uuid.uuid4().hex
        img_name = str(filename) + '.png'
        txt_name = str(filename) + '.gt.txt'
        
        image = plt.imread(img_paths[i])
        if np.size(np.shape(image)) > 2: image = image[:,:,0]    #slice to reduce to grayscale image

        image = transform.rescale(image, np.random.uniform(0.8,1.1)*fct)
        image = transform.rotate(image, math.degrees(np.random.uniform(-0.02,0.02)*fct), mode='edge')  #rotate btwn -5 and 5 deg 
        plt.imsave(img_name,image)
        
        shutil.copy(gt_paths[i],txt_name)
        
    print('rescaled, rotated and saved {} images and copied {} gt-files\n'.format(len(img_paths),len(gt_paths)))
    
    

# nice, apply blur, distorsion and some warping -> like real handwritten ink 
# the bigger sigma, the less blurry and distorted the resulting image will be
def warp_images(img_paths, gt_paths, target_dir, fct): 
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.chdir(target_dir)
    
    print("\ndistorting {} images:".format(len(img_paths)))
    for i in tqdm.tqdm(range(len(img_paths))):
        filename = uuid.uuid4().hex
        img_name = str(filename) + '.png'
        txt_name = str(filename) + '.gt.txt'
        
        image = plt.imread(img_paths[i])
        if np.size(np.shape(image)) > 2: image = image[:,:,0]    #slice to reduce to grayscale image
        sigma = np.random.uniform(4.0, 8.0)*(1/fct)
        noise = bounded_gaussian_noise(image.shape, sigma, 5.0)
        distorted_img = distort_with_noise(image, noise)

        plt.imsave(img_name,distorted_img)
        shutil.copy(gt_paths[i],txt_name)
        
    print('distorted {} images and copied {} gt-files\n'.format(len(img_paths),len(gt_paths)))    



#to blur images a bit, cut out small treshold parts and make the letters look less similar        
def sloppy_blur(img_paths, gt_paths, target_dir, fct): 
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.chdir(target_dir)
    
    print("\nsloppy-blurring {} images:".format(len(img_paths)))
    for i in tqdm.tqdm(range(len(img_paths))): 
        filename = uuid.uuid4().hex
        img_name = str(filename) + '.png'
        txt_name = str(filename) + '.gt.txt'
        
        image = plt.imread(img_paths[i])
        if np.size(np.shape(image)) > 2: image = image[:,:,0]    #slice to reduce to grayscale image
        #blurred_img = ocrodeg.binary_blur(image, np.random.uniform(0.5,3.0))
        blurred_img = ndi.gaussian_filter(image,np.random.uniform(0.5,3.0)*fct)
        tresholded_img = 1.0*(blurred_img>0.5)
        plt.imsave(img_name,tresholded_img)
        
        shutil.copy(gt_paths[i],txt_name)
        
    print('created {} sloppy blurred images and copied {} gt-files\n'.format(len(img_paths),len(gt_paths)))    


def add_random_blobs(img_paths, gt_paths, target_dir, fct): 
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.chdir(target_dir)
    
    print("\nrandom-blobbing {} images:".format(len(img_paths)))
    for i in tqdm.tqdm(range(len(img_paths))): 
        filename = uuid.uuid4().hex
        img_name = str(filename) + '.png'
        txt_name = str(filename) + '.gt.txt' 
    
        image = plt.imread(img_paths[i])
        if np.size(np.shape(image)) > 2: image = image[:,:,0]    #slice to reduce to grayscale image
        blotched_img = random_blotches(image, (3e-4)*fct, (1e-4)*fct)
        plt.imsave(img_name,blotched_img)
        
        shutil.copy(gt_paths[i],txt_name)
        
    print('created {} random-blobbed images and copied {} gt-files\n'.format(len(img_paths),len(gt_paths)))    
    
    
    

def augment_all(src_dir, target_dir): 
    
    image_paths, gt_paths = get_image_paths(src_dir)    
    
    scale_and_rotate(image_paths, gt_paths, target_dir)
    warp_images(image_paths, gt_paths, target_dir)
    sloppy_blur(image_paths,gt_paths, target_dir)
    add_random_blobs(image_paths, gt_paths, target_dir)
    
    
    
    
## copied from degrade.py to avoid version conflicts: 
    
def bounded_gaussian_noise(shape, sigma, maxdelta):
    n, m = shape
    deltas = pylab.rand(2, n, m)
    deltas = ndi.gaussian_filter(deltas, (0, sigma, sigma))
    deltas -= np.amin(deltas)
    deltas /= np.amax(deltas)
    deltas = (2*deltas-1) * maxdelta
    return deltas

def distort_with_noise(image, deltas, order=1):
    assert deltas.shape[0] == 2
    assert image.shape == deltas.shape[1:], (image.shape, deltas.shape)
    n, m = image.shape
    xy = np.transpose(np.array(np.meshgrid(
        range(n), range(m))), axes=[0, 2, 1])
    deltas += xy
    return ndi.map_coordinates(image, deltas, order=order, mode="reflect")

def random_blobs(shape, blobdensity, size, roughness=2.0):
    from random import randint
    h, w = shape
    numblobs = int(blobdensity * w * h)
    mask = np.zeros((h, w), 'i')
    for i in range(numblobs):
        mask[randint(0, h-1), randint(0, w-1)] = 1
    dt = ndi.distance_transform_edt(1-mask)
    mask =  np.array(dt < size, 'f')
    mask = ndi.gaussian_filter(mask, size/(2*roughness))
    mask -= np.amin(mask)
    mask /= np.amax(mask)
    noise = pylab.rand(h, w)
    noise = ndi.gaussian_filter(noise, size/(2*roughness))
    noise -= np.amin(noise)
    noise /= np.amax(noise)
    return np.array(mask * noise > 0.5, 'f')

def random_blotches(image, fgblobs, bgblobs, fgscale=10, bgscale=10):
    fg = random_blobs(image.shape, fgblobs, fgscale)
    bg = random_blobs(image.shape, bgblobs, bgscale)
    return np.minimum(np.maximum(image, fg), 1-bg)
    
    
    



def main(): 
    results = parser.parse_args() 
    
    fct = results.factor 
    
    
    if (results.separate_output==True) and (results.zip_output==True): 
        print("cannot separate and zip output simultaneously. toggle -s or -z.")
        return
    
    if results.output_folder == "": 
        os.mkdir("augmentations")
        results.output_folder = os.path.join(os.getcwd(),"augmentations")
        
    
    
    img_paths, gt_paths = get_image_paths(results.input_folder)
    
    
    if results.separate_output == True: 
        
        root_dir = results.output_folder 
        
        if not results.rotation_toggle: 
            target_dir = os.path.join(root_dir,'scale_and_rotate')
            scale_and_rotate(img_paths,gt_paths,target_dir,fct)
        
        target_dir = os.path.join(root_dir,'warped')
        warp_images(img_paths,gt_paths,target_dir,fct)
        
        target_dir = os.path.join(root_dir,'sloppy_blur')
        sloppy_blur(img_paths,gt_paths,target_dir,fct)
        
        target_dir = os.path.join(root_dir,'random_blobs')
        add_random_blobs(img_paths,gt_paths,target_dir,fct)
    
    
    else: 
        target_dir = results.output_folder     
        
        if not results.rotation_toggle:
            scale_and_rotate(img_paths, gt_paths, target_dir,fct)
        warp_images(img_paths, gt_paths, target_dir,fct)
        sloppy_blur(img_paths,gt_paths, target_dir,fct)
        add_random_blobs(img_paths, gt_paths, target_dir,fct)
    
    
    if results.zip_output == True: 
    
        import zipfile 
        
        zip_name = str(uuid.uuid4().hex)+'.zip'
        zip_handler = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        
        for file in os.listdir(results.output_folder): 
            if not file.endswith('.zip'):
                if file.endswith('.png') or file.endswith('.gt.txt'):
                    zip_handler.write(file)
            
        zip_handler.close()
        print("\nCreated Zip-Archive in {}.".format(results.output_folder))
            
        
    
    
if __name__=='__main__': 
    main() 
    
    
    
    
# =============================================================================
#     called_from_main = True
#     #to augment other images, change this folder 
#     img_dir = r'C:\HiWi_6\TextRecognitionDataGenerator\TextRecognitionDataGenerator\out'
#     #img_dir = 
#     image_paths, gt_paths = get_image_paths(img_dir)    
#     
#     target_dir = r'C:\HiWi_6\calamari_training\\'
#     #cont = raw_input("Attention. When calling this script, lots of augmented files from {} will be written to {}. \nContinue? y(yes) / n(no)".format(img_dir, target_dir))
#     
#     cont = 'y'
#     if cont == 'y':     
#         #scale_and_rotate(image_paths, gt_paths, target_dir)
#         #warp_images(image_paths, gt_paths, target_dir)
#         #sloppy_blur(image_paths,gt_paths, target_dir)
#         add_random_blobs(image_paths, gt_paths, target_dir)
# 
# 
# 
# =============================================================================










#ocrodeg summary: 

# =============================================================================
# #randomly scale and rotate the images a bit 
# for i in xrange(4):
#     plt.subplot(2, 2, i+1)
#     plt.imshow(ocrodeg.transform_image(image, **ocrodeg.random_transform()))
# 
# #similar to above 
# for i, angle in enumerate([-2, -1, 0, 1]):
#     plt.subplot(2, 2, i+1)
#     plt.imshow(ocrodeg.transform_image(image, angle=angle*math.pi/180))
# =============================================================================

# =============================================================================
# # stretch or press images together
# for i, aniso in enumerate([0.5, 1.0, 1.5, 2.0]):
#     plt.subplot(2, 2, i+1)
#     plt.imshow(ocrodeg.transform_image(image, aniso=aniso))
# =============================================================================

# =============================================================================
# # nice, apply blur, distorsion and some warping -> like real handwritten ink 
# for i, sigma in enumerate([1.0, 2.0, 5.0, 20.0]):
#     plt.subplot(2, 2, i+1)
#     noise = ocrodeg.bounded_gaussian_noise(image.shape, sigma, 5.0)
#     distorted = ocrodeg.distort_with_noise(image, noise)
#     h, w = image.shape
#     plt.imshow(distorted[h//2-200:h//2+200, w//3-200:w//3+200])
# =============================================================================

# =============================================================================
# #to rotate around angle 
# for i, angle in enumerate([0, 90, 180, 270]):
#     plt.subplot(2, 2, i+1)
#     plt.imshow(ndi.rotate(image, angle))
# =============================================================================

# =============================================================================
# # to gaussian blur the images 
# for i, s in enumerate([0, 1, 2, 4]):
#     plt.subplot(2, 2, i+1)
#     blurred = ndi.gaussian_filter(image, s)
#     plt.imshow(blurred)    
# =============================================================================
    
# =============================================================================
# # to blur a bit, and cut out small treshold parts -> quite nice 
# for i, s in enumerate([0, 1, 2, 4]):
#     plt.subplot(2, 2, i+1)
#     blurred = ndi.gaussian_filter(image, s)
#     thresholded = 1.0*(blurred>0.5)
#     plt.imshow(thresholded)
# =============================================================================

# =============================================================================
# # similar as above, blur and treshold cutout
# for i, s in enumerate([0.0, 1.0, 2.0, 4.0]):
#     plt.subplot(2, 2, i+1)
#     blurred = ocrodeg.binary_blur(image, s)
#     plt.imshow(blurred)
# =============================================================================

# =============================================================================
# # blur and add noise -> not really relevant I'd say 
# for i, s in enumerate([0.0, 0.1, 0.2, 0.3]):
#     plt.subplot(2, 2, i+1)
#     blurred = ocrodeg.binary_blur(image, 2.0, noise=s)
#     plt.imshow(blurred)
# =============================================================================

# =============================================================================
# # add random blobs to image -> nice as well 
# blotched = ocrodeg.random_blotches(image, 3e-4, 1e-4)
# #blotched = min(max(image, ocrodeg.random_blobs(image.shape, 30, 10)), 1-ocrodeg.random_blobs(image.shape, 15, 8))
# plt.subplot(121)
# plt.imshow(image); 
# plt.subplot(122); 
# plt.imshow(blotched)
# =============================================================================

    
    
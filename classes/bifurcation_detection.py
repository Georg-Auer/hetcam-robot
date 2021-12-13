import cv2
import numpy as np
import imutils
from classes.fingerprint_feature_extractor import extract_minutiae_features

def prepare_and_analyze(img, scale_percent = 10):
    # # only use the red component, because structure is red
    # # https://stackoverflow.com/questions/39903809/wrong-color-reading-an-image-with-opencv-python
    # blue,green,red = cv2.split(img)
    # img = red
    # scale_percent = 10 means 10% of original size, advisable for 4k images
    # Finding bifurcations and terminations takes a really long time otherwise
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    r = resized.copy()
    # set blue and green channels to 0
    r[:, :, 0] = 0
    r[:, :, 2] = 0
    # cv2.imshow("red image",r)

    # cv2.imshow("resized image",resized)

    gray = cv2.cvtColor(r,cv2.COLOR_BGR2GRAY)
    # edges = cv2.Canny(gray, 60, 150, apertureSize=3)
    #edges = cv2.Canny(gray, 1, 90, apertureSize=3)

    # #somehow working
    # edges = cv2.Canny(gray, 19, 25, apertureSize=3)

    # lines = cv2.bitwise_not(edges)
    # cv2.imshow("line detection",lines)

    # cv2.imshow("gray",gray)
    # GRAY IMAGE COULD BE SAVED

    blur = cv2.GaussianBlur(gray,(5,5),0)

    # make a binary image out of grayscale
    # https://docs.opencv.org/master/d7/d4d/tutorial_py_thresholding.html
    thresh255 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,11,2)

    # ret2, thresh255 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # cv2.imshow("threshold1",thresh255)
    # ADAPTIVE THRESHOLD IMAGE COULD BE SAVED
    # print(thresh255)

    thresh255 = cv2.bitwise_not(thresh255)

    # # make a binary image out of grayscale for skeletonize
    blur_inverted = np.invert(blur)
    thresh1 = cv2.adaptiveThreshold(blur_inverted,1,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,11,2)
    # skeletonize is not needed, it is implemented in fingerprint_feature_extractor
    # https://scikit-image.org/docs/dev/auto_examples/edges/plot_skeleton.html
    
    # for saving a skeleton, do it anyways:
    from skimage.morphology import skeletonize
    skeleton = skeletonize(thresh1)
    print("non inverted skeleton")
    print(skeleton)

    # skeleton = cv2.bitwise_not(skeleton)
    # skeleton = np.invert(skeleton)
    # print("inverted skeleton")
    # print(skeleton)

    skeleton = skeleton.astype(np.uint8) # to create numbers out of binary false/true

    # cv2.imshow("binary",thresh1)
    # SKELETON IMAGE COULD BE SAVED
    # skeleton_path = f"{skeleton_image_foldername}/{img_name}"
    # cv2.imshow("skeleton",skeleton)
    # https://stackoverflow.com/questions/44587613/how-to-save-a-binary-imagewith-dtype-bool-using-cv2

    # cv2.imwrite(skeleton_path, skeleton*255) # multiply by 255 to get a b/w image again
    skeleton = skeleton * 255 # multiply by 255 to get a b/w image again

    # find line terminations and bifurcations
    print("Calculating vascular terminations and bifurcations..")
    FeaturesTerminations, FeaturesBifurcations = extract_minutiae_features(thresh255, showResult=False, spuriousMinutiaeThresh=5)

    # this does not work with this fingerprint library
    # name = "bifurcations"
    # from datetime import datetime
    # filename = f'position{name}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.jpg'
    # # writing image
    # cv2.imwrite(filename, FeaturesBifurcations)

    print(dir(FeaturesTerminations))
    print(FeaturesBifurcations)

    x_terminations = []
    y_terminations = []

    print("Terminations at:")
    for element in FeaturesTerminations:
        print(f"X position {element.locX}")
        x_terminations.append(element.locX)
        print(f"Y position {element.locY}")
        y_terminations.append(element.locY)

    x_bifurcations = []
    y_bifurcations = []

    print("Bifurcations at:")
    for element in FeaturesBifurcations:
        print(f"X position {element.locX}")
        print(f"Y position {element.locY}")
        x_bifurcations.append(element.locX)
        y_bifurcations.append(element.locY)

    print(f"List of feature terminations: {y_terminations, x_terminations}")
    print(f"List of feature bifurcations: {y_bifurcations, x_bifurcations}")
    return skeleton, x_terminations, y_terminations, x_bifurcations, y_bifurcations
    # import matplotlib.pyplot as plt

    # imgplot = plt.imshow(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
    # imgplot = plt.imshow(cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))

    # plt.plot(y_terminations, x_terminations, 'ro')
    # plt.plot(y_bifurcations, x_bifurcations, 'b1')
    # plt.gca().invert_yaxis()
    # plt.show()

    # press space bar to close everything
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
if __name__ == "__main__":
    prepare_and_analyze('het-cam-test.jpg')
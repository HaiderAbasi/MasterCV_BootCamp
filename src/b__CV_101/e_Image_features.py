import cv2
import numpy as np
from loguru import logger

from src.utilities import build_montages,print_h


o_s = 100
def on_overlayS_change(val):
    global o_s
    o_s = val

def img_registration(obj,scene,debug = True):
    #  Hint     : Find Homography will be be critical here. 

    # Write Code here
    obj_reg_on_scene = scene.copy()
    
    
    return obj_reg_on_scene


def assignment(debug = True):
    # Assignment: Orthomosaic is a composite image that is created by stitching together multiple overlapping 
    #             images of an area taken from the same perspective. The images are geometrically corrected so 
    #             that the scale is uniform across the entire image. This process is known as orthorectification.
    #             Here we have an orthomosaic and a distorted image taken by a drone from some part of the area
    #             of which the orthomosaic was generated from. But at some other time.   
    #  Task     : Your task is to use the orthomosaic to correct the distortions in the distorted image and 
    #             overlay it on the orthomosaic.(This will be useful in analyzig the recent changes that had
    #                                             had happened in the area) 
    #
    #  Returns  : (img) drone view mapped on the mosaic using image registration.
    #
    #  Hint     : See Image registration in this regard.
    #             Reference: https://www.mathworks.com/discovery/image-registration.html#:~:text=Image%20registration%20is%20an%20image,are%20common%20when%20overlaying%20images.
    #                        Further read: https://analyticsindiamag.com/what-is-image-registration-and-how-does-it-work/
    print_h("[Assignment]:  Estimate the relative drone pose (utilizing the the drone view with known map using feature detection and mapping)\n")

    # Input
    drone_view = cv2.imread("Data/test\DSC00153.JPG")

    map = cv2.imread("Data/test/building_mosaic.tif")

    if debug:
        cv2.namedWindow("> drone_view < ",cv2.WINDOW_NORMAL)
        cv2.imshow("> drone_view < ",drone_view)
        cv2.waitKey(0)
        cv2.destroyWindow("> drone_view < ")
    
    images = []
    titles = []
    images.append(drone_view)
    titles.append("drone_view")
    

    # Task Function
    img_mapped_on_map = img_registration(drone_view,map,debug)
    
    if (np.array_equal(img_mapped_on_map,map)):
        logger.error("img_registration() needs to be coded to get the required(distorted image registered on the orthomosaic) result.")
        exit(0)


    # Output (Display)
    if debug:
        # Close previously opened windows
        cv2.destroyAllWindows()
        images.append(img_mapped_on_map)
        titles.append("img_mapped_on_map")
        montage = build_montages(images,None,None,titles,True,True)
        for montage_img in montage:
            cv2.imshow("Image-registration",montage_img)
        cv2.waitKey(0)
        
    return img_mapped_on_map



def vis_keypoints(img):
    images = []
    titles = []

    images.append(img)
    titles.append("deans_car")

    # A) Harris Corner detector : The first keypoint detector available in OpencV
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # grayscale and float32 type.
    blockSize = 2 # size of neighbourhood considered for corner detection
    ksize = 7     # Aperture parameter of the Sobel derivative used.
    k = 0.08      # Harris detector free parameter in the equation. 
    # Cornerness = R = det (M) - k * (trace (M))^2
    dst = cv2.cornerHarris(gray,blockSize,ksize,k) # dst [Float_32 size same as src]
    dst = cv2.dilate(dst,None)
    # Threshold for an optimal value, it may vary depending on the image.
    img_harris = img.copy()
    img_harris[dst>0.01*dst.max()]=[0,0,255]

    images.append(img_harris)
    titles.append("Corners (Harris)")

    # B) Shi-Thomsi Corner detector (Important: Improved Harris Corner so better to use this!)
    max_corners = 25   # Maximum numbers of corner you wish to get
    min_quality = 0.01 # Minimum quality required to be considered a valid corner Range (0-1)
    min_euc_dist = 10  # Minimum allowed euc distance between two corners
    corners = cv2.goodFeaturesToTrack(gray,max_corners,min_quality,min_euc_dist) # Returns detected corners (Float)

    img_shi_thomsi = img.copy()
    corners = np.int0(corners) # Convert corners to int for display
    for i in corners:
        x,y = i.ravel() # unpack
        img_shi_thomsi = cv2.circle(img_shi_thomsi,(x,y),8,(255,0,0),-1)
    
    images.append(img_shi_thomsi)
    titles.append("Corners (Shi-Thomsi)")

    # Displaying image and threshold result
    montage = build_montages(images,None,None,titles,True,True)
    for montage_img in montage:
        #imshow("Found Clusters",cluster,cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Keypoints",montage_img)
    cv2.waitKey(0)

def vis_features(img):
    # SURF and SIFT are very robust, and perform well under scale and rotation variances. Affine shifts are a little tricky, but not bad. And FAST is not a descriptor, it is just a (mind-boggling fast!) detector.
    # If you're considering eligibility for real-time tests, then I'm afraid you'll have to trade-off a great deal of performance. SIFT and SURF are not real-time. Others are relatively faster (BRISK should top it, if I recall)
    images = []
    titles = []

    images.append(img)
    titles.append("deans_car")

    
    img_sift = img.copy()
    
    #cv.SIFT_create(nfeatures, nOctaveLayers, contrastThreshold, edgeThreshold, sigma)
    # n features = Number of best features that you wish to retrieve
    # n OctaveLayers = Number of guassian layers in each octave
    # contrast threshold: Part of Keypoint localization: Where we remove low contrast candidates
    # edge threshold: Part of // // Where we remove candidates greater then the threshold
    # sigma : Sigma of guassian applied to input image at OCtave 0
    sift = cv2.SIFT_create()
    
    # detect (InputArray image, std::vector< KeyPoint > &keypoints, InputArray mask=noArray())
    kp  = sift.detect(img,None)
    
    cv2.drawKeypoints(img,kp,img_sift,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS|cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    
    # dcptr, kp_updated = compute(image,KeyPoint)		
    [descriptors, keypoints] = sift.compute(img,kp)
    
    images.append(img_sift)
    titles.append("Sift")

    img_orb = img.copy()
    # Initiate ORB detector
    # scaleFactor	Pyramid decimation ratio
    # nlevels	The number of pyramid levels.
    # nfeatures	The maximum number of features to retain.    
    orb = cv2.ORB_create()
    # find the keypoints and descriptors with ORB
    # kp, desc = detectAndCompute ( image,  mask, keypoints)
    kp1, des1 = orb.detectAndCompute(img,None)
    # draw only keypoints location,not size and orientation
    cv2.drawKeypoints(img, kp1, img_orb, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS|cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    images.append(img_orb)
    titles.append("ORB")

    # Displaying image and threshold result
    montage = build_montages(images,None,None,titles,True,True)
    for montage_img in montage: 
        #imshow("Found Clusters",cluster,cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Features",montage_img)
    cv2.waitKey(0)


def find_obj_inscene(obj,scene,method="sift",debug=True,min_match_count = 15):
    
    images = []
    titles = []
    
    # Extract features
    if method =="orb":
        if debug:
            print("\n> Using ORB for detection and matching")
        orb = cv2.ORB_create()
        # find the keypoints and descriptors with ORB
        kp1, des1 = orb.detectAndCompute(obj,None)
        kp2, des2 = orb.detectAndCompute(scene,None) 
    elif method =="sift":
        if debug:
            print("\n> Using Sift for detection and matching")
        sift = cv2.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(obj,None)
        kp2, des2 = sift.detectAndCompute(scene,None)
    else:
        print(f"Unknown method specified = {method}")
        return

    # Feature Matching
    if method == "orb":
        # create BFMatcher drone_viewect
        # 1) normType =  Normalization method used : Norm_hamming is recommend for Orb feature extractor
        # 2) crossCheck = crosscheck the matches: Set to true If not using Lowe's ratio test.
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # Match descriptors.
        matches = bf.match(des1,des2) # Finds the best match for each desriptor in the feature set
        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)

        # Take first 20 matches.
        good = matches[:20]
            
    elif method == "sift":
        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1,des2,k=2) # Finds the k best matches for each descriptor : Set k = 2 for
                                             #                                                for Lowe ratio test
        # Apply Lowe's ratio test
        good = []
        for m,n in matches:
            if m.distance < 0.75*n.distance:
                good.append(m)


    # Retreiving only matches that are actually part of object in scene
    M = None
    if debug:
        print(len(good))
    MIN_MATCH_COUNT = min_match_count    
    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()
        h,w = obj.shape[0:2]
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        scene = cv2.polylines(scene,[np.int32(dst)],True,255,3, cv2.LINE_AA)
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
        matchesMask = None

    
    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                    singlePointColor = None,
                    matchesMask = matchesMask, # draw only inliers
                    flags = 2)
    matched_img = cv2.drawMatches(obj,kp1,scene,kp2,good,None,**draw_params)
    
    images.append(matched_img)
    titles.append(f"Feature Matching ({method})")
    
    if debug:
        # Displaying image and threshold result
        montage = build_montages(images,None,None,titles,False,True)
        for montage_img in montage:
            method_str = f"({method})"
            cv2.imshow("find_Obj_in_Scene " + method_str.upper(),montage_img)
        cv2.waitKey(0)

    return M


def main():
    print_h("[main]: OpenCV Image feature-extraction and Usage.")

    # Task a : Keypoint Extraction
    print_h("[a]: Extracting and Visualizing keypoints and features of an image.")
    img = cv2.imread("Data\supernatural-impala.jpg")
    
    vis_keypoints(img)
    vis_features(img)
    
    # Application: Finding known object in a scene
    print_h("[b]: Using feature-matching to find obj in scene.")
    obj = cv2.imread("Data\ltp.jpg")
    scene = cv2.imread("Data\scene2.jpg")
    
    find_obj_inscene(obj,scene,"orb")
    
    find_obj_inscene(obj,scene,"sift") 


    cv2.destroyAllWindows()



if __name__ =="__main__":
    i_am_ready = False
    
    if i_am_ready:
        assignment()
    else:    
        main()
import cv2
from src.utilities import imshow,print_h,build_montages
from loguru import logger


def main():
    
    # Task: Learn two important functions in OpenCV [cv2.selectROI, cv2.cvtColor]
    print_h("Learn to important functions in OpenCV --> [cv2.selectROI, cv2.cvtColor]")
    
    # Read an image
    img = cv2.imread("Data/messi5.jpg")
    
    # Display
    imshow("image",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    
    # [Function 1]: cv2.selectROI ( Select ROi manually )
    rect = cv2.selectROI("Select ROI",img)
    x,y,w,h = rect
    if (w==0 or h==0):
        logger.opt(colors=True).error("[ Invalid ROI provided ]\n<green>Solution:</green> <white>Manually specify the ROI in 'Select ROI' window</white>")
        exit(0)

    images = []
    titles = []
    # >  Cropping using the selected ROI
    roi = img[y:y+h,x:x+w]
    images.append(roi)
    titles.append("ROI")
    
    
    # [Function 2]: cv2.cvtColor ( Change colorspaces from to another )

    # > Change color from BGR to gray
    roi_gray = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    images.append(roi_gray)
    titles.append("roi_gray")
    
    images.append(img)
    titles.append("img")
    
    # > change color space of the image
    hls = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    
    images.append(hls[:,:,0])
    titles.append("hue")
    
    images.append(hls[:,:,1])
    titles.append("lit")
    
    images.append(hls[:,:,2])
    titles.append("sat")
    
    # Display montage
    montages = build_montages(images,None,None,titles,True,True)
    for img in montages:
        cv2.imshow("image",img) # Show large image
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    



if __name__ == "__main__":
    main()
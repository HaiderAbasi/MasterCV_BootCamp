import cv2
import numpy as np
import os
from a3_Advanced.utilities import imshow,describe,putText,get_data,debugger,get_fileName,GUI
import time
from random import randint



class multitracker:

    def __init__(self,tracker_type = "CSRT"):
        print("Initialized Object of multitracker class")
        # Create MultiTracker object        
        self.m_tracker = cv2.MultiTracker_create()        
        self.tracker_type = tracker_type

        self.mode = "Detection"
        self.tracked_bboxes = []

        self.Tracked_class = "Unknown"
        self.colors = []        

    def tracker_create(self):
        if self.tracker_type == "MOSSE":
            return(cv2.TrackerMOSSE_create())
        elif self.tracker_type == "KCF":
            return(cv2.TrackerKCF_create())
        if self.tracker_type == "CSRT":
            return(cv2.TrackerCSRT_create())

    def track(self,frame,frame_draw,bboxes=[]):
        
        # 4. Checking if SignTrack Class mode is Tracking If yes Proceed
        if(self.mode == "Tracking"):
            
            # Start timer
            timer = cv2.getTickCount()

            # get updated location of objects in subsequent frames
            success, boxes = self.m_tracker.update(frame)
            if success:
                self.tracked_bboxes = []
                for rct in boxes:
                    #rct = boxes[0]
                    self.tracked_bboxes.append((round(rct[0],1),round(rct[1],1),round(rct[2],1),round(rct[3],1)))
            else:
                print("Tracking Failed")
                
            # Calculate Frames per second (FPS)
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

            # Draw bounding box
            # draw tracked objects
            if success:
                for i, newbox in enumerate(boxes):
                    p1 = (int(newbox[0]), int(newbox[1]))
                    p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                    cv2.rectangle(frame_draw, p1, p2, self.colors[i], 3, 1)
            else:
                self.mode = "Detection"
                # Tracking failure
                cv2.putText(frame_draw, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

        
            # Display FPS on frame
            cv2.putText(frame_draw, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
       
        # 3. If SignTrack is in Detection Mode -> Proceed to intialize tracker
        elif (self.mode == "Detection"):
            # Incase multitracker initialzied previously -> Delete multitracker object + Create new instance
            if (len(self.m_tracker.getObjects())!= 0):
                del self.m_tracker
                self.m_tracker = cv2.MultiTracker_create()            
                self.colors.clear() # Colors would have also been initialized along with the tracker, Clear it!

            # Randomly coloring each bbox
            for i in range(len(bboxes)):
                self.colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))

            # Initialize MultiTracker
            for bbox in bboxes:
                if bbox != (0,0,0,0): # Sane bbox (y)
                    #print("bbox = ", bbox)
                    tracker = self.tracker_create()
                    self.m_tracker.add(tracker, frame, bbox)
                    #self.m_tracker.
                    self.tracked_bboxes = [] # Resetting tracked bboxes
                    self.mode = "Tracking" # Set mode to tracking
                    self.Tracked_class = "Plant" # keep tracking frame sign name


def main():
    gui = GUI()
    # Use CSRT when you need higher object tracking accuracy and can tolerate slower FPS throughput
    # Use KCF when you need faster FPS throughput but can handle slightly lower object tracking accuracy
    # Use MOSSE when you need pure speed
    tracker_type = "CSRT"
    m_tracker = multitracker(tracker_type)

    Friends = "Data/NonFree\Friends\Friends_AllClothes.mp4"
    Megamind = "Data/NonFree/Megamind.avi"
    Window_Name = get_fileName(Megamind)

    vid_dirs,filenames = get_data("multitracking")

    #data_iter = int(input("Please select one from the following:\n"+"\n".join(filenames)+"\n"))
    data_iter = gui.selectdata(filenames)
    Window_Name = filenames[data_iter]

    #debugger = debugger(Window_Name,["data_iter"],[len(filenames)])

    #-- 1. Read the video stream
    cap = cv2.VideoCapture(vid_dirs[data_iter])
    if not cap.isOpened:
        print('--(!)Error opening video capture')
        exit(0)


    while True:
        #debugger.update_variables() # Get updated variables
        #data_iter = debugger.debug_vars[0]

        ret, frame = cap.read()
        
        if frame is None:
            print('--(!) No captured frame -- Break!')
            break
        else:
            frame_disp = frame.copy()
            if m_tracker.mode=="Tracking":
                start_time = time.time()
                m_tracker.track(frame,frame_disp)

                if len(m_tracker.tracked_bboxes)!=0:
                    fps = 1.0 / (time.time() - start_time) if (time.time() - start_time)!=0 else 100.00
                    fps_txt = f"FPS: = {fps:.2f}"
                    putText(frame, f"Tracking ( {tracker_type} ) at {fps_txt}",(20,20))
                else:
                    m_tracker.mode = "Detection" # Reset to Detection
            else:
                putText(frame, f"Detection",(20,20))

            cv2.imshow(Window_Name,frame_disp)
            k = cv2.waitKey(30)
            if k==ord('c'):
                gui.selectROIs(frame)
                bboxes = gui.selected_rois
                # Initliaze Tracker
                m_tracker.track(frame,frame.copy(),bboxes)
            elif k==27:# If Esc Pressed Quit!
                break


if __name__ =="__main__":
    main()
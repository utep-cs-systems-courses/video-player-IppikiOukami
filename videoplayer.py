import cv2
import threading
import queue
import os

lock = threading.Lock()

class pcQueue():
    def __init__(self):
        self.sem = threading.Semaphore(10) # limits queue to only 10 frames
        self.que = queue.Queue()

    def put(self, frame):
        self.sem.acquire()                 # prevent others from accessing 
        lock.acquire()                     # lock the thread 
        self.que.put(frame)                # add a frame to the queue
        lock.release()                     # release the thread

    def get(self):
        self.sem.release()                 # allow access back to the queue
        lock.acquire()                     
        frame = self.que.get()             # get the first element from the queue "pop"
        lock.release()
        return frame

    def isEmpty(self):
        lock.acquire()
        empty = self.que.empty()           # returns true if empty, false otherwise
        lock.release()
        return empty

def convertToGray(producer, consumer, maxFrames):
    count = 0
    while True:
        if proQue.isEmpty(): continue      # Cycle until a frame becomes available
        Frame = producer.get()             # grab unedited frame from producer queue
        if count == maxFrames: break       # at limit, stop conversion
        print(f'Frame {count} of {maxFrames}')
        grayScaleFrame = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY) # convert from color to gray
        consumer.put(grayScaleFrame)       # put converted frame into consumer queue
        count += 1
    print("Grayscale Complete!")

def extractFrames(producer, fileName, maxFrames):
    count = 0
    vidcap = cv2.VideoCapture(fileName)    # file containing video clip to edit
    status, image = vidcap.read()          # read the video 
    while status and count < maxFrames:
        status, jpgImage = cv2.imencode('.jpg',image) # get image from video ('Frame') 
        producer.put(image)                # put image into producer queue
        status, image = vidcap.read()      # prepare next video portion for frame
        print(f'Reading frame {count}/{status}')
        count += 1
    print('Extraction Complete')

def displayFrames(consumer, maxFrames):
    count = 0
    while True:
        if consumer.isEmpty(): continue    # cycle until consumer has a frame
        if count == maxFrames: break       # at limit, stop display
        displayFrame = consumer.get()      # get first frame from consumer queue
        print(f'Displaying frame {count}')
        cv2.imshow('Video', displayFrame)  # show frame onto display
        if cv2.waitKey(1) and 0xFF == ord('q'): break # if q is pressed stop display 
        count += 1
    print('Display Complete!')
    cv2.destroyAllWindows()                # close all windows

proQue = pcQueue()                         # initialize producer
conQue = pcQueue()                         # initialize consumer
fileName = 'clip.mp4'
maxFrames = 9999
extract = threading.Thread(target = extractFrames, args = (proQue,fileName,maxFrames))
convert = threading.Thread(target = convertToGray, args = (proQue, conQue, maxFrames))
display = threading.Thread(target = displayFrames, args = (conQue, maxFrames))

extract.start()
convert.start()
display.start()

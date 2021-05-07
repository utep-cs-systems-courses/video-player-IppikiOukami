import cv2
import threading
import queue
import os

lock = threading.Lock()

class pcQueue():
    def __init__(self):
        self.full = threading.Semaphore(0)   # allows 0 frames of space
        self.empty = threading.Semaphore(10) # allows 10 frames of space
        self.que = queue.Queue()

    def put(self, frame):
        self.empty.acquire()                 # reduce number of available spots from empty (spot filled by enqueue)
        lock.acquire()                       # avoid race condition 
        self.que.put(frame)                  # add a frame to the queue
        lock.release()                       
        self.full.release()                  # increment full (spot has been taken by enqueue)

    def get(self):
        self.full.acquire()                  # remove a spot from full
        lock.acquire()                       # avoid race condition
        frame = self.que.get()               # get the first element from the queue "pop"
        lock.release()
        self.empty.release()                 # add a spot to empty (more spots opened up after dequeue)
        return frame

    def isEmpty(self):
        lock.acquire()                       # avoid race condition
        empty = self.que.empty()             # returns true if empty, false otherwise
        lock.release()
        return empty

def convertToGray(producer, consumer):
    count = 0
    while True:
        if proQue.isEmpty(): continue      # Cycle until a frame becomes available
        else:
            Frame = producer.get()             # grab unedited frame from producer queue
            if Frame is None: break
            print(f'Converted frame #{count}')
            grayScaleFrame = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY) # convert from color to gray
            consumer.put(grayScaleFrame)       # put converted frame into consumer queue
            count += 1
    print("Grayscale Complete!")
    consumer.put(None)

def extractFrames(producer, fileName, maxFrames):
    count = 0
    vidcap = cv2.VideoCapture(fileName)        # file containing video clip to edit
    status, image = vidcap.read()              # read the video 
    while status and count < maxFrames:
        status, jpgImage = cv2.imencode('.jpg',image) # get image from video ('Frame') 
        producer.put(image)                    # put image into producer queue
        status, image = vidcap.read()          # prepare next video portion for frame
        print(f'Extracted frame #{count}')
        count += 1
    print('Extraction Complete!')
    producer.put(None)

# Same pattern of execution should appear not 10 then 1
def displayFrames(consumer):
    count = 0
    while True:
        if consumer.isEmpty(): continue        # cycle until consumer has a frame
        else:
            displayFrame = consumer.get()      # get first frame from consumer queue
            if displayFrame is None: break     # break at None identifier
            print(f'Display frame #{count}')
            cv2.imshow('Video', displayFrame)  # show frame onto display
            if cv2.waitKey(42) and 0xFF == ord('q'): break # if q is pressed stop display 
            count += 1
    cv2.destroyAllWindows()                    # close all windows
    print('Display Complete!')
    
proQue = pcQueue()                             # initialize producer
conQue = pcQueue()                             # initialize consumer
fileName = 'clip.mp4'
maxFrames = 300
extract = threading.Thread(target = extractFrames, args = (proQue,fileName,maxFrames)) # completing
convert = threading.Thread(target = convertToGray, args = (proQue, conQue)) # completing 
display = threading.Thread(target = displayFrames, args = {conQue})

extract.start()
convert.start()
display.start()

import numpy as np
import cv2
import requests
from datetime import datetime
import time
import json

""" 
Caveat Emptor: This doesn't work well. Mostly due to the following:
* It tries to find the pool based on color (ie: blue)
* It needs lab conditions and can't handle fluctations from things like sun glare or water reflection 
"""

base_path = '/src/skimmer-controller/image-'

def logger(message):
       time = datetime.now()
       current_time = time.strftime("%H:%M:%S")
       print("{} - {}".format(current_time,message))

def command_code(command):
        with open('parameters.json', 'r') as myfile:
                data=myfile.read()
        parameters = json.loads(data)
        code = parameters[command]
        return code

def http_request(json):
        logger('Sending HTTP request: {}'.format(json))
        response = requests.post(
                'http://localhost:8080/command/',
                json=json
        )
        logger('Recieved status code: {}'.format(response.status_code))

def send_command(command):
        code = command_code(command)
        logger("Sending command: {} ({})".format(command, code))

        # Prepend the start/stop command (4)
        json=[
                {'frequency': 27.15, 'dead_frequency': 49.83, 'spacing_us': 500, 'burst_us': 1500, 'repeats': 4},
                {'frequency': 27.15, 'dead_frequency': 49.83, 'spacing_us': 500, 'burst_us': 500, 'repeats': code}
        ]
        http_request(json)
        # Sleep until we're ready to send the start/stop command
        time.sleep(2)
        json=[
                {'frequency': 27.15, 'dead_frequency': 49.83, 'spacing_us': 500, 'burst_us': 500, 'repeats': 4}
        ]
        http_request(json)

def process_image():
        logger("Starting")
        # Acquire image
        logger("Acquiring image")
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite('{}{}'.format(base_path, 'original.jpg'), image)

        # Blur the image to difuse and help with line finding
        logger("Blurring image")
        image_blurred = cv2.GaussianBlur(image, (9, 9), 2, 2)
        cv2.imwrite('{}{}'.format(base_path, 'blurred.jpg'), image_blurred)

        # Convert from BGR to HSV - easier color detection
        logger("Converting to HSV")
        image_hsv = cv2.cvtColor(image_blurred, cv2.COLOR_BGR2HSV)
        cv2.imwrite('{}{}'.format(base_path, 'hsv.jpg'), image_hsv)

        # Define color we found using trackbars.py
        # This is the color of our pool, we'll use to mask out the rest of the image
        seek_color = np.uint8([[[200, 100, 0]]])
        hsv_color = cv2.cvtColor(seek_color,cv2.COLOR_BGR2HSV)
        hsv_lower = np.uint8([hsv_color[0][0][0]-10,100,100])
        hsv_upper = np.uint8([hsv_color[0][0][0]+10,255,255])

        # Mask out using hsv values
        logger("Masking")
        image_mask = cv2.inRange(image_hsv, hsv_lower, hsv_upper)
        cv2.imwrite('{}{}'.format(base_path, 'mask.jpg'), image_mask)

        # Use our mask to black out the perimeter of the pool and skimmer
        # Reduces the area we need to contour search
        logger("Bitwise")
        image_bitwise = cv2.bitwise_and(image, image, mask=image_mask)
        cv2.imwrite('{}{}'.format(base_path, 'bitwise.jpg'), image_bitwise)

        # Find all the contours in our image
        logger("Finding contours")
        _, contours, hierarchy = cv2.findContours(image_bitwise, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # Find the pool by iterating through all contours until we find the right size
        logger("Finding pool")
        # Just enough hacky for a POC
        pool_upper = 500000
        pool_lower = 100000
        for index, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > pool_lower and area < pool_upper:
                        # Found the pool, draw it's shape
                        cv2.drawContours(image,[contour],-1, (0,0,255), 3)
                        pool_contour = contour
                        pool_index = index
                        # We're done here
                        break


        # Find our skimmer, it's inside our pool
        logger("Finding skimmer")
        skimmer_upper = 4000
        skimmer_lower = 500
        # Set turn distance to zero in case we can't find the skimmer
        turn_distance = 0
        for index, contour in enumerate(contours):
        # Check if we're inside the pool index
                if hierarchy[0, index, 3] == pool_index:
                        area = cv2.contourArea(contour)
                        # Contour the right size?
                        if area > skimmer_lower and area < skimmer_upper:
                                # compute the center of our skimmer
                                M = cv2.moments(contour)
                                cX = int(M["m10"] / M["m00"])
                                cY = int(M["m01"] / M["m00"])
                                # Measure distance between the center of our skimmer and the pool contour
                                turn_distance = cv2.pointPolygonTest(contours[pool_index], (cX, cY), True)
                                # draw the contour
                                cv2.drawContours(image,[contour],-1, (0,255,0), 3)
                                # draw a circle in the center of the contour
                                cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
                                break

        if turn_distance < 100:
                # we're too close to the wall, turn left
                command = "left"
        else:
                # go straight/forward
                command = "forward"

        logger("Adding direction text and writing final image")
        cv2.putText(image,command,(30,256), cv2.FONT_HERSHEY_SIMPLEX, 2.5,(255,255,255),2,cv2.LINE_AA)
        cv2.imwrite('{}{}'.format(base_path, 'final.jpg'), image)

        return command

def main():
	while True:
            # Acquire image, determine direction, and send the skimmer a command
            send_command(process_image())

main()

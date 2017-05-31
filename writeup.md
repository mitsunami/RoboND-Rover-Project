## Project: Search and Sample Return

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./output/navigable_threshed.png
[image2]: ./output/rock_threshed.png
[image3]: ./output/tukey_biweight.png
[image4]: ./output/tukey_biweight2.png
[image5]: ./output/wheretogo.png

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

This is the Writeup.

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
I use color_thresh function to identify obstacles. RGB threshold is default value (160,160,160).
```python
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select
```
![alt text][image1]

I added a new function to identify golden rocks. Here is the code to do that. This function convert a color from RGB to HSV, and threshold the image to get only required colors by specifying lower and upper threshold value.
```python
# Define a function to perform a color threshold
def color_hsv_thresh(img, lower_thresh=np.array([82,128,128]), upper_thresh=np.array([102,255,255])):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # define range of color in HSV
    # Threshold the HSV image to get only colors
    color_select = cv2.inRange(hsv, lower_thresh, upper_thresh)
    # Return the single-channel binary image
    return color_select
```

To achieve appropriate HSV threshold, I checked target golden rock's RGB color value and configured a range to cover the golden rock's color. Here's the code.
```python
golden = np.uint8([[[186,155,10 ]]])
hsv_golden = cv2.cvtColor(golden,cv2.COLOR_BGR2HSV)
print(hsv_golden)
```
![alt text][image2]

#### 2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
Here's my `process_image()` function. At first, definition of source and destination points for perspective transform is done. The coordinations are extract from four corners of a grid of calibration_image. From those, perspective transformation matrix is calculated, and then, input `img` is transformed by using the matrix.
```python
def process_image(img):
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                      [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                      ])
    # 2) Apply perspective transform
    warped = perspect_transform(img, source, destination)
```

To identify navigable terrain/obstacles/rock samples, thresholding functions are called. Navigable terrain is extracted by calling `color_thresh()` function, which is the same as above. obstacles are region execpt navigable, so the region are calculated by inverse of the navigable terrain. rock samples are extracted `color_hsv_thresh()` function, which is my original function explained above.
```python
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    rgb_thresh=(160, 160, 160)
    navigable_threshed = color_thresh(warped, rgb_thresh)
    obstacle_threshed = 1 - navigable_threshed
    rock_threshed = color_hsv_thresh(warped)

```

Coordinates of each region are converted to rover centric coordinates. And the coordinates are converted to world coordinates based on rover's position, yaw angle. Navigable terrain's coords are colored as blue, obstacles as red and rock samples as green. 
```python
    # 4) Convert thresholded image pixel values to rover-centric coords
    navigable_xpix, navigable_ypix = rover_coords(navigable_threshed)
    obstacle_xpix, obstacle_ypix = rover_coords(obstacle_threshed)
    rock_xpix, rock_ypix = rover_coords(rock_threshed)
    # 5) Convert rover-centric pixel values to world coords
    worldmap = data.worldmap
    scale = 10
    # Get navigable pixel positions in world coords
    rover_xpos = data.xpos[data.count]
    rover_ypos = data.ypos[data.count]
    rover_yaw  = data.yaw[data.count]
    navigable_x_world, navigable_y_world = pix_to_world(navigable_xpix, navigable_ypix, rover_xpos, 
                                    rover_ypos, rover_yaw, 
                                    worldmap.shape[0], scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_xpix, obstacle_ypix, rover_xpos, 
                                    rover_ypos, rover_yaw, 
                                    worldmap.shape[0], scale)
    rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix, rover_xpos, 
                                    rover_ypos, rover_yaw, 
                                    worldmap.shape[0], scale)

    # 6) Update worldmap (to be displayed on right side of screen)
    data.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    data.worldmap[rock_y_world, rock_x_world, :] = 255
    data.worldmap[navigable_y_world, navigable_x_world, 2] += 1
```

Finally, a mosaic image is generated. The process is as-is example code.
```python
    # 7) Make a mosaic image, below is some example code
        # First create a blank image 
    output_image = np.zeros((img.shape[0] + data.worldmap.shape[0], img.shape[1]*2, 3))
        # Next you can populate regions of the image with various output
        # Here I'm putting the original image in the upper left hand corner
    output_image[0:img.shape[0], 0:img.shape[1]] = img

        # Let's create more images to add to the mosaic, first a warped image
    #warped = perspect_transform(img, source, destination)
        # Add the warped image in the upper right hand corner
    output_image[0:img.shape[0], img.shape[1]:] = warped

        # Overlay worldmap with ground truth map
    map_add = cv2.addWeighted(data.worldmap, 1, data.ground_truth, 0.5, 0)
        # Flip map overlay so y-axis points upward and add to output_image 
    output_image[img.shape[0]:, 0:data.worldmap.shape[1]] = np.flipud(map_add)
    
        # Then putting some text over the image
    cv2.putText(output_image,"Populate this image with your analyses to make a video!", (20, 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
    data.count += 1 # Keep track of the index in the Databucket()
    
    return output_image
```

My video output will be included with my submission.

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

Here's `perception_step()` function. The functionality is basically same as `process_image()` function described above except updating Rover's state.
```python
def perception_step(Rover):
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    bottom_offset = 6
        # Define calibration box in source (actual) and destination (desired) coordinates
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])

    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable_threshed = color_thresh(warped, rgb_thresh=(160,160,160))
    obstacle_threshed = np.subtract(255, navigable_threshed)
    rock_threshed = color_hsv_thresh(warped, lower_thresh=np.array([82,128,128]), upper_thresh=np.array([102,255,255]))

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle_threshed
    Rover.vision_image[:,:,1] = rock_threshed
    Rover.vision_image[:,:,2] = navigable_threshed

    # 5) Convert map image pixel values to rover-centric coords
    navigable_xpix, navigable_ypix = rover_coords(navigable_threshed)
    obstacle_xpix, obstacle_ypix = rover_coords(obstacle_threshed)
    rock_xpix, rock_ypix = rover_coords(rock_threshed)

    # 6) Convert rover-centric pixel values to world coordinates
    scale = 10
    rover_xpos = Rover.pos[0]
    rover_ypos = Rover.pos[1]
    rover_yaw  = Rover.yaw
    navigable_x_world, navigable_y_world = pix_to_world(navigable_xpix, navigable_ypix, rover_xpos, 
                                    rover_ypos, rover_yaw, 
                                    Rover.worldmap.shape[0], scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_xpix, obstacle_ypix, rover_xpos, 
                                    rover_ypos, rover_yaw, 
                                    Rover.worldmap.shape[0], scale)
    rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix, rover_xpos, 
                                    rover_ypos, rover_yaw, 
                                    Rover.worldmap.shape[0], scale)
                                    
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(navigable_xpix, navigable_ypix)

    return Rover
```

And `decision_step()` function is below.

```python
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0

                # Set steering to weighted average angle clipped to the range +/- 15
                #### weighted average based on direction
                if Rover.nav_angles.size != 0:
                    #weights = Rover.nav_dists*np.subtract(Rover.nav_angles,Rover.nav_angles.min())
                    weighted_angle = 10 * np.pi /180
                    acceptable_range = 60 * np.pi /180
                    delta = np.abs(np.subtract(Rover.nav_angles, weighted_angle))
                    dir_weights = np.square(np.subtract(1, np.square(np.divide(delta, acceptable_range))))
                    #weights = Rover.nav_dists*dir_weights
                    weights = dir_weights
                else:
                    weights = 1    
                mean_dir = np.sum(Rover.nav_angles*weights)/np.sum(weights) #dist-weighted average
                Rover.steer = np.clip(mean_dir * 180/np.pi, -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover
```
I'll explain about what techniques I used in next section. 

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**
##### My simulator settings are below:
    - Screen resolution: 1280x1024
    - Graphics quality: simple
    - Frames per second: around 20 FPS

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  

Basically, decision tree is not changed from default setting. My method is mainly focusing Rover's steering. To always keep a wall on Rover's left, I used weighted average angle to decide which direction to go, which is also known as M-estimator. Weighting amount is calculated based on Tukey's biweight, which is shown below. In the equation, d is a distance between target angle and each navigable terrain pixel's angle. W is boundary of weighting. In summary, M-estimator does weighting to target angle most, while normal averaging is weighting equally all direction.
![alt text][image3]
Weighting curve is shown here.
![alt text][image4]

. The code is shown below. `weighted_angle` indicates d in the above equation. My setting is ten degree to make Rover to keep a wall on its left. `acceptable_range` indicates W, which is sixty degree. By doing this, Rover tend to go at a direction around 10 degree if possible. Even if not, Rover can still steer to possible direction.
```python
                # Set steering to weighted average angle clipped to the range +/- 15
                #### weighted average based on direction
                if Rover.nav_angles.size != 0:
                    #weights = Rover.nav_dists*np.subtract(Rover.nav_angles,Rover.nav_angles.min())
                    weighted_angle = 10 * np.pi /180
                    acceptable_range = 60 * np.pi /180
                    delta = np.abs(np.subtract(Rover.nav_angles, weighted_angle))
                    dir_weights = np.square(np.subtract(1, np.square(np.divide(delta, acceptable_range))))
                    #weights = Rover.nav_dists*dir_weights
                    weights = dir_weights
                else:
                    weights = 1    
                mean_dir = np.sum(Rover.nav_angles*weights)/np.sum(weights) 
                #dir-weighted average
                Rover.steer = np.clip(mean_dir * 180/np.pi, -15, 15)
```
Actual calculation result is shown below. The figure shows that Rover steers to left wall by using my method.
![alt text][image5]


One additional modification was done. Based on above method, Rover tend to steer to left direction. When Rover is facing dead end, Rover needs to turn around more then defaut setting. Thus I increased threshold to go forward again `go_forward` from five hundred to one thousand.
```python
        self.go_forward = 1000 #default is 500 # Threshold to go forward again
```

I confirmed that the rover map 96.4% of the environment with 60.5% against the ground truth. And, Rover find the location of five rock sample. For futher improvement, I need to handle some probelems like below:
    - Avoidance of rock abstacles by caring Rover's body area.
    - Finding one rock sample hiding in shadow of obstacles by adjusting golden color threshold.
    - Improvement of fidelity by adjusting navigable terrain.
    - Optimizing time by speeding up and ajusting other parameters.
    - Collect samples by ordering `send_pickup()` function



import numpy as np


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
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
            if Rover.rock_angles.size != 0 and np.mean(Rover.rock_angles) > -5 * np.pi /180:
                Rover.steer = np.clip(np.mean(Rover.rock_angles) * 180/np.pi, -15, 15)
                if Rover.near_sample:
                    Rover.mode = 'stop'
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                else:
                    if Rover.vel == 0:
                        # Set throttle value to throttle setting
                        Rover.throttle = Rover.throttle_set
                    else: # Else coast
                        Rover.throttle = 0
                    Rover.brake = 0

            elif len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0

                # Set Rover's steering
                if Rover.nav_angles.size != 0:
                    #### weighted average based on dist and left
                    #weights = Rover.nav_dists*np.subtract(Rover.nav_angles,Rover.nav_angles.min())
                    weighted_angle = 10 * np.pi /180
                    acceptable_range = 45 * np.pi /180
                    delta = np.abs(np.subtract(Rover.nav_angles, weighted_angle))
                    delta = np.minimum(delta, acceptable_range)
                    dir_weights = np.square(np.subtract(1, np.square(np.divide(delta, acceptable_range))))
                    dir_weights = np.add(dir_weights, 0.01)
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
                if Rover.near_sample == 1:
                    if Rover.vel == 0 and not Rover.picking_up:
                        Rover.steer = 0
                        Rover.throttle = 0
                        Rover.brake = 0
                        Rover.send_pickup = True
                    #else:
                    #    Rover.steer = np.clip(np.mean(Rover.rock_angles) * 180/np.pi, -15, 15)
                    #    Rover.throttle = 0
                    #    Rover.brake = Rover.brake_set
                        
                # Now we're stopped and we have vision data to see if there's a path forward
                elif len(Rover.nav_angles) < Rover.go_forward:
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


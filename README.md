# skimmer-drone
Automate pool skimming

## Why?
Pools are fun, but they're so much work. Why not automate some of that work?  

I have a robot that cleans the bottom of my pool, why not have one that cleans the top? 

## Current state
I started to go down the road of building a motorized vessel with a skimmer, but then I found the [Dunn Rite Hydro-Net](https://dunnriteproducts.com/hydro-net/). 

The Hydro-Net worked great as a rc skimmer, but how can I automate it? Ideally I could just turn it on, drop it in the water, and it would start cleaning. 

There's plenty of drone waypoint finder examples out there but I wanted to avoid adding onboard electronics to something constantly exposed to water, and I figured it would be difficult to iterate while maintaining a waterproof solution. How about computer vision with RF? I'd used opencv in a [past project to annoy my kids into putting their dishes in the dishwasher](https://github.com/ericalexanderorg/DishDetector), and I've had some experience working with rf - seemed doable.

First step was to snap some pictures and see if it was viable. I took [18 pictures](https://github.com/ericalexanderorg/skimmer-drone/tree/master/v1/test/images/poc) of the Hydro-Net while it was manually controlled and cleaning the pool. A couple of hours later and I had a working prototype that could detect the pool, where the Hydro-Net was in the pool, and how close it was to the perimeter of the pool. I figured I could turn left if close to the perimeter, or drive straight if not. Time to start working on the rest. 

The rest took a lot longer. 

* Had to get a spare raspberry pi working but I didn't have the right hdmi or usb cables, it was a holiday weekend, and it would be 3 days before I could get the right cables. Yak shaving adventure #1: cable hacking/splicing. 
* Pi up and running, but the camera wasn't working. Yak shaving adventure #2. Traced it down to a bad ribbon cable connection and eventually ended up using a usb webcam. 
* Reverse engineered the Hydro-Net RF controls and found [pi-rc](https://github.com/bskari/pi-rc) to help send the commands.
* Soldered on an antenna connection to the pi

Yak shaving adventures over and I had a working rasbperry pi that could take a picture, determine where the boat was, how close it was to the pool edge, and send a command to either move forward or turn left. Well, it could do it with my [test images](https://github.com/ericalexanderorg/skimmer-drone/tree/master/v1/test/images/poc). Turns out it didn't work so well when it was all up and running. Turns out the camera on my phone is much better than the webcam, and I'd taken test pictures at the ideal time of day when the sun was overhead and there wasn't any reflection on the water. 

At the end of the day this solution isn't viable. Literraly, at the end of the day the lighting is a problem, [too many reflections](https://github.com/ericalexanderorg/skimmer-drone/blob/master/v1/test/images/reflections/image-original.jpg), too many skimmer identification false positives. At other times of the day there's too much sun glare and the code has issues finding the pool. 

This solution needs lab conditions to work. It could potentially work with a better camera and only when the sun is behind the camera, but that doesn't work with my yard. I'd have to mount a camera on a pole, and a intrusive spot to pull it off. 

Didn't work as an autonomous solution but it was possible to remotely drive and skim from the comfort of my AC cooled office while viewing through the webcam. 

## Next steps
I wanted to avoid additional electronics on the Hydro-net but I'm statring to think that's the best solution. It should be relativly easy to add an Arduino with a proximity detector. Onboard opens up options to either continue to control the boat with RF or control the motors directly. 

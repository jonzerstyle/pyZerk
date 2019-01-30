**pyZerk**
===================
Three week project where I attempted to learn python and make my first working game.  Aiming to create a Berserk like game.  

youtube video of some gameplay:

[![berserk like game](https://img.youtube.com/vi/7LbB4dXbi1Q/0.jpg)](https://www.youtube.com/watch?v=7LbB4dXbi1Q "berserk like game uses pygame lib")

<!-- example on how to embed youtube video thumbnail -->
<!-- view youtube webpage source of video search for thumbnail to eventually find video ID -->
<!-- [![Everything Is AWESOME](https://img.youtube.com/vi/StTqXEQ2l-Y/0.jpg)](https://www.youtube.com/watch?v=StTqXEQ2l-Y "Everything Is AWESOME") -->

Recently I found this project on github which is a better clone of berserk: 

https://github.com/flyingthing/PyBerzerk

I would also like to leave credit to an example pygame project which helped immensely dealing 
with object collections and basics of a pygame that I leveraged:

https://sourceforge.net/projects/asteroidsinf/

To new people I would highly encourage hacking the game variables to see what happens:

Hack the number of robots...
globals.py
NUM_OF_ROBOTS = 24

Hack the screen size...
globals.py
SCREENSIZE = (1024, 768)

Hack the number of OTTOs...
main.py
MAX_OTTOS = 2

Hack the gun fire heat... Others....  Change the BMUSIC.ogg to your music...  Use Audacity to converter from mp3 to ogg.

Notice that most robots die because they run directly away from bullets when they are lined up with the bullet trajectory.  Try changing the robot.py code to be smarter about this scenario...  You might invent skynet?  Robots that you can't hit?

Crazy stuff can happen have fun ;)

----------

**REQUIREMENTS:**

install
https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi

then install this and point at previous local installation location
http://pygame.org/ftp/pygame-1.9.2a0.win32-py2.7.msi

then execute run.bat from folder and have fun

left cntrl is fire - hold and use arrows to stand ground and shoot 
otherwise run with cursor

lives are unlimited
as you die levels increase - basically robots move faster too a point and then
game goes back to level zero 

voices were created using a artificial voice program called eSpeak

http://espeak.sourceforge.net/

when you run into a wall or robot - that was me going aghahgahghagh - hahah

Blasting effects were created using SoX - I didn't do anything crazy just used a sine wave or something with varying parameters.  If you have ever put a waveform generator through a speaker you will know what I mean.  It's easy to make simple synth retro type sounds with just a square wave of triangle waveform where you can quickly ramp the frequency.  Sox can generate these waveforms for you.  I used Sox output when I was working on a audio compressor decompressor at work to see how well the compressor handled audio at different frequencies by sweeping the frequency.  I found a null at certain frequencies that are in the voice range that was interesting but not a show stopper apparently unless someone used that tone a great deal while speaking.  I would feed the audio file into the compression algorithm on a computer to evaluate compression and decompression without using actual audio hardware.  Just an example how a simple tool can be used in more things than video games.  How you can learn a great deal by making a game that can apply to engineering jobs and others.

http://sox.sourceforge.net/

fun game to make - not complete - but learned python and a game in 3 weeks not bad 

if you browse src code you will see the basic vector math etc... 

pygame did the collision detection work - and the low level graphics and sound the rest was done
in python by me

https://www.pygame.org/news

Objects were created on the fly using hardcoded vector points
not blipped - less efficient maybe but more old skool hardcore...  I punched in manual
vector points
the robots the players the bullets are all code created versus blipped in bitmaps...

A friend got it running on android just for heck of it (you may notice some artifacts of this in the files) ... its not a good game for a phone but it ran pretty good on a cell phone throughput wise...

Audacity is a great free converter for audio.  I used it to convert a thrown together song I made using Reason in wav to ogg format.

https://www.audacityteam.org/

I used Reason 8.0 it's pretty easy to throw together music that doesn't sound bad with it.  Also, includes many sophisticated tools that I have yet to learn like the vocoder!

[![Reason 8.0](https://img.youtube.com/vi/hl9MNgJAbXc/0.jpg)](https://www.youtube.com/watch?v=hl9MNgJAbXc "Reason 8.0")

Youtube video of in game music played within Reason

[![Blade Runnerish Tune](https://img.youtube.com/vi/neFVcz5PFRA/0.jpg)](https://www.youtube.com/watch?v=neFVcz5PFRA "Blade Runnerish Tune")

----------

**END NOTES:**

I would not use python or any interpreted language for a important application.  One of the huge issues I found while working on this project is that syntax bugs are not found until the code executes that portion of the code.  Your edge case conditions that could be exposed during basic compilation with other languages will go unchecked with a python project.  They will only be found when the edge case occurs in real time.  There are tools to help with this, though ultimately python is not a language that should be used beyond very small projects in my opinion.  

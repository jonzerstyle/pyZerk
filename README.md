**PyZerk**
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

voices were created using a articifial voice program called eSpeak

when you run into a wall or robot - that was me going aghahgahghagh - hahah

blasting effects were created using SoX

fun game to make - not complete - but learned python and a game in 3 weeks not bad 

if you browse src code you will see the basic vector math etc... 

pygame did the collision detection work - and the low level graphics and sound the rest was done
in python by me

Objects were created on the fly using hardcoded vector points
not blipped - less efficient maybe but more old skool hardcore...  I punched in manual
vector points
the robots the players the bullets are all code created versus blipped in bitmaps...

A friend got it running on android just for heck of it (you may notice some artifacts of this in the files) ... its not a good game for a phone but it ran pretty good on a cell phone throughput wise...

Audacity is a great free converter for audio.  I used it to convert a thrown together song I made using Reason in wav to ogg format.

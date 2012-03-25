Hawk and Dove is a simulation of the [Hawk-Dove game](http://en.wikipedia.org/wiki/Hawk-dove#Hawk-Dove) described by John Maynard Smith and George Price in their paper ["The logic of animal conflict."](http://www.nature.com/nature/journal/v246/n5427/abs/246015a0.html) Evolutionary game theory is fascinating. Here is one [good book](http://www.amazon.com/Evolution-Social-Contract-Brian-Skyrms/dp/0521555833) on the subject.

This simulation requires [NumPy](http://numpy.scipy.org/) and [PyGame](http://www.pygame.org/news.html). I wrote it as an exercise to practice object orientation. Instead of simulating each round of the game offscreen, birds bounce around in a Pong-like environment, playing a round of Hawk-Dove when they collide. Here are the controls: 

- [ escape ]: Quit.

- [ h ]: Spawn a new hawk.
- [ d ]: Spawn a new dove.
- [ b ]: Spawn an new bourgeois.

- [ p ]: Print population statistics to the terminal.
- [ q ]: Kill all current birds.

- [ = ]: Raise death threshold.
- [ - ]: Reduce death threshold.
- [ ] ]: Raise replication threshold.
- [ [ ]: Reduce replication threshold.
- [ " ]: Raise game payoff.
- [ ; ]: Reduce game payoff.
- [ / ]: Raise game cost.
- [ . ]: Reduce game cost.

- [ l ]: Enable fitness-based speeds.
- [ k ]: Disable fitness-based speeds.

- [ up arrow ]: Increase game speed.
- [ down arrow ]: Decrease game speed.

- [ z ]: Print current death threshold, replication threshold, game cost, and payoff to the terminal.



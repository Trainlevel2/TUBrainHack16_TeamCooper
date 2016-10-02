# Temple University Brain Hackathon 2016: Team Cooper Union
Sebastien Charles </br>
Darwin Huang </br>
Eric Mendoza-Conner </br>
Zhengqi Xi

<b>9/23/2016-9/25/2016 </b></br>

A project using the Emotiv Insight, after an unsuccessful foray with the openBCI, and some fun times messing around with a Muscle SpikerShield.

The project shown here is capable of classifying for two states, say an up or down state. It does this by taking partially processed data from the Emotiv which represent the various brain waves (alpha, beta, theta, etc). Using these brain wave inputs, it has two "training periods". A user can train for "up", then train for "down" in 1000 sample increments, which would typically take about 20-30 seconds. Afterwards, the user can choose to train more for increased accuracy, or run using these classified states (stored in text files for safekeeping and debugging purposes). When running, a user can either think "up", or "down", as they trained before. While simple, the method of classification was successful in classifying the two states, and could be used to move a cursor up or down, or move a robot forwards or backwards.

 <b>Hackathon Log</b></br>
We all had a fantastic time learning about how hard it is to work with EEGs and the brain. It took us all of Friday to get data out of the openBCI, which was then superimposed with high-frequency, high-amplitude noise (we suspect) that should have been filtered away by the included software. Afterwards, we split into groups. Eric tried to exhaust all possible avenues of approach to resurrect the openBCI and get some good data out of it, trying as well to use it as an EMG with little success. Our conclusion regarding the OpenBCI was that our hardware seemed to be faulty, as it wouldn't lose the noise even after seemingly identical setups as other groups. Darwin built a Muscle SpikerShield and achieved basic functionality of turning a light array on and off in conjunction with muscles tensing, as well as a few other basic functions. Sebastien worked on figuring out how the Emotiv Insight worked and how to connect with it. And Zhengqi advised us all (while attempting to fix his computer).

In the end, the OpenBCI turned out to be cool but non-functional, the Muscle SpikerShield was easy to set up but determined to be unnecessary due to the goal of our participation being to achieve something regarding EEGs, and the Emotiv was finally figured out by Sebastien, and ended up being our tool of choice. We all had fun testing the included Emotiv software (monitoring brain waves and such), and Sebastien spearheaded, and wrote, most of the code that ended up being presented, and committed to this repository (everyone else kind of just advised and debugged). Our EEG ended up classifying up and down well, as mentioned above, and we all concluded that it was a pretty fun, informative time.

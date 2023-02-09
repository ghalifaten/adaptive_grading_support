# Adaptive Grading Support
This repository contains the project Adaptive Grading Support for Persuasive Essays developed in the context of my semester project at ML4ED lab.

## Run
To launch the interface, please follow these instructions:
1. clone the repository 
2. unzip the data folders data/clean/ and data/feedback_prize/
3. install the required libraries: `pip3 install -r requirements.txt`
4. run `python3 graspe-interface/front-end/src/main.py`
5. The teacher interface is available on `localhost:5000` and the student interface on `localhost:5000/submit`

## Next steps
* Implement statistics.
* Make the grading section adjustable to the teachers' needs (add, edit, remove sub-sections for instance).
* Make computation of final grade automatic using the final grade formula feature.
* Cache the models' results to retrieve them faster the second time when a check is activated twice.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.90.2),
    on Mon Jul  2 12:32:24 2018
If you publish work using this script please cite the PsychoPy publications:
    Peirce, JW (2007) PsychoPy - Psychophysics software in Python.
        Journal of Neuroscience Methods, 162(1-2), 8-13.
    Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008

Modified by Taylor Salo, 2024.
"""

import os

from psychopy import core, data, event, gui, logging, visual
from psychopy.constants import FINISHED, NOT_STARTED, STARTED
from psychopy.visual.movies import MovieStim

# Ensure that relative paths start from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Store info about the experiment session
experiment_name = "PAFIN"
experiment_info = {"participant": "", "stimulus": ["Bao", "YFTR"]}

dlg = gui.DlgFromDict(dictionary=experiment_info, title=experiment_name)
if dlg.OK is False:
    core.quit()

experiment_info["date"] = data.getDateStr()  # add a simple timestamp
experiment_info["experiment_name"] = experiment_name
image_file = "Pixar.png"
if experiment_info["stimulus"] == "Bao":
    movie_file = "Bao_Body_with_Fadeout.mp4"
elif experiment_info["stimulus"] == "YFTR":
    movie_file = "YFTR_with_Fadeout.mp4"

# Data file name stem = absolute path + name; later add .psyexp, .csv, etc
filename = os.path.join(
    script_dir,
    "data",
    f'{experiment_info["participant"]}_{experiment_name}_{experiment_info["date"]}',
)

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(
    name=experiment_name,
    version="",
    extraInfo=experiment_info,
    runtimeInfo=None,
    originPath=None,
    savePickle=True,
    saveWideText=True,
    dataFileName=filename,
)
# save a log file for detail verbose info
logFile = logging.LogFile(filename + ".log", level=logging.EXP)
# this outputs to the screen, not a file
logging.console.setLevel(logging.WARNING)


def save_and_quit(experiment, window, filename):
    experiment.saveAsWideText(filename + ".csv")
    experiment.saveAsPickle(filename)
    logging.flush()
    experiment.abort()
    window.close()
    core.quit()


# Start Code - component code to be run before the window creation

# Set up the Window
win = visual.Window(
    size=(1920, 1080),
    fullscr=True,
    screen=0,
    allowGUI=False,
    allowStencil=False,
    monitor=None,
    color=[0, 0, 0],
    colorSpace="rgb",
    blendMode="avg",
    useFBO=True,
)
win.mouseVisible = False

# store frame rate of monitor if we can measure it
experiment_info["frameRate"] = win.getActualFrameRate()

# Initialize components for Routine "trial"
trialClock = core.Clock()
image = visual.ImageStim(
    win=win,
    name="image",
    image=image_file,
    mask=None,
    ori=0,
    pos=(0, 0),
    size=(1920, 1080),
    units="pix",  # added units, changed size from 0.5, 0.5 (ATP)
    color=[1, 1, 1],
    colorSpace="rgb",
    opacity=1,
    flipHoriz=False,
    flipVert=False,
    texRes=128,
    interpolate=True,
    depth=0.0,
)
movie = MovieStim(
    win=win,
    name="movie",
    noAudio=False,
    filename=movie_file,
    ori=0,
    pos=(0, 0),
    opacity=1,
    depth=-1.0,
    size=(1920, 1080),  # size=(1440,900)  # used (1600,900) with Shared PC
)

# Create some handy timers
# to track the time since experiment started
globalClock = core.Clock()

# ------Prepare to start Routine "trial"-------
t = 0
trialClock.reset()  # clock
frameN = -1
continueRoutine = True
# update component parameters for each repeat
# keep track of which components have finished
trialComponents = [image, movie]
for thisComponent in trialComponents:
    if hasattr(thisComponent, "status"):
        thisComponent.status = NOT_STARTED

# -------Start Routine "trial"-------
while continueRoutine:
    # get current time
    t = trialClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)

    if t >= 0.0 and image.status == NOT_STARTED:
        # keep track of start time/frame for later
        image.tStart = t
        image.frameNStart = frameN  # exact frame index
        image.setAutoDraw(True)

    # Changed trigger from "t" key to 5 (TS)
    allKeys = event.getKeys(keyList=["5", "escape"])
    for key in allKeys:
        if image.status == STARTED and key == "5":
            image.setAutoDraw(False)

            movie.tStart = t
            movie.frameNStart = frameN  # exact frame index
            movie.setAutoDraw(True)
            win.flip()

        if key == "escape":
            save_and_quit(thisExp, win, filename)

    if movie.status == FINISHED:
        save_and_quit(thisExp, win, filename)

    # refresh the screen
    # don't flip if this routine is over or we'll get a blank screen
    if continueRoutine:
        win.flip()

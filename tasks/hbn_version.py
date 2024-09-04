#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.83.04),
Wed 08 Feb 2017 11:41:38 AM EST
If you publish work using this script please cite the relevant PsychoPy
publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python.
  Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
  Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008

Modified from https://fcon_1000.projects.nitrc.org/indi/cmi_healthy_brain_network/File/scripts/the_present_withcredits_play_lastrun.py.
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0

import os

from psychopy import visual, core, data, event, logging, gui
from psychopy.constants import STARTED, FINISHED, NOT_STARTED

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
experiment_name = "pixar_short_7"
experiment_info = {"participant": "", "stimulus": ["Bao", "YFTR"]}
dlg = gui.DlgFromDict(dictionary=experiment_info, title=experiment_name)
if dlg.OK is False:
    core.quit()  # user pressed cancel

experiment_info["date"] = data.getDateStr()  # add a simple timestamp
experiment_info["experiment_name"] = experiment_name
if experiment_info["stimulus"] == "Bao":
    movie_file = "Bao.mp4"
    image_file = "Bao.png"
    video_duration = 420.0  # XXX: Fix this
elif experiment_info["stimulus"] == "YFTR":
    movie_file = "YFTR.mp4"
    image_file = "YFTR.png"
    video_duration = 420.0  # XXX: Fix this

# Data file name stem = absolute path + name;
# later add .psyexp, .csv, .log, etc
filename = os.path.join(
    _thisDir,
    "data",
    f"{experiment_info['participant']}_{experiment_name}_{experiment_info['date']}",
)

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(
    name=experiment_name,
    version="",
    extraInfo=experiment_info,
    runtimeInfo=None,
    originPath=_thisDir,
    savePickle=True,
    saveWideText=True,
    dataFileName=filename,
)
# save a log file for detail verbose info
logFile = logging.LogFile(filename + ".log", level=logging.EXP)
logging.console.setLevel(logging.WARNING)

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation

# Setup the Window
win = visual.Window(
    size=(1680, 1050),
    fullscr=True,
    screen=0,
    allowGUI=False,
    allowStencil=False,
    monitor="testMonitor",
    color=[0, 0, 0],
    colorSpace="rgb",
    blendMode="avg",
    useFBO=True,
)
# store frame rate of monitor if we can measure it successfully
experiment_info["frameRate"] = win.getActualFrameRate()
if experiment_info["frameRate"] is not None:
    frameDur = 1.0 / round(experiment_info["frameRate"])
else:
    frameDur = 1.0 / 60.0  # couldn't get a reliable measure so guess

# Initialize components for Routine "trial"
trialClock = core.Clock()
ISI = core.StaticPeriod(win=win, screenHz=experiment_info["frameRate"], name="ISI")
Intro = visual.TextStim(
    win=win,
    ori=0,
    name="Intro",
    text="In this section you will see a movie",
    font="Arial",
    pos=[0, 0],
    height=0.1,
    wrapWidth=None,
    color="Black",
    colorSpace="rgb",
    opacity=1,
    depth=-1.0,
)

# Initialize components for Routine "wait_for_trigger"
wait_for_triggerClock = core.Clock()
TriggerWait = visual.TextStim(
    win=win,
    ori=0,
    name="TriggerWait",
    text="The Movie is about to start",
    font="Arial",
    pos=[0, 0],
    height=0.1,
    wrapWidth=None,
    color="black",
    colorSpace="rgb",
    opacity=1,
    depth=0.0,
)

# Initialize components for Routine "movie_play"
movie_playClock = core.Clock()
movie = visual.MovieStim3(
    win=win,
    name="movie",
    noAudio=False,
    filename=movie_file,
    ori=0,
    pos=[0, 0],
    opacity=1,
    size=[1000, 600],
    depth=0.0,
)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()

# ------Prepare to start Routine "trial"-------
t = 0
trialClock.reset()  # clock
frameN = -1
routineTimer.add(3.000000)  # XXX: What is this for?
# update component parameters for each repeat
# keep track of which components have finished
trialComponents = []
trialComponents.append(ISI)
trialComponents.append(Intro)
for thisComponent in trialComponents:
    if hasattr(thisComponent, "status"):
        thisComponent.status = NOT_STARTED

# -------Start Routine "trial"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = trialClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *Intro* updates
    if t >= 0.0 and Intro.status == NOT_STARTED:
        # keep track of start time/frame for later
        Intro.tStart = t  # underestimates by a little under one frame
        Intro.frameNStart = frameN  # exact frame index
        Intro.setAutoDraw(True)

    # most of one frame period left
    if Intro.status == STARTED and t >= (0.0 + (3.0 - win.monitorFramePeriod * 0.75)):
        Intro.setAutoDraw(False)

    # *ISI* period
    if t >= 0.0 and ISI.status == NOT_STARTED:
        # keep track of start time/frame for later
        ISI.tStart = t  # underestimates by a little under one frame
        ISI.frameNStart = frameN  # exact frame index
        ISI.start(3.0)
    # one frame should pass before updating params and completing
    elif ISI.status == STARTED:
        ISI.complete()  # finish the static period

    # check if all components have finished
    if not continueRoutine:
        break

    continueRoutine = False
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()

    # refresh the screen
    if continueRoutine:
        win.flip()

# -------Ending Routine "trial"-------
for thisComponent in trialComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "wait_for_trigger"-------
t = 0
wait_for_triggerClock.reset()  # clock
frameN = -1
# update component parameters for each repeat
key_resp_2 = event.BuilderKeyResponse()  # create an object of type KeyResponse
key_resp_2.status = NOT_STARTED
# keep track of which components have finished
wait_for_triggerComponents = []
wait_for_triggerComponents.append(TriggerWait)
wait_for_triggerComponents.append(key_resp_2)
for thisComponent in wait_for_triggerComponents:
    if hasattr(thisComponent, "status"):
        thisComponent.status = NOT_STARTED

# -------Start Routine "wait_for_trigger"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = wait_for_triggerClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *TriggerWait* updates
    if t >= 0.0 and TriggerWait.status == NOT_STARTED:
        # keep track of start time/frame for later
        TriggerWait.tStart = t  # underestimates by a little under one frame
        TriggerWait.frameNStart = frameN  # exact frame index
        TriggerWait.setAutoDraw(True)

    # *key_resp_2* updates
    if t >= 0.0 and key_resp_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_2.tStart = t  # underestimates by a little under one frame
        key_resp_2.frameNStart = frameN  # exact frame index
        key_resp_2.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType="keyboard")

    if key_resp_2.status == STARTED:
        theseKeys = event.getKeys(keyList=["5"])

        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True

        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_2.keys.extend(theseKeys)  # storing all keys
            key_resp_2.rt.append(key_resp_2.clock.getTime())
            # a response ends the routine
            continueRoutine = False

    # check if all components have finished
    if not continueRoutine:
        break

    continueRoutine = False
    for thisComponent in wait_for_triggerComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()

    # refresh the screen
    if continueRoutine:
        win.flip()

# -------Ending Routine "wait_for_trigger"-------
for thisComponent in wait_for_triggerComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# check responses
if key_resp_2.keys in ["", [], None]:  # No response was made
    key_resp_2.keys = None

# store data for thisExp (ExperimentHandler)
thisExp.addData("key_resp_2.keys", key_resp_2.keys)
if key_resp_2.keys is not None:  # we had a response
    thisExp.addData("key_resp_2.rt", key_resp_2.rt)

thisExp.nextEntry()
# the Routine "wait_for_trigger" was not non-slip safe,
# so reset the non-slip timer
routineTimer.reset()

# ------Prepare to start Routine "movie_play"-------
t = 0
movie_playClock.reset()  # clock
frameN = -1
routineTimer.add(video_duration)
# update component parameters for each repeat
# keep track of which components have finished
movie_playComponents = []
movie_playComponents.append(movie)
for thisComponent in movie_playComponents:
    if hasattr(thisComponent, "status"):
        thisComponent.status = NOT_STARTED

# -------Start Routine "movie_play"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = movie_playClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *movie* updates
    if t >= 0.0 and movie.status == NOT_STARTED:
        # keep track of start time/frame for later
        movie.tStart = t  # underestimates by a little under one frame
        movie.frameNStart = frameN  # exact frame index
        movie.setAutoDraw(True)

    if movie.status == STARTED and (
        t >= (0.0 + (video_duration - (win.monitorFramePeriod * 0.75)))
    ):
        movie.setAutoDraw(False)

    if movie.status == FINISHED:  # force-end the routine
        continueRoutine = False

    # check if all components have finished
    if not continueRoutine:
        break

    continueRoutine = False
    for thisComponent in movie_playComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()

    # refresh the screen
    if continueRoutine:
        win.flip()

# -------Ending Routine "movie_play"-------
for thisComponent in movie_playComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(filename + ".csv")
thisExp.saveAsPickle(filename)
logging.flush()

# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()

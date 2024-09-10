#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run a film-viewing task with PsychoPy.

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
import time

from psychopy import core, data, event, gui, logging, visual
from psychopy.constants import STARTED, STOPPED
from psychopy.visual.movies import MovieStim

# Ensure that relative paths start from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Store info about the experiment session
experiment_name = "PAFIN"
experiment_info = {"participant": "01", "stimulus": ["TEST", "Bao", "YFTR"]}

dlg = gui.DlgFromDict(dictionary=experiment_info, title=experiment_name)
if dlg.OK is False:
    core.quit()

experiment_info["date"] = data.getDateStr()  # add a simple timestamp
experiment_info["experiment_name"] = experiment_name
if experiment_info["stimulus"] == "Bao":
    movie_file = "Bao_Body_with_Fadeout.mp4"
elif experiment_info["stimulus"] == "YFTR":
    movie_file = "YFTR_with_Fadeout.mp4"
else:
    movie_file = "YFTR_test.mp4"

# Data file name stem = absolute path + name; later add .psyexp, .csv, etc
filename = os.path.join(
    script_dir,
    "data",
    (
        f"sub-{experiment_info['participant']}_"
        f"task-{experiment_info['stimulus']}_events"
    ),
)

# An ExperimentHandler isn't essential but helps with data saving
this_experiment = data.ExperimentHandler(
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
log_file = logging.LogFile(filename + ".log", level=logging.EXP)
# this outputs to the screen, not a file
logging.console.setLevel(logging.WARNING)


def save_and_quit(experiment, window, filename):
    """Save the experiment data and close the window."""
    experiment.saveAsWideText(filename + ".csv")
    experiment.saveAsPickle(filename)
    logging.flush()
    experiment.abort()
    window.close()
    core.quit()


def draw_until_keypress(win, stim, continueKeys=["5"]):
    """Draw a stimulus until a key is pressed."""
    response = event.BuilderKeyResponse()
    win.callOnFlip(response.clock.reset)
    event.clearEvents(eventType="keyboard")
    while True:
        if isinstance(stim, list):
            for s in stim:
                s.draw()
        else:
            stim.draw()
        keys = event.getKeys(keyList=continueKeys)
        if any([ck in keys for ck in continueKeys]):
            return

        if "escape" in event.getKeys():
            win.close()
            core.quit()

        win.flip()


def draw(win, stim, duration, clock):
    """Draw stimulus for a given duration.

    Parameters
    ----------
    win : (visual.Window)
    stim : object with `.draw()` method
    duration : (numeric) duration in seconds to display the stimulus
    """
    # Use a busy loop instead of sleeping so we can exit early if need be.
    start_time = time.time()
    response = event.BuilderKeyResponse()
    response.tStart = start_time
    response.frameNStart = 0
    response.status = STARTED
    win.callOnFlip(response.clock.reset)
    event.clearEvents(eventType="keyboard")
    while time.time() - start_time < duration:
        stim.draw()
        keys = event.getKeys(
            keyList=["1", "2", "escape"],
            timeStamped=clock,
        )
        if "escape" in keys:
            save_and_quit(this_experiment, win, filename)
        elif keys:
            response.keys.extend(keys)
            response.rt.append(response.clock.getTime())

        win.flip()
    response.status = STOPPED
    return response.keys, response.rt


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
# experiment_info["frameRate"] = win.getActualFrameRate()

# Initialize components for the task
trial_clock = core.Clock()
waiting = visual.TextStim(
    win,
    """\
You are about to watch a video.
Please keep your eyes open.""",
    name="instructions",
    color="white",
)
end_screen = visual.TextStim(
    win,
    "The task is now complete.",
    name="end_screen",
    color="white",
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
    units="pix",
    size=(1440, 810),
    volume=0.0,
)

# Show message until scan starts ('5' key)
draw_until_keypress(win=win, stim=waiting)

# Start the video
trial_clock.reset()  # clock for the movie
continue_routine = True
this_experiment.addData("trial_type", "film")
this_experiment.addData("onset", trial_clock.getTime())

# NOTE: I set volume to 0 at initialization because I was
# getting a small blip of sound between the "framerate check" and
# the wait screen.
movie.volume = 1.0
movie.setAutoDraw(True)
win.flip()
while continue_routine:
    if "escape" in event.getKeys():
        this_experiment.addData("duration", trial_clock.getTime())
        this_experiment.addData("resp.key", "escape")
        save_and_quit(this_experiment, win, filename)

    if movie.isFinished:
        movie.setAutoDraw(False)
        this_experiment.addData("duration", trial_clock.getTime())
        continue_routine = False

    # refresh the screen
    win.flip()

# Final note that task is over. Runs after scan ends.
curr_time = trial_clock.getTime()
this_experiment.nextEntry()
this_experiment.addData("trial_type", "end_screen")
this_experiment.addData("onset", curr_time)
draw(win=win, stim=end_screen, duration=2, clock=trial_clock)
this_experiment.addData("duration", trial_clock.getTime() - curr_time)
win.flip()

# Task is over. Close everything.
logging.flush()
win.close()
core.quit()

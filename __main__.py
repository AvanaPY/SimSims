import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

from simsims import SimSims

SAVE_DIRECTORY = './saves'

DIMS = (1200, 800)

sims = SimSims(DIMS, save_dir=SAVE_DIRECTORY)
sims.start()

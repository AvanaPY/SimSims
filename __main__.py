import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


from simsims import SimsSims


DIMS = (1200, 800)

sims = SimsSims(DIMS)
sims.start()

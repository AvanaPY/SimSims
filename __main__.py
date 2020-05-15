import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


from sim_assets import SimsSims


DIMS = (1200, 800)

sims = SimsSims(DIMS)
sims.start()

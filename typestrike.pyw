# Double-click launcher for Windows (runs the game without a console window).
import os, runpy
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'typestrike.py'), run_name='__main__')

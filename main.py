import argparse
import os

from lane_finder import LaneFinder

# Parse arguments
parser = argparse.ArgumentParser(description='Input parameters parser')
parser.add_argument('-input', type=str, help='path of input picture or video', default=None)
parser.add_argument('-output', type=str, help='path of output picture or video', default=None)
parser.add_argument('-calibration_path', type=str, help='path to folder with calibration chessboard images', default=None)
parser.add_argument('-multiview', action='store_true', default=False)
parser.add_argument('-ff', type=int, default=0, help='Frame from')
parser.add_argument('-ft', type=int, default=1000000, help='Frame to')
args = parser.parse_args()

# Parameters logic
mode = None
video_ext = ['mp4']
image_ext = ['jpg']

if args.input.split('.')[-1] in video_ext and args.output.split('.')[-1] in video_ext:
    mode = "video"

if args.input.split('.')[-1] in image_ext and args.output.split('.')[-1] in image_ext:
    mode = "image"

# Call proper method
if mode == "video" or mode == "image":
    lane_finder = LaneFinder(args.input, args.output, args.calibration_path, mode, args.multiview, args.ff, args.ft)
    lane_finder.process()
    print("DONE.")
else:
    print("Unknown mode.")
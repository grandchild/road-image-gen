#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from sys import platform
try:
    from subprocess import run
except ImportError:  # python 3.4 or less
    from subprocess import call as run  # return value is not the same!
from grounds.textures import cobblestone_ground_textures, slate_ground_textures, asphalt_ground_textures
from util.config import write_config, remove_config
from util.output_suppressor import OutputSuppressor
from util.progress_bar import progress_bar, progress_bar_clear, PROGRESS_VERTICAL


# stuff that get's displayed with --help/-h
DESCRIPTION = '''\
create stereoskopic test images for neural network training
'''
FOOTER = '''\
part of the project "Stereoscopic image processing with
Convolutional Neural Networks", WS 17/18 @ TU Berlin.
authors: Jonas Massmann, Asis Karojan, Jakob Karge;
supervisor: Hauke Brunken
'''

project_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
if platform == 'win32':  # Windows blender install dir \ blender.exe
    # Asis
    blender_default = r'C:\Users\Karojan\Desktop\blender-2.79-windows64\blender.exe'
    # blender_default = r'C:\Program Files\blender-2.79-windows64\blender.exe'
elif platform == 'darwin':  #
    # Jonas
    blender_default = '/Volumes/EXTERNAL/Programme/Blender/blender.app/Contents/MacOS/blender'
    # blender_default = 'blender.app/Contents/MacOS/blender'
else:  # Blender binary is in Path (Linux)
    blender_default = 'blender'


def cli(*argv):
    '''
    CLI for Image Generator. Run `./image_generator.py -h` to show help.
    
    See also the `user's manual`_.
    
    .. _user's manual:
        user_manual.html
    '''
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=FOOTER,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        # formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Main options
    parser.add_argument('-n', '--number',      default=1,               type=uint,                                   help='number of output images')
    parser.add_argument('-r', '--resolution',  default='960x540',       type=parse_resolution,                       help='[width]x[height] of the output images')
    parser.add_argument('-o', '--output',      default='output',        type=str,                                    help='output path for images (will be created if non-existing)')
    # parser.add_argument('-t', '--type',        default='depth',         choices=['depth', 'displacement'],           help='depth data type')
    parser.add_argument('-g', '--ground-type', default='asphalt',       choices=['cobblestone', 'asphalt', 'slate'], help='ground style')
    parser.add_argument('-d', '--defects',     default=0,               type=uint,                                   help='number of road defects')
    parser.add_argument('-D', '--depth-range', default='16bit',         choices=['8bit', '16bit'],                   help='depth output pixel bit depth')
    
    # Camera options
    parser.add_argument('--camera-distance',   default=20.0,            type=float,                                  help='horizontal camera distance (in cm)')
    parser.add_argument('--camera-pitch',      default=12.5,            type=float,                                  help='camera pitch downward (in deg)')
    parser.add_argument('--camera-height',     default=125.0,           type=float,                                  help='vertical camera distance (in cm)')
    parser.add_argument('--camera-inward-yaw', default=0.0,             type=float,                                  help='camera rotation towards each other (in deg, 0° to 15° makes sense, depending on --camera-distance)')
    
    # Setup options
    parser.add_argument('-p', '--project',     default=project_path,      help='path to project directory')
    parser.add_argument('-b', '--blenderpath', default=blender_default,   help='path to blender executable')
    parser.add_argument('-f', '--foreground',  action='store_true',       help='show blender UI')
    parser.add_argument('-v', '--verbose',     default=0, action='count', help='increase output verbosity level')
    parser.add_argument('-q', '--quiet',       action='store_true',       help='don\'t print any output')
    
    args = parser.parse_args(argv[1:])
    
    # Select config keys to pass to main.py
    ## NOTE: All '-'s become '_'s in the config object!
    config_keys = [
        'number',
        'resolution',
        'output',
        'depth-range',
        'ground-type',
        'defects',
        'camera-distance',
        'camera-height',
        'camera-pitch',
        'camera-inward-yaw',
        'verbose',
    ]
    
    blender_options = [
        '' if args.foreground else '--background',
        # '-noaudio',
    ]
    
    # run blender script
    command = [args.blenderpath] + blender_options + ['--python', os.path.join(args.project, 'main.py')]
    if args.verbose > 0:
        print(command)
    try:
        for  i in range(args.number):
            if args.verbose == 0 and not args.quiet:
                progress_bar(i, args.number, style=PROGRESS_VERTICAL)
            write_config(args, config_keys, args.project, image_index=i)
            if args.verbose > 0:
                print('generating ground textures')
                ground_textures(args.output, args.ground_type, args.defects)
                run(command)
            else:
                ground_textures(args.output, args.ground_type, args.defects)
                progress_bar(i+0.15, args.number, style=PROGRESS_VERTICAL)
                with OutputSuppressor():
                    run(command)
        if args.verbose == 0 and not args.quiet:
            progress_bar(args.number, args.number, style=PROGRESS_VERTICAL)
            print()
    except FileNotFoundError as fnfe:
        progress_bar_clear()
        if args.blenderpath in str(fnfe):
            print('Cannot locate Blender in "{}", set with --blenderpath option.'.format(
                args.blenderpath
            ), file=sys.stderr)
        else:
            print(fnfe, file=sys.stderr)
    except KeyboardInterrupt:
        progress_bar_clear()
        print('Aborted')
    # remove_config()


def ground_textures(output, ground_type, defects=0):
    texture_output = os.path.join(output, 'road_textures')
    if ground_type == 'cobblestone':
        cobblestone_ground_textures(defects=defects, output_path=texture_output)
    elif ground_type == 'asphalt':
        asphalt_ground_textures(defects=defects, output_path=texture_output)
    elif ground_type == 'slate':
        slate_ground_textures(defects=defects, output_path=texture_output)
    else:
        raise ValueError('Unknown ground type {}'.format(ground_type))



def uint(number):
    '''
    Checks if the number is integer and positive.
    
    Returns:
        int: A positive integer or 0.
    
    Raises:
        argparse.ArgumentTypeError: on invalid input.
    '''
    try:
        number = int(number)
    except ValueError:
        raise argparse.ArgumentTypeError('"{}" is not an integer'.format(number))
    if number < 0:
        raise argparse.ArgumentTypeError('Negative numbers are not allowed.')
    return int(number)

def parse_resolution(resolution):
    '''
    Parses a resolution string with a separating 'x'.
    
    Returns:
        (int, int): Width & height.
    
    Raises:
        argparse.ArgumentTypeError: on invalid input.
    '''
    res_parts = resolution.split('x')
    if len(res_parts) != 2:  # Too many or too few 'x's
        raise argparse.ArgumentTypeError('"{}" is not a valid resolution. Format: [width]x[height].'.format(resolution))
    try:
        width, height = int(res_parts[0]), int(res_parts[1])
    except ValueError as err:  # Not an integer on either side
        raise argparse.ArgumentTypeError('"{}" is not a valid resolution ({} is invalid)'.format(resolution, str(err).split(': ', 1)[1]))
    return width, height


if __name__ == '__main__':
    cli(*sys.argv)

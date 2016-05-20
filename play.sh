#!/usr/bin/env bash

snapshot=$1
full=${1##*/}
game=${full%%_*}
rom="roms/$game.bin"
shift

python src/main.py --play_games 1 --display_screen true --replay_size 0 --load_weights $snapshot $rom $*

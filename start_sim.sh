#!/bin/bash
# start_sim.sh - Launch Reachy Mini simulation daemon in the background
# Usage: ./start_sim.sh

echo "Starting Reachy Mini Simulation Daemon..."
# Launching with --sim and --no-media as requested
reachy-mini-daemon --sim --scene minimal --no-media &

echo "Simulation daemon is starting in the background."
echo "You can now run your control scripts (e.g., python test_reachy.py)."

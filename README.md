# Reachy Mini Simulation & Development Environment

This project sets up the local development and simulation environment for the **Reachy Mini** robot by Pollen Robotics.

## 1. Setup

### Dependencies
The following dependencies have been installed:
- **Python 3.10+**: Core runtime.
- **Git & Git LFS**: For model assets and SDK versioning.
- **reachy-mini[mujoco,dev]**: The core SDK with MuJoCo simulation support.

### Virtual Environment
A virtual environment has been created in the `venv/` directory.

## 2. Running the Simulation

The simulation requires a background daemon to act as a bridge between your control code and the virtual robot.

### Using Bash (recommended for Git Bash/WSL):
```bash
# Make the script executable
chmod +x start_sim.sh

# Start the daemon in the background
./start_sim.sh
```

### Using PowerShell (Native Windows):
```powershell
# Activate the virtual environment
.\venv\Scripts\activate

# Start the daemon
.\venv\Scripts\reachy-mini-daemon --sim --scene minimal --no-media
```

## 3. Running the Control Script

Once the simulation daemon is running, you can execute the test script to verify connectivity and control.

```bash
# Activate venv if not already done
# bash: source venv/Scripts/activate
# powershell: .\venv\Scripts\activate

python test_reachy.py
```

### What `test_reachy.py` does:
1. **Connects** to the Reachy Mini simulation SDK.
2. **Moves the Head** to a neutral "look forward" position (6-DOF control).
3. **Animates Antennas** with a wiggle sequence to verify responsiveness.
4. **Prints Joint States** including the 6-DOF head pose and antenna positions to the console.

## 4. Documentation & References
- [Reachy Mini Documentation](https://pollen-robotics.com/docs/reachy-mini/)
- [GitHub: Pollen Robotics - Reachy Mini SDK](https://github.com/pollen-robotics/reachy-mini)

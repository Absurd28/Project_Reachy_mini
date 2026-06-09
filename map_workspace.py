import os

def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

def map_workspace():
    root_dir = "."
    categories = {
        "HCI & Application Logic (Root Scripts)": [
            "interactive_reachy.py",
            "test_reachy.py",
            "patient_tracker.py",
            "webcam_tracker.py",
            "PROJECT_SUMMARY.md",
            "PROJECT_DETAILS.txt",
            "README.md",
            "start_sim.sh"
        ],
        "Physics Simulation & Assets": "venv/Lib/site-packages/reachy_mini/assets",
        "Kinematics & Control Core": "venv/Lib/site-packages/reachy_mini/kinematics",
        "Execution Daemons & IO": "venv/Lib/site-packages/reachy_mini/daemon",
        "Peripheral SDK Modules (Tools, Utils, IO)": [
            "venv/Lib/site-packages/reachy_mini/tools",
            "venv/Lib/site-packages/reachy_mini/utils",
            "venv/Lib/site-packages/reachy_mini/io"
        ],
        "Dependency Noise (Virtual Environment)": "venv",
        "Source Control (Git History)": ".git"
    }

    print("REACHY MINI WORKSPACE ARCHITECTURE - FILE DISTRIBUTION")
    print("=====================================================")
    
    total_accounted = 0
    
    for cat, paths in categories.items():
        cat_count = 0
        if isinstance(paths, list):
            for path in paths:
                full_path = os.path.join(root_dir, path)
                if os.path.isdir(full_path):
                    cat_count += count_files(full_path)
                elif os.path.isfile(full_path):
                    cat_count += 1
        else:
            full_path = os.path.join(root_dir, paths)
            if os.path.isdir(full_path):
                cat_count = count_files(full_path)
            elif os.path.isfile(full_path):
                cat_count = 1
        
        print(f"{cat:<50}: {cat_count:>6} items")
        
        # Avoid double counting venv subfolders if we are just summing everything
        if cat != "Dependency Noise (Virtual Environment)":
             total_accounted += cat_count

    # Total files in root for sanity check
    total_files = count_files(root_dir)
    print("-----------------------------------------------------")
    print(f"{'TOTAL WORKSPACE ITEMS (Sanity Check)':<50}: {total_files:>6} items")

if __name__ == "__main__":
    map_workspace()

# ME 323 Course Project: Robotic Micromilling & Laser Scanning

This repository contains the code used for the data acquisition and motion control system in our project: **"Post-Processing of Additively Manufactured Components via Robotic Micromilling and Laser Scanning"**.

## File Descriptions

* **`me323_project_copy_20251121161339.ino`**
    * **Purpose:** Arduino firmware to control the stepper motor driven linear stage.
    * **Functionality:** Interprets serial commands (direction, distance, speed) to move the workpiece under the laser scanner.

* **`full_profiles_realtime_with_csv.py`**
    * **Purpose:** Main data acquisition script.
    * **Functionality:** Interfaces with the Micro-Epsilon scanControl scanner via Ethernet to capture profiles in real-time and save raw X/Z data to CSV.

* **`process_csv_add_y.py`**
    * **Purpose:** Post-processing script.
    * **Functionality:** Reads the raw CSV data, calculates Y-coordinates based on scan speed/distance, and exports a `.ply` point cloud file for analysis in CloudCompare.

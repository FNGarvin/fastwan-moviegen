# nodes.py - A custom node for ComfyUI to run a bunch of test prompts using FastWan
# it is intended that one run the provisioning script first to download all the models.
#
# Author: FNGarvin
# License: CC BY-NC 4.0
# Date: 2025-08-22
# Description: This node serves as a user-friendly wrapper for the external
#              moviegen_logic.py script, allowing it to be executed from
#              within the ComfyUI interface.

import subprocess
import os
import sys
from folder_paths import get_output_directory

class MovieGenBatchRunner:
    """
    A node that launches the MovieGen batch processing script as an external process.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompts_file_path": ("STRING", {"default": "MovieGenVideobench.txt"}),
                "concat_only": ("BOOLEAN", {"default": False, "label": "Concatenate existing videos only?"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_message",)
    FUNCTION = "run"
    CATEGORY = "MovieGen"
    
    DESCRIPTION = "Runs the MovieGen batch script to generate or concatenate videos."

    def run(self, prompts_file_path, concat_only):
        """
        Executes the external moviegen_logic.py script as a non-blocking process.
        """
        node_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(node_dir, "moviegen_logic.py")

        output_dir = get_output_directory()
        
        full_prompts_path = os.path.join(node_dir, prompts_file_path)

        # Build the command for the dry run check
        check_command = [
            "python", script_path,
            "--prompts-file", full_prompts_path,
            "--output-dir", output_dir,
            "--dry-run",
        ]

        # Run the dry run check in a blocking manner
        print(f"Executing dry run check: {' '.join(check_command)}")
        check_process = subprocess.run(check_command, capture_output=True, text=True)

        if check_process.returncode != 0:
            error_message = f"Dry run failed with exit code {check_process.returncode}."
            print(f"Dry run failed: {check_process.stdout}\n{check_process.stderr}", file=sys.stderr)
            return (error_message,)

        # Build the command for the main run
        command = [
            "python", script_path,
            "--prompts-file", full_prompts_path,
            "--output-dir", output_dir,
        ]
        
        if concat_only:
            command.append("--concat")

        print(f"Executing MovieGen script: {' '.join(command)}")

        if concat_only:
            # Run in blocking mode and capture output for the console
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode == 0:
                print(f"Concatenation completed successfully. Output:\n{process.stdout}")
                return ("Concatenation completed successfully.",)
            else:
                print(f"Concatenation failed. Output:\n{process.stderr}", file=sys.stderr)
                return (f"Error: Concatenation failed with exit code {process.returncode}.",)
        else:
            # Run in non-blocking mode and return immediately
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return ("Batch process launched successfully.",)

#END OF nodes.py

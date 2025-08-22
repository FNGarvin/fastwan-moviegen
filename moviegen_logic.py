#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# moviegen_bench.py - A script to batch process a ComfyUI workflow via API.
#
# Author: FNGarvin
# License: MIT
# Date: 2025-08-22

import json
import requests
import time
import sys
import os
import re
import argparse
import subprocess

# --- SCRIPT CONFIGURATION ---
WORKFLOW_FILE = 'MovieGen-API.json'
PROMPT_NODE_ID = '6'
PROMPT_INPUT_NAME = 'text'
FILENAME_PREFIX = 'Bench'
FINAL_OUTPUT_FILENAME = 'MovieGenBench.FastWan5b.mp4'

# --- SCRIPT LOGIC ---
def get_video_duration(video_path):
    """
    Uses ffprobe to get the duration of a video in seconds.
    Assumes ffprobe is in your system's PATH.
    """
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return float(result.stdout)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error getting duration for {video_path}: {e}", file=sys.stderr)
        return 0

def find_last_completed_index(output_dir, filename_prefix):
    """Finds the number of the last successfully generated video."""
    if not os.path.exists(output_dir):
        return 0

    files = os.listdir(output_dir)
    pattern = re.compile(f'^{filename_prefix}_(\d{5,})_.*\.mp4$')
    
    last_index = 0
    for file in files:
        match = pattern.match(file)
        if match:
            index = int(match.group(1))
            if index > last_index:
                last_index = index
    
    return last_index 

def get_queue_length(api_url):
    """
    Gets the current number of running and pending jobs in the queue.
    """
    try:
        response = requests.get(f"{api_url}/prompt")
        response.raise_for_status()
        data = response.json()
        running = len(data.get('queue_running', []))
        pending = len(data.get('queue_pending', []))
        return running + pending
    except requests.exceptions.RequestException as e:
        print(f"Error checking queue status: {e}", file=sys.stderr)
        return -1

def concatenate_videos(prompts_to_generate, output_dir, output_filename=FINAL_OUTPUT_FILENAME):
    """
    Creates the concat and chapter files and runs ffmpeg.
    """
    print("Preparing videos for concatenation...")
    
    if not os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' not found.", file=sys.stderr)
        return 1

    file_pattern = re.compile(f'^{FILENAME_PREFIX}_(\d{{5,}})_.*\.mp4$')
    video_files = sorted(
        [f for f in os.listdir(output_dir) if file_pattern.match(f)],
        key=lambda f: int(file_pattern.match(f).group(1))
    )
    
    if not video_files:
        print("No video files found in the output directory that match the expected format. Exiting.", file=sys.stderr)
        return 1

    concat_file_path = os.path.join(output_dir, "concat_list.txt")
    with open(concat_file_path, "w", encoding='utf-8') as f:
        for filename in video_files:
            f.write(f"file '{filename}'\n")

    chapters_file_path = os.path.join(output_dir, "chapters.txt")
    cumulative_duration_ms = 0
    with open(chapters_file_path, "w", encoding='utf-8') as f:
        f.write(';FFMETADATA1\n')
        
        for filename in video_files:
            match = re.search(r'_(\d+)_', filename)
            if match:
                video_index = int(match.group(1)) - 1
                if video_index < len(prompts_to_generate):
                    prompt = prompts_to_generate[video_index]
                    duration_s = get_video_duration(os.path.join(output_dir, filename))
                    duration_ms = int(duration_s * 1000)
                    
                    f.write('[CHAPTER]\n')
                    f.write('TIMEBASE=1/1000\n')
                    f.write(f'START={cumulative_duration_ms}\n')
                    f.write(f'END={cumulative_duration_ms + duration_ms}\n')
                    f.write(f'title={prompt}\n\n')
                    
                    cumulative_duration_ms += duration_ms
                else:
                    print(f"Warning: Prompt not found for video {filename}. Skipping chapter.", file=sys.stderr)

    print("Concatenation and chapter files created.")
    
    ffmpeg_command = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file_path, 
        '-i', chapters_file_path, '-map_metadata', '1', '-c', 'copy', 
        os.path.join(output_dir, output_filename)
    ]
    print("Running ffmpeg command:", " ".join(ffmpeg_command))
    try:
        subprocess.run(ffmpeg_command, check=True)
        print("\nVideos concatenated successfully.")
        
        os.remove(concat_file_path)
        os.remove(chapters_file_path)
        print("Temporary files removed.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg failed with exit code {e.returncode}", file=sys.stderr)
        print(f"Output:\n{e.stdout}\n{e.stderr}", file=sys.stderr)
        return 1

    return 0

def find_server_info_from_ps():
    """
    Parses `ps aux` output to find ComfyUI's host and port.
    Returns a tuple of (host, port) or (None, None) if not found.
    """
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, check=True)
        
        for line in result.stdout.splitlines():
            if 'python' in line and 'main.py' in line:
                host_match = re.search(r'--listen\s+([^\s]+)', line)
                port_match = re.search(r'--port\s+([^\s]+)', line)
                
                if host_match and port_match:
                    host = host_match.group(1)
                    port = port_match.group(1)
                    
                    if host == '0.0.0.0':
                        host = '127.0.0.1'
                        
                    return (host, port)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
        
    return (None, None)

def main():
    """Main function to parse arguments and run the chosen mode."""
    parser = argparse.ArgumentParser(description="Batch process ComfyUI generations or concatenate existing videos.")
    
    parser.add_argument(
        '--prompts-file',
        type=str,
        default='MovieGenVideoBench.txt',
        help='Path to the text file containing prompts.'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        required=False,
        help='The absolute path to the ComfyUI output directory.'
    )

    parser.add_argument(
        '--api-host',
        type=str,
        required=False,
        help='The host for the ComfyUI API server.'
    )

    parser.add_argument(
        '--api-port',
        type=int,
        required=False,
        help='The port for the ComfyUI API server.'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform checks without queuing jobs.'
    )

    parser.add_argument(
        '--concat', '-c',
        action='store_true',
        help='Concatenate existing videos from the output directory instead of generating new ones.'
    )

    parser.add_argument(
        '--start-over',
        action='store_true',
        help='Ignore existing files and start the batch from the beginning.'
    )
    
    args = parser.parse_args()
    
    prompts_file_path = args.prompts_file

    if args.api_host and args.api_port:
        api_host = args.api_host
        api_port = args.api_port
    else:
        api_host, api_port = find_server_info_from_ps()
        
    if not api_host or not api_port:
        api_host = '127.0.0.1'
        api_port = 8188
    
    api_url = f"http://{api_host}:{api_port}"

    if args.output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_output_dir = os.path.normpath(os.path.join(script_dir, '../../output'))
    else:
        base_output_dir = args.output_dir
    
    output_dir = os.path.join(base_output_dir, 'MovieGenVideoBench/')

    if not os.path.exists(prompts_file_path):
        print(f"Error: Prompts file '{prompts_file_path}' not found.", file=sys.stderr)
        return 1
    with open(prompts_file_path, 'r', encoding='utf-8') as f:
        prompts_to_generate = [line.strip() for line in f if line.strip()]

    queue_count = get_queue_length(api_url)
    if queue_count > 0:
        print(f"Aborting: There are {queue_count} jobs already in the queue. Please wait for them to finish before starting a new batch.")
        return 1

    if args.concat:
        if args.dry_run:
            print("Dry run successful: Concatenation arguments are valid.")
            return 0
        return concatenate_videos(prompts_to_generate, output_dir)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workflow_file = os.path.join(script_dir, WORKFLOW_FILE)

        if not os.path.exists(workflow_file):
            print(f"Error: Workflow file '{workflow_file}' not found.", file=sys.stderr)
            return 1
        if not prompts_to_generate:
            print("Warning: Prompts file is empty. Exiting.", file=sys.stderr)
            return 1
        
        if args.dry_run:
            print("Dry run successful: Generation arguments are valid.")
            return 0

        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                prompt_workflow = json.load(f)

            if args.start_over:
                start_index = 0
            else:
                start_index = find_last_completed_index(output_dir, FILENAME_PREFIX)

            # This is the important change: handles the -1 return from find_last_completed_index
            if start_index < 0:
                start_index = 0

            if start_index >= len(prompts_to_generate):
                print("Batch generation already complete. Exiting.", file=sys.stderr)
                return 0
                
            print(f"Loaded {len(prompts_to_generate)} prompts from '{prompts_file_path}'.")
            if start_index > 0:
                print(f"Resuming from index {start_index} ('{prompts_to_generate[start_index]}').")
            else:
                print("Starting batch from the beginning.")
            print("Starting batch generation...")

            def queue_prompt(prompt_workflow):
                p = {"prompt": prompt_workflow}
                data = json.dumps(p).encode('utf-8')
                requests.post(f"{api_url}/prompt", data=data)

            for i in range(start_index, len(prompts_to_generate)):
                prompt = prompts_to_generate[i]
                print(f"[{i+1}/{len(prompts_to_generate)}] Generating: '{prompt}'")
                
                if PROMPT_NODE_ID in prompt_workflow:
                    node = prompt_workflow[PROMPT_NODE_ID]
                    node['inputs'][PROMPT_INPUT_NAME] = prompt
                else:
                    print(f"Error: Node ID '{PROMPT_NODE_ID}' not found in the workflow.", file=sys.stderr)
                    return 1
                
                queue_prompt(prompt_workflow)
                
                time.sleep(1)

            print("\nBatch generation complete.")
            return 0

        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to ComfyUI API at {api_url}.", file=sys.stderr)
            print("Please ensure ComfyUI is running in API mode (--listen) and the port is correct.", file=sys.stderr)
            return 1
        except KeyError:
            print(f"Error: Could not find node with ID '{PROMPT_NODE_ID}' or input '{PROMPT_INPUT_NAME}'.", file=sys.stderr)
            print("Please check your node ID and input name in the script configuration.", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            return 1

if __name__ == "__main__":
    sys.exit(main())
	
#END OF moviegen_logic.py

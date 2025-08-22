# fastwan-moviegen

**Provisioning Script and Simple Test to Work the MovieGen Prompts Using FastWan**

This project is intended to facilitate easily firing off test renders using the FastWan model. It uses demo prompts from MovieGenBench and Wan2.2-Lightning on the `madiator2011/better-comfyui:slim-5090` container image.

---

### How to Use

1.  Start the container and open a shell using `zasper`/`ssh`/`exec -it bash`/whatever.
2.  Run the provisioning script with the following command:

    ```bash
    curl -s https://raw.githubusercontent.com/FNGarvin/fastwan-moviegen/main/provision.sh | bash
    ```

3.  Open ComfyUI, open the FastWanMovieGen.json template (found in the "Load Workflow" menu at or near the bottom), and hit **Run** to queue a large number of demo prompts.  Alternatively, open the FastWan-Simple template to test individual prompts of your own devices.

---

### Features

* **Custom Prompts:** The default prompts are sourced from MovieGenBenchmark and Wan2.2-Lightning, but you can use any text file with one prompt per line by providing the filename.
* **Resume Feature:** If you stop the batch and later attempt to resume, the script will scan the output directory and attempt to pick up where you stopped.
* **Concatenation:** If you check the "concat only" option, the script will concatenate all available files with nicely labeled chapters that indicate the prompt used for each segment.

---

### Licensing

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International Public License (CC BY-NC 4.0).

This project uses and packages the following, each provided under their respective licenses:

* Prompts from [MovieGenBench](https://github.com/facebookresearch/MovieGenBench): Licensed under the Creative Commons Attribution-NonCommercial 4.0 International Public License (CC BY-NC 4.0).
* Prompts from [Wan2.2-Lightning](https://github.com/ModelTC/Wan2.2-Lightning): Licensed under the Apache License, Version 2.0.
* Models from [Wan2.2](https://github.com/Wan-Video/Wan2.2): Licensed under the Apache License, Version 2.0.
* Models from [FastVideo](https://github.com/hao-ai-lab/FastVideo): Licensed under the Apache License, Version 2.0.

# fastwan-moviegen

**Provisioning Script and Simple Test to Work the MovieGen Prompts Using FastWan**

This project is intended to facilitate easily firing off test renders using the FastWan model across a range of GPU capacities. It uses demo prompts from MovieGenBench and Wan2.2-Lightning on the `madiator2011/better-comfyui:slim-5090` container image.

---

### How to Use

1.  Start the container and open a shell using `zasper`/`ssh`/`exec -it bash`/whatever.

2.  Choose the provisioning script that matches your GPU's VRAM and run the corresponding command.

    * **For 16GB+ GPUs (Original FP16 Model):**
        ```bash
        curl -s https://raw.githubusercontent.com/FNGarvin/fastwan-moviegen/main/provision.sh | bash
        ```

    * **For 10GB/12GB GPUs (Quantized GGUF Q6 Model):**
        ```bash
        curl -s https://raw.githubusercontent.com/FNGarvin/fastwan-moviegen/main/provision10GB.sh | bash
        ```

    * **For 8GB GPUs (Quantized GGUF Q3 Model):**
        ```bash
        curl -s https://raw.githubusercontent.com/FNGarvin/fastwan-moviegen/main/provision8GB.sh | bash
        ```

3.  Open ComfyUI and load the workflow that corresponds to your setup (found in the "Load Workflow" menu).

    * `FastWanMovieGen.json`: Queues a large batch of demo prompts using the full FP16 model.
    * `FastWan-Simple.json`: A simple template for testing individual prompts with the full FP16 model.
    * `FastWan-GGUF.json`: A template for low-VRAM GPUs. **Important:** After loading, you must click the GGUF Loader node and **select the `.gguf` model file** your provisioning script downloaded from the dropdown menu.

---

### Features

* **Custom Prompts:** The default prompts are sourced from MovieGenBenchmark and Wan2.2-Lightning, but you can use any text file with one prompt per line by providing the filename.
* **Resume Feature:** If you stop the batch and later attempt to resume, the script will scan the output directory and attempt to pick up where you stopped.
* **Concatenation:** If you check the "concat only" option, the script will concatenate all batched videos with nicely labeled chapters that indicate the prompt used for each segment.

---

### Licensing

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International Public License (CC BY-NC 4.0).

This project uses and packages the following, each provided under their respective licenses:

* Prompts from [MovieGenBench](https://github.com/facebookresearch/MovieGenBench): Licensed under the CC BY-NC 4.0 license.
* Prompts from [Wan2.2-Lightning](https://github.com/ModelTC/Wan2.2-Lightning): Licensed under the Apache License, Version 2.0.
* Models from [Wan2.2](https://github.com/Wan-Video/Wan2.2): Licensed under the Apache License, Version 2.0.
* Models from [FastVideo](https://github.com/hao-ai-lab/FastVideo): Licensed under the Apache License, Version 2.0.
* Node from [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF): Licensed under the MIT License.

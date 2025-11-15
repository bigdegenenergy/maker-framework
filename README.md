> # MAKER Framework: A Practical Implementation
> 
> This repository provides a practical implementation of the **MAKER** framework, as described in the paper "[Solving a Million-Step LLM Task with Zero Errors](https://arxiv.org/abs/2511.09030)". MAKER stands for **M**aximal **A**gentic decomposition, first-to-ahead-by-**K** **E**rror correction, and **R**ed-flagging.
> 
> The goal of this project is to provide a reusable, adaptable, and easy-to-understand implementation of the MAKER framework, enabling developers and researchers to apply these powerful techniques to their own complex, multi-step tasks.
> 
> ## Core Principles
> 
> The MAKER framework is built on three core principles:
> 
> 1.  **Maximal Agentic Decomposition (MAD):** The task is broken down into the smallest possible, independent subtasks. Each subtask is then assigned to a dedicated "micro-agent" (an LLM instance with a specific, focused prompt).
> 
> 2.  **First-to-Ahead-by-k Voting:** To ensure the accuracy of each step, multiple micro-agents are run in parallel for each subtask. Their outputs are then subjected to a voting process. A result is considered valid only when it has been produced by at least 'k' more agents than any other competing result.
> 
> 3.  **Red-Flagging:** To further improve reliability, any LLM output that exhibits signs of potential error is immediately discarded. The paper identifies two key red flags: overly long responses and incorrectly formatted responses.
> 
> ## Repository Structure
> 
> ```
> maker_framework/
> ├── docs/ # Detailed documentation
> │   └── MAKER_Framework_Guide.md
> ├── examples/ # Example implementations
> │   └── towers_of_hanoi/
> │       ├── __init__.py
> │       ├── main.py
> │       └── prompts.py
> ├── maker/ # Core MAKER framework implementation
> │   ├── __init__.py
> │   ├── algorithms.py
> │   └── prompts.py
> ├── prompts/ # General bootstrap prompts
> │   └── maker_bootstrap_prompt.md
> └── README.md
> ```
> 
> ## Getting Started
> 
> 1.  **Explore the Documentation:** Start by reading the detailed guide in `docs/MAKER_Framework_Guide.md` to fully understand the principles and architecture of the framework.
> 
> 2.  **Review the Bootstrap Prompt:** The `prompts/maker_bootstrap_prompt.md` file provides a template for applying the MAKER framework to your own tasks.
> 
> 3.  **Examine the Core Implementation:** The `maker/` directory contains the Python implementation of the core MAKER algorithms, including the voting and red-flagging mechanisms.
> 
> 4.  **Run the Example:** The `examples/towers_of_hanoi/` directory provides a complete, runnable example of the MAKER framework applied to the Towers of Hanoi problem.
> 
> ## How to Adapt to Your Own Tasks
> 
> 1.  **Decompose Your Task:** Break down your problem into the smallest possible subtasks.
> 
> 2.  **Define Your Micro-agent Prompts:** For each subtask, create a specific, focused prompt. See the `examples/towers_of_hanoi/prompts.py` file for an example.
> 
> 3.  **Configure the MAKER Algorithms:** Use the functions in `maker/algorithms.py` to implement the voting and red-flagging logic for your task.
> 
> 4.  **Create Your Main Application:** Write a main script that orchestrates the execution of your subtasks using the MAKER framework. The `examples/towers_of_hanoi/main.py` file serves as a great starting point.
> 
> ## Contributing
> 
> Contributions are welcome! Please feel free to submit pull requests with improvements, new examples, or bug fixes.
> 
> ## License
> 
> This project is licensed under the MIT License. See the `LICENSE` file for details.

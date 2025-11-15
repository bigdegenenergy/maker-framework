# MAKER Framework: A Guide to Solving Complex Multi-Step Tasks with LLMs

## Executive Summary

This guide provides a comprehensive analysis of the MAKER framework, introduced in the paper "Solving a Million-Step LLM Task with Zero Errors" (arXiv:2511.09030), along with a reusable prompt template that allows you to apply the framework's principles to your own complex tasks. The MAKER system represents a paradigm shift in how we approach large-scale LLM reasoning tasks, moving away from relying on continual improvement of base models toward massively decomposed agentic processes.

**Key Achievement**: MAKER successfully solved a task requiring over one million LLM steps with zero errors, demonstrating that extreme task decomposition combined with rigorous error correction can enable LLMs to perform at scales previously thought impossible.

## The Problem: LLMs Cannot Scale to Long-Horizon Tasks

Large language models have achieved remarkable breakthroughs in reasoning, insights, and tool use. However, chaining these abilities into extended processes at the scale of those routinely executed by humans, organizations, and societies has remained out of reach. The fundamental issue is that LLMs have a **persistent error rate** that prevents scale-up.

For instance, recent experiments in the Towers of Hanoi benchmark domain showed that LLM-based processes inevitably become derailed after at most a few hundred steps. Even if an LLM achieves 99% accuracy on individual steps, a system with a 1% per-step error rate is expected to fail after only 100 steps of a million-step task. This exponential decay in reliability makes solving large-scale tasks fundamentally impossible with traditional approaches.

## The MAKER Solution: Three Core Components

MAKER (Maximal Agentic decomposition, first-to-ahead-by-K Error correction, and Red-flagging) addresses this challenge through three synergistic components that work together to achieve unprecedented reliability in long-horizon tasks.

### Component 1: Maximal Agentic Decomposition (MAD)

The first component involves breaking down a task with s steps into s subtasks, where each subtask consists of exactly one step. This extreme level of decomposition stands in stark contrast to traditional approaches that attempt to solve entire problems in a single LLM call or divide tasks into larger chunks.

**Why Extreme Decomposition Works**

LLMs are auto-regressive models, meaning that when generating the ith action in a sequence, the model becomes increasingly burdened by the context produced in generating all previous actions. As context accumulates, the model's outputs become increasingly unreliable. With maximal decomposition, each agent's context is limited to only the information necessary to execute its single assigned step. This focused approach allows the agent to avoid confusion that can creep in from irrelevant context.

Additionally, this approach enables the use of smaller, more cost-effective LLMs with limited context windows. The paper demonstrates that state-of-the-art reasoning models are not required; relatively small non-reasoning models suffice when tasks are decomposed to this granular level.

**The Microagent Concept**

In the MAKER framework, each agent is assigned a "micro-role" rather than a human-level role. Instead of asking an agent to "solve the Towers of Hanoi problem," you ask it to "determine the next single move given the current state." This shift from anthropomorphic agents to specialized microagents is critical to exploiting the inherent machine-like nature of LLMs and taking advantage of error-correction methods that have been essential to scaling in many domains of computing.

**Parallels with Microservices Architecture**

The paper draws compelling parallels between microagents and microservices in software engineering. The benefits of decomposing a monolithic agent's task into subtasks mirror those of decomposing a monolithic application into smaller services: modularity, independent development and testing, scalability, design for failure, and easier management of change. Microagents can be considered a natural evolution of microservices, where natural language serves as a powerful, well-understood communication protocol.

### Component 2: First-to-Ahead-by-k Voting

The second component addresses the exponential decay problem inherent in multi-step processes. While decomposition creates many potential points of failure, the modularity it provides enables effective error correction at each step through a voting mechanism.

**The Voting Process**

For each subtask, multiple independent samples are drawn from the LLM. A "first-to-ahead-by-k" voting process is then used to determine the winning result. This means that a candidate result is accepted only when it has been sampled k times more than any other competing result. This approach is motivated by the optimality of the sequential probability ratio test (SPRT) and generalizes the classic gambler's ruin problem.

**Mathematical Foundation**

The paper provides rigorous mathematical analysis showing that for a task requiring s total steps with an inherent per-step success rate p, the minimal voting parameter k needed to achieve a target overall success probability t grows logarithmically with the number of steps:

k_min = Θ(ln s)

This logarithmic growth is crucial because it means that even for tasks with millions of steps, the required voting parameter remains manageable. The paper demonstrates that for a task with one million steps, MAKER with first-to-ahead-by-k error correction enables high probability zero-error solutions for practical values of k, even when the base per-step error rate approaches 1-in-10.

**Cost-Effectiveness**

The expected cost of solving a task scales with the number of steps and the voting parameter, but under extreme decomposition (m=1), this cost remains manageable. Without extreme decomposition, the cost becomes exponentially infeasible. The formalization shows that effective scaling is achievable only under extreme decomposition; partial decomposition is insufficient.

### Component 3: Red-Flagging

The third component recognizes that "bad" behaviors are correlated in LLMs. If an LLM produces a response that signals pathological behavior, the response should be flagged and immediately discarded before it enters the voting process.

**Two Types of Red Flags**

The paper identifies two key indicators of unreliable outputs:

**Overly Long Responses**: When an LLM becomes confused, it tends to over-analyze situations in a cycle of self-destruction, producing excessively long responses. In the MAKER framework, each microagent's role is highly focused and relatively simple. If an agent is doing too much work to figure out its answer, it is likely confused and more likely to provide an incorrect response. The paper found that responses exceeding approximately 700 tokens showed a precipitous increase in error rates.

**Incorrectly Formatted Responses**: When an agent produces an answer in an incorrect format, it indicates that the LLM has been conditioned into a strange state. Misformatted output is often correlated with twisted reasoning, making it a reliable indicator of potential errors.

**Impact on Correlated Errors**

While red-flagging does increase the overall per-step success rate p, its more important contribution is in reducing **correlated errors**—particular steps that have unusually high error rates compared to the average step. The paper's experiments showed that red-flagging successfully reduces collision counts (the number of steps where both the first and second votes are incorrect), which is critical for many-step tasks. Even increasing the success rate from 99% to 99.9% can have a large impact when the number of steps is in the millions.

## The Algorithms

The MAKER framework is implemented through three interconnected algorithms:

**Algorithm 1: generate_solution**
- Takes as input the initial state, the model, and the voting parameter k
- For each of s steps, calls the voting procedure to determine the action
- Returns the complete action sequence

**Algorithm 2: do_voting**
- Implements the first-to-ahead-by-k voting mechanism
- Maintains vote counts for all candidate actions
- Repeatedly calls get_vote until one action has k more votes than any other
- Returns the winning action

**Algorithm 3: get_vote**
- Samples a response from the model given the current state
- Checks the response for red flags (overly long or incorrectly formatted)
- If red flags are detected, discards the response and resamples
- Otherwise, parses and returns the action and next state

This recursive structure ensures that error correction is applied at every step, and that potentially problematic outputs are filtered out before they can influence the voting process.

## Empirical Results: Solving the 20-Disk Towers of Hanoi

The paper demonstrates the framework's effectiveness by solving the 20-disk Towers of Hanoi problem, which requires 1,048,575 steps (2^20 - 1 moves). Using gpt-4.1-mini as the base model with a maximum output token threshold of 750 and k_min = 3, the system successfully completed the task with zero errors.

The behavior of the process showed exponential decay in the number of undecided steps as voting rounds progressed, mirroring theoretical predictions. While most steps were resolved quickly, a few steps required notably more sampling and voting rounds, highlighting the importance of red-flagging in handling correlated errors. One pathological step required 18 rounds of voting, but the system's design allowed it to persist until the correct answer emerged.

The experiments confirmed that robust decorrelation is crucial in many-step tasks, and that red-flagging helps with both overall error rates and, more importantly, with correlated errors that could otherwise derail the entire process.

## Reusable Prompt Template

To apply the MAKER framework to your own tasks, use the following structured prompt template:

---

### MAKER Framework Prompt Template

**Overall Task Description:**
[Provide a clear, concise description of the complete task you want to solve]

**Step 1: Maximal Agentic Decomposition**

Break down the overall task into the smallest possible independent subtasks. Each subtask should represent a single, atomic step in the process.

For each subtask, define a focused microagent prompt:

```
Microagent Role: [Describe the single, specific function this agent performs]

Input Context: [Specify what information the agent receives]

Expected Output: [Define the exact format and content of the agent's response]

Constraints: [List any rules or limitations the agent must follow]
```

**Step 2: First-to-Ahead-by-k Voting Configuration**

- **Voting Parameter (k):** [Specify your k value. Start with k=3 for most tasks. Increase k if higher reliability is needed, though this increases computational cost]

- **Voting Implementation:** For each subtask, run [2k-1] instances of the microagent in parallel. Accept a result only when it has been returned by at least k more agents than any other competing result.

**Step 3: Red-Flagging Criteria**

Define the criteria for identifying and discarding unreliable outputs:

- **Length Threshold:** Discard any response exceeding [specify token/word count] as it likely indicates confusion or over-analysis.

- **Format Requirements:** Discard any response that does not match the expected format: [specify exact format, e.g., JSON structure, specific fields, data types]

- **Additional Red Flags:** [List any task-specific indicators of unreliable output]

**Execution Protocol:**

1. Initialize the task with the starting state
2. For each step in the sequence:
   a. Generate [2k-1] candidate responses using the microagent prompt
   b. Apply red-flagging criteria to filter out unreliable responses
   c. If a response is flagged, generate a replacement
   d. Apply first-to-ahead-by-k voting to select the winning action
   e. Update the state based on the winning action
3. Continue until the task is complete

---

## Practical Example: Applying MAKER to Towers of Hanoi

To illustrate how to use this framework, here's a concrete example using the Towers of Hanoi problem:

**Overall Task Description:**
Solve the Towers of Hanoi puzzle for 20 disks, moving all disks from peg 0 to peg 2, following the rules that only one disk can be moved at a time and a larger disk cannot be placed on top of a smaller disk.

**Step 1: Maximal Agentic Decomposition**

```
Microagent Role: Determine the next single legal move in the Towers of Hanoi puzzle

Input Context: 
- Current state of all three pegs (which disks are on which pegs)
- The goal configuration
- The rules of the game

Expected Output: 
A single move in the format [disk_number, source_peg, destination_peg]
Example: [3, 0, 2] means move disk 3 from peg 0 to peg 2

Constraints:
- Only move one disk at a time
- Never place a larger disk on top of a smaller disk
- Choose the optimal move that progresses toward the goal
```

**Step 2: First-to-Ahead-by-k Voting Configuration**

- **Voting Parameter (k):** 3
- **Voting Implementation:** For each move decision, run 5 microagent instances (2×3-1=5). Accept a move only when at least 3 agents agree on it, and this agreement is at least 3 votes ahead of any alternative move.

**Step 3: Red-Flagging Criteria**

- **Length Threshold:** Discard any response exceeding 750 tokens. A simple move decision should be concise; excessive length indicates confusion.

- **Format Requirements:** Discard any response that is not a valid list of three integers in the format [disk, source, target] where:
  - disk is an integer from 1 to 20
  - source and target are integers from 0 to 2
  - source ≠ target

- **Additional Red Flags:** Discard responses that suggest illegal moves (e.g., moving a disk that isn't on top of its peg, or placing a larger disk on a smaller one).

## Key Insights and Implications

The MAKER framework represents a fundamental shift in how we approach scaling AI systems. Rather than waiting for continual improvement of base LLMs to solve increasingly complex tasks, the framework demonstrates that **massively decomposed agentic processes (MDAPs)** can efficiently solve problems at the level of organizations and societies using current models.

**State-of-the-Art Models Not Required**: One of the most surprising findings is that advanced reasoning models are not necessary. Relatively small, non-reasoning models suffice when tasks are properly decomposed. This has significant implications for cost-effectiveness and accessibility.

**The Multi-Agent Advantage**: The paper demonstrates an instance of "multi-agent advantage" analogous to quantum advantage—a solution to a problem that is not solvable by a monolithic single-agent system. This establishes a new paradigm for scaling AI capabilities.

**Limits and Future Directions**: The framework assumes that tasks can be decomposed into small enough steps that each step can be solved by an LLM agent with reasonable probability. The central question for future research is: Are there important problems where such decomposition is not possible or is computationally infeasible to discover? At the lowest level of LLM implementation, there is a decomposition into primitive operations; the hope is that there exists some intermediate decomposition that is still linguistic but effectively compartmentalizes context and different behaviors.

## Conclusion

The MAKER framework provides a practical, theoretically grounded approach to solving complex, multi-step tasks with LLMs. By combining maximal agentic decomposition, first-to-ahead-by-k voting, and red-flagging, the framework achieves unprecedented reliability in long-horizon tasks. The reusable prompt template provided in this guide allows you to apply these principles to your own problems, potentially unlocking capabilities that were previously thought to be beyond the reach of current LLM technology.

The key takeaway is that the path to more capable AI systems may not solely lie in building ever-larger and more sophisticated models, but in developing better architectures for decomposing and coordinating multiple agents working on focused subtasks. This represents a shift from the "bigger is better" paradigm to a "smarter coordination is better" paradigm—one that may prove essential for tackling the complex, multi-step challenges that characterize real-world problems at the scale of organizations and societies.

---

## References

- Meyerson, E., Paolo, G., Dailey, R., Shahrzad, H., Francon, O., Hayes, C. F., Qiu, X., Hodjat, B., & Miikkulainen, R. (2025). Solving a Million-Step LLM Task with Zero Errors. arXiv:2511.09030. https://arxiv.org/abs/2511.09030

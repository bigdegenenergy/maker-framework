> # MAKER Framework Bootstrap Prompt
> 
> This document provides a bootstrap prompt for applying the **MAKER** framework to a new task. The goal is to structure your problem in a way that is compatible with the principles of Maximal Agentic Decomposition, First-to-Ahead-by-k Voting, and Red-Flagging.
> 
> ## Task Definition
> 
> **Overall Task:** [Clearly and concisely describe the overall task to be solved.]
> 
> **Success Criteria:** [Define what constitutes a successful completion of the task.]
> 
> ## MAKER Framework Configuration
> 
> ### 1. Maximal Agentic Decomposition (MAD)
> 
> **Subtask Breakdown:**
> 
> *   **Subtask 1:** [Describe the first subtask]
> *   **Subtask 2:** [Describe the second subtask]
> *   ... and so on.
> 
> **Micro-agent Prompts:**
> 
> For each subtask, define a specific, focused prompt for a micro-agent.
> 
> *   **Micro-agent for Subtask 1:**
>     ```
>     Role: [Role of the micro-agent]
>     Input: [Input for the micro-agent]
>     Output: [Expected output format]
>     ```
> 
> *   **Micro-agent for Subtask 2:**
>     ```
>     Role: [Role of the micro-agent]
>     Input: [Input for the micro-agent]
>     Output: [Expected output format]
>     ```
> 
> ### 2. First-to-Ahead-by-k Voting
> 
> **Voting Parameter (k):** [Define the value of k. A good starting point is k=3.]
> 
> **Voting Logic:** For each subtask, the output of the micro-agents will be collected. A result is considered valid only when it has been produced by at least 'k' more agents than any other competing result.
> 
> ### 3. Red-Flagging
> 
> **Red-Flagging Criteria:**
> 
> *   **Overly Long Responses:** Responses exceeding [e.g., 500] tokens will be discarded.
> *   **Incorrectly Formatted Responses:** Responses that do not adhere to the specified output format will be discarded.
> *   **[Add any other custom red-flagging criteria for your specific task.]**
> 
> ## Implementation Plan
> 
> 1.  **Implement the Micro-agents:** Write the code to call the LLM with the defined micro-agent prompts.
> 
> 2.  **Implement the Voting Logic:** Write the code to perform the first-to-ahead-by-k voting.
> 
> 3.  **Implement the Red-Flagging Logic:** Write the code to check for and discard red-flagged responses.
> 
> 4.  **Orchestrate the Workflow:** Write the main application logic that chains the subtasks together, using the MAKER framework to ensure reliability at each step.

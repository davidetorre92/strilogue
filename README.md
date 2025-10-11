# Strilogue: The ZDoom Dialogue Script Compiler

Strilogue is an open-source web application designed to simplify the creation, editing, and management of **Universal Strife Dialogue Format (USDF)** and **ZDoom Script Dialogue Format (ZSDF)** files.

Stop manually battling nested curly braces and start managing your dialogue with a clean, verifiable, plain-text flow.

## Features

Strilogue provides **bidirectional conversion** and essential tools for mod developers:

### 1. Full Round-Trip Conversion

Strilogue offers two-way conversion functionality. ZDoom $\rightarrow$ Plain Text: Converts complex `conversation { ... }` blocks into a clean, human-readable format. Plain Text $\rightarrow$ ZDoom: Converts the simplified plain text format back into a valid, indented ZDoom script file, ready for use in UDB/DoomBuilder.

### 2. Plain Text Editing Mode

This mode is the core of the tool's usability. It allows dialogue authors to focus purely on text and flow. The benefits of this mode includes a clearer flow. The format uses `#Page` and `#CHOICE:` headers for instant readability. Tagging: Logic is represented by simple, readable tags (e.g., `(#nextpage(2))`, `(#req(Token, 1))`, `(#close)`).

### 3. Language Variable Management

The tool intelligently handles external string variables, which are essential for translation projects. This includes Lookup: Upload your external `LANGUAGE` file to view variables (e.g., `$TXT_ID`) in the sidebar for easy cross-referencing and export new variables.

### 4. Supported Dialogue Logic

Strilogue supports all major ZDoom dialogue features, including:

| Feature | ZDoom Syntax | Plain Text Tag | 
| :--- | :--- | :--- | 
| Jump to Page | `nextpage = ID;` | `(#nextpage(ID))` | 
| Item Requirement | `require { ... }` | `(#req(ItemName, Amount))` | 
| Give Item | `giveitem = ItemName;` | `(#give(ItemName))` | 
| ACS Script Call | `special = ID; arg0 = A; arg1 = B;` | `(#special(ID, A, B))` | 
| Close Dialogue | `closedialog = true;` | `(#close)` | 
| UI/Sound | `panel = "NAME"; voice = "FILE";` | `#PANEL(NAME)`, `#VOICE(FILE)` | 

## Getting Started (Workflow)

The workflow consists of six steps:

1. Input: Paste your ZDoom `conversation { ... }` script into the main input area.

2. Language: If your script uses `$TXT_IDs`, upload or paste your `LANGUAGE` file contents into the sidebar.

3. Convert to Plain Text: Use the button to generate the human-readable format for editing.

4. Reverse Conversion: Paste your edited Plain Text into the second input area.

5. Choose Output Mode: This step involves selecting between two primary modes. Variable Mode (Default) utilizes the Plain Text variable keys (e.g., `$TXT_ID`) in the final ZDoom output and generates a Language Snippet for new text. Literal Mode requires you to check the "Literal Text Output Mode" box to substitute the variable keys with the literal text you wrote (e.g., `dialog = "Hello World!"`).

6. Convert to ZDoom: Generate and download your new ZDoom script file.

## Future Plans (Graphical Editor)

The current version focuses on robust text-based editing and conversion. Future updates will incorporate the graphical interface vision: Node-Based Flow Editor: Visualize Pages (nodes) and Choices (edges) for intuitive flow design. Real-time Syntax Validation.
# 3D Neural Network Visualizer (NN Viz)

**A Blender add-on for generating publication-quality 3D diagrams of neural network architectures.**

---

## Table of Contents

1. [Overview](#overview)  
2. [Installation & Quick Start](#installation--quick-start)  
   - [Splitting the Viewport](#splitting-the-viewport)  
   - [Loading & Running the Script](#loading--running-the-script)  
   - [Accessing the NN Viz Panel](#accessing-the-nn-viz-panel)  
3. [Usage Guide](#usage-guide)  
4. [Features](#features)  
5. [Repository Structure](#repository-structure)  
6. [Tips & Best Practices](#tips--best-practices)  
7. [Contributing](#contributing)  
8. [License & Credits](#license--credits)  

---

## Overview

NN Viz is a Blender-based utility designed to streamline the creation of three-dimensional neural network diagrams. By leveraging Blender’s Python API, NN Viz enables researchers and educators to:

- Define custom layer dimensions, names, and colors  
- Randomize connection colors per input for clarity  
- Instantly preview and iterate via Blender’s scripting workflow  

---

## Installation & Quick Start

<details>
<summary><strong>1. Splitting the Viewport</strong></summary>

1. Hover your cursor over the **right** edge of the 3D Viewport.  
2. When the cursor changes to ↔, **right-click** and select **Vertical Split**.  
3. Drag to allocate space for the new panel.  
</details>

<details>
<summary><strong>2. Loading & Running the Script</strong></summary>

1. In the newly created panel, switch to the **Text Editor** workspace.  
2. Click **New** → paste your most recent script (e.g. `nn_viz.py`).  
3. Select **Run Script** (▶️) to register the add-on.  
</details>

<details>
<summary><strong>3. Accessing the NN Viz Panel</strong></summary>

1. Return to your main 3D Viewport.  
2. Press **N** to open the sidebar.  
3. Locate and click the **NN Viz** tab to reveal the control panel.  
</details>

---

## Usage Guide

1. **Define Layers**  
   - Specify the number of neurons per layer.  
   - Assign custom names and RGBA colors.  

2. **Configure Connections**  
   - Enable “Show Connections.”  
   - Set the number of inputs and assign per-input colors.  
   - NN Viz will apply colors randomly to each connection.

3. **Generate Diagram**  
   - Click **Generate Network**.  
   - Inspect and refine directly in the 3D Viewport.

4. **Export & Render**  
   - Use Blender’s standard export (e.g., `File → Export → glTF`) or render settings to produce final imagery.

---

## Features

- **Layer Management**  
  - Editable names, neuron counts, and color pickers.  
- **Connection Styling**  
  - Per-input color assignment with random distribution.  
- **Live Scripting Workflow**  
  - Vertical split allows on-the-fly script edits and instant execution.  
- **Publication-Ready Output**  
  - High-resolution renders suitable for articles and presentations.

---

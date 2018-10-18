![Branchlabel](https://img.shields.io/badge/Branch-Develop-green.svg)  ![Versionlabel](https://img.shields.io/badge/Version-0.4.0-yellow.svg)
# SyntheticRTI
Creation of synthetic datasets for RTI and Photometric Stereo applications
- [Introduction](https://github.com/giach68/SyntheticRTI/tree/Develop#introduction)
- [Download](https://github.com/giach68/SyntheticRTI/tree/Develop#download)
- [Installation](https://github.com/giach68/SyntheticRTI/tree/Develop#installation)
- [Usage](https://github.com/giach68/SyntheticRTI/tree/Develop#usage)
  - [Create](https://github.com/giach68/SyntheticRTI/tree/Develop#create)
  - [Render](https://github.com/giach68/SyntheticRTI/tree/Develop#render)
  - [Tools](https://github.com/giach68/SyntheticRTI/tree/Develop#tools)
- [Various](https://github.com/giach68/SyntheticRTI/tree/Develop#various)
## Introduction
SyntheticRTI is a Blender plugin built to help create a synthetic database of 3d scanned images to train and test algorithms on.

Currently the plugin is developed for Blender version 2.79 and uses only the cycles renderer.

## Download
You can clone the whole project or download just the zipped plugin from here: [Download](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/giach68/SyntheticRTI/tree/Develop/SyntheticRTI-Plugin)

## Installation
If you cloned the project you have to first zip the `SyntheticRTI-Plugin` folder.
To install the plugin go to `file -> User Preferences… -> Add-ons -> install Add-on from File…` choose the file `SyntheticRTI-Plugin.zip` and press on `Install Add-on from File…` . Once installed it need to be activated. In the same settings page, write SyntheticRTI in the searchbox and check the tick on the add-on. The plugin will be available on the 3DView on the Tool tab.

## Usage
![plugin](https://github.com/giach68/SyntheticRTI/blob/master/Documentation/plugin_full.png)

The plugin is divided in 4 panels:
- **Create**: its mainly purpose is to create lamps, cameras and to manage the material parameters we want to iterate over the combinations;
- **Render**: it prepares the environment for rendering;
- **Tools**: various tools to help building the set;
- **Debug**: various information about the scene.

## Create
**Light file**: here you can insert the filepath of the .lp file with the position of lamps. Using the folder button it is possible to use the file select mode.  
The .lp files are structured this way:  

    #lights
    #index x y z

> for example:

    71
    00000001 0.276388019323349 -0.8506492376327515 0.4472198486328125
    00000002 -0.7236073017120361 -0.5257253050804138 0.44721952080726624
    00000003 -0.7236073017120361 0.5257253050804138 0.44721952080726624
    00000004 0.276388019323349 0.8506492376327515 0.4472198486328125
    00000005 0.8944262266159058 0.0 0.44721561670303345
    00000006 0.0 0.0 1.0
    00000007 0.956625759601593 -0.147618368268013 0.251149445772171
    00000008 0.956625759601593 0.147618368268013 0.251149445772171
    00000009 0.1552150994539261 -0.955422043800354 0.25115153193473816
    00000010 0.4360068142414093 -0.8641878962516785 0.25115203857421875
    …

**Create Lamps**: It loads all the lamps and it attaches them to a main object so it is possible to move the lamps (and cameras) altogether.

**Delete Lamps**: It deletes all the lamps at once.

**Create cameras**: It creates a camera attached to the main object.

**Delete cameras**: It deletes all cameras at once.

**Object**: a drop down list to select the mesh with the material on which to iterate

**Parameters**: To add a parameter just press the + or the – icon to remove the selected one. The up and down arrows move the selected parameter order in the list.

Each parameter has a name *(It must be unique!)*, a *min* and *max* value and a *steps* value.   The animation iterates over all parameters in order from top to bottom from max to min in n steps.

> in example:

    Par 1: min = 0, max = 1, steps = 2;
    
    Par 2: min =0, max=1, steps = 5
    
    Par 1 = 0  
    - Par 2 = 0  
    - Par 2 = 0.25  
    - Par 2 = 0.5  
    - Par 2 = 0.75  
    - Par 2 = 1  
    Par 1 = 1  
    - Par 2 = 0  
    - Par 2 = 0.25  
    - Par 2 = 0.5  
    - Par 2 = 0.75  
    - Par 2 = 1
	
For a total of 10 frames.

> **An object MUST be selected to iterate over the parameters!**

To apply the parameters to the material the object must have at least one material. The plugin enables the nodes for each materials and creates an animated value node for each parameter. Then you simply connect the value nodes to whichever node is needed to change over the animation.

![material node](https://github.com/giach68/SyntheticRTI/blob/master/Documentation/node_example.png)

## Render
**Output folder**: the path where to save the output files.

**Output name**: the name of the project. (Must be changed before the Animate all operation!)

**Animate all**: it creates the animation which iterates over all parameters, all cameras and all lights in this specific order. It needs at least one Camera to work.  

> In example:

    - Par 1 = 0
      - Par 2 = 0
        - Cam 1
          - Light 1
          - Light 2
        - Cam 2
          - Light 1
          - Light 2
      - Par 2 = 1
        - Cam 1
        - ...
    - Par 1 = 1
      - Par 2 = 0
        - ...
      - Par 2 = 1
        - ...

**Set Render**: set the render output path: `output_folder/EXR/name-frame_number`, the format to be .exr 32bit.

![output](https://github.com/giach68/SyntheticRTI/blob/master/Documentation/output.png)

It also set the following render passes on:  
- Normal;  
- Shadow  
- Diffuse Direct;  
- Diffuse Indirect;  
- Diffuse Color;  
- Glossy Direct;  
- Glossy Indirect;  
- Glossy Color.

![steps](https://github.com/giach68/SyntheticRTI/blob/master/Documentation/passes.png)

**Create file**: saves the output .csv file in the output folder with the given name. It contains all the coordinates of lamps and parameters value (camera positions and parameters still need implementation).  

## Tools

![tools](https://github.com/giach68/SyntheticRTI/blob/master/Documentation/tools.png)

**Export Lamp**: When a mesh is selected is possible to export its vertices in a .lp file to use them as lamps.

**Create nodes**: it’s used to convert .exr files in .png. Selecting a single file in the folder searches for the first and last frame of the animation. If there is a number in front (like 005-cube) it adds the number prefix to all the output folders. The output folders will be in a PNG folder at the upper level of the .exr file. The operator creates a compositing node tree and enables the following operations:

**Render Normals**: exports a single image of the normal in frame 1. It normalizes for a 0-1 range, multiplying by 0.5 and adding 0.5 to the .exr format.

> The output file will have a suffix number that has to be deleted
> manually.

**Render Composite**: exports the entire animation for all the following combinations in the PNG folder, each in its own subfolder:
- *DIFF*: only diffuse direct light `(Diffuse Direct * Diffuse Color)`;
- *DIFF-INDIFF*: diffuse direct and indirect light `((Diffuse Direct + Diffuse Indirect) * Diffuse Color)`;
- *DIFF-SPEC*: diffuse direct and specular direct light `((Diffuse Direct * Diffuse Color) + (Glossy Direct * Glossy Color))`;
- *DIFF-SPEC-INDIFF*: diffuse direct and indirect light plus specular direct light `(((Diffuse Direct + Diffuse Indirect) * Diffuse Color) + (Glossy Direct * Glossy Color))`;
- *DIFF-SPEC-INDIFF-INSPEC*: all the light components `(((Diffuse Direct + Diffuse Indirect) * Diffuse Color) + ((Glossy Direct +Glossy Indirect) * Glossy Color))`;
- *SHADOWS*: Direct shadow.

The final folder will look like this:

    Main folder/
    ├── EXR/
    │   ├── 005-cube-001.exr
    │   └── …
    └── PNG/
        ├── 005-DIFF/
        │   ├──005-cube-DIFF-001.png
        │   └── …
        ├── 005-DIFF-INDIFF/
        │   ├──005-cube-DIFF-INDIFF-001.png
        │   └── …
        ├── 005-DIFF-SPEC/
        │   ├──005-cube-DIFF-SPEC-001.png
        │   └── …
        ├── 005-DIFF-SPEC-INDIFF/
        │   ├──005-cube-DIFF-SPECC-INDIFF-001.png
        │   └── …
        ├── 005-DIFF-SPEC-INDIFF-INSPEC/
        │   ├──005-cube-DIFF-SPECC-INDIFF-INSPEC-001.png
        │   └── …
        ├── 005-SHADOWS/
        │   ├──005-cube-SHADOWS-001.png
        │   └── …
        └── 005-cube-NORMAL-001.png

> Please note the normal image suffix!

**Delete Nodes**: it deletes the nodes tree and restores the output to .exr

![Node setup](https://github.com/giach68/SyntheticRTI/blob/master/Documentation/node_export.png)

## Various
To view the console in Micorsoft Windows and have output information: `Window -> Toggle System Console`

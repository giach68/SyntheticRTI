# SyntheticRTI
Creation of synthetic datasets for RTI and Photometric Stereo applications

## Introduction
SyntheticRTI is a Blender plugin built to help create a synthetic database of 3d scanned images to train and test algorithms on.

Currently the plugin is developed for Blender version 2.79 and uses only the cycles renderer.

## Installation
To install the plugin go to `file -> User Preferences… -> Add-ons -> install Add-on from File…` choose the file `SyntheticRTI.py` and press on `Install Add-on from File…` . Once installed it need to be activated. In the same settings page, write SyntheticRTI in the searchbox and check the tick on the add-on. The plugin will be available on the 3DView on the Tool tab.

## Usage
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

## Render
**Output folder**: the path where to save the output files.  
**Output name**: the name of the project. (Must be changed before the Animate all operation!)  
**Animate all**: it creates the animation which iterates over all parameters, all cameras and all lights in this specific order. It needs at least one Camera to work.  

> In example:

    Par 1 = 0  
    - Par 2 = 0  
    -- Cam 1  
    --- Light 1  
    --- Light 2  
    -- Cam 2  
    --- Light 1  
    --- Light 2  
    - Par 2 = 1  
    -- Cam 1  
    -- …  
    Par 1 = 1  
    - Par 2 = 0  
    -- …  
    - Par 2 = 1  
    -- …

**Set Render**: set the render output path: `output_folder/EXR/name-frame_number`, the format to be .exr 32bit and the following render passes on:  
- Normal;  
- Shadow  
- Diffuse Direct;  
- Diffuse Indirect;  
- Diffuse Color;  
- Glossy Direct;  
- Glossy Indirect;  
- Glossy Color.

**Create file**: save the output .csv file in the output folder with the name given. It contains all the coordinates of lamps and parameters value (camera positions and parameters still need implementation).  

## Various
To view the console in windows: `Window -> Toggle System Console`

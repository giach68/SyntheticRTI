###OPERATORS###
import bpy
import os
import re
import csv
import shutil
from ..srtifunc import *
from bpy_extras.io_utils import ExportHelper, ImportHelper
#####TOOLS#####
#export lamps
class SRTI_OT_export_as_lamp(bpy.types.Operator, ExportHelper):
    """Create a .lp file for lamp from active object vertices. (Must be a MESH!)"""
    bl_idname = "srti.export_as_lamp"
    bl_label = "Export Mesh as Lamp file (.lp)"
    bl_options = {'REGISTER', 'UNDO'}
    # ExportHelper mixin class uses this
    filename_ext = ".lp"
    filter_glob : bpy.props.StringProperty(
            default="*.lp",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    @classmethod
    def poll(cls, context):
        if context.active_object != None:
            if context.active_object.type == 'MESH': 
                return True
        return False

    def execute(self, context):
        obj = context.active_object
        i = 0
        list = []
        for vert in obj.data.vertices:
            coord = vert.co
            i += 1
            string = "{0:08d} {1} {2} {3}".format(i, coord[0], coord[1], coord[2])
            list.append(string)

        print(i)
        for string in list:
            print (string)

        file = open(self.filepath, "w")
        file.write(str(i))
        file.write('\n')
        for line in list:
            file.write(line)
            file.write('\n')

        file.close()
        return{'FINISHED'}

class SRTI_OT_create_export_node(bpy.types.Operator, ImportHelper):
    """Prepares the file to output png passes."""
    bl_idname = "srti.create_export_node"
    bl_label = "Create Nodes from .exr"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".exr"
    filter_glob : bpy.props.StringProperty(
        default="*.exr",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
        )

    def execute(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        file_path = self.filepath
        folder_path = os.path.split(file_path)[0]
        file_name = os.path.splitext(bpy.path.basename(file_path))[0]
        project_name = re.split('\d+$', file_name)[0]
        image = bpy.data.images.load(file_path)
        #check if there is a project number suffix
        if file_name[0].isdigit(): 
            project_number = re.split('(^\d+)', file_name)[1]+"-"
        else:
            project_number = ''

        self.report({'OPERATOR'}, "file path: " + file_path)
        self.report({'OPERATOR'}, "file name: "+ file_name)
        self.report({'OPERATOR'}, "folder: "+ folder_path)
        self.report({'OPERATOR'}, "project name: "+ project_name)
        self.report({'OPERATOR'}, "project number: "+ project_number)

        #search for minimum and maximum frames
        list_of_files = os.listdir(folder_path)
        frame_max = frame_min = int(re.split('(\d+$)', file_name)[1])

        for file in list_of_files:
            #print(file)
            if os.path.splitext(file)[1].lower() == ".exr":
                num = int(re.split('(\d+)(?=\.exr$)', file, flags = re.I)[1])  # assuming filename is "filexxx.exr"
                #compare num to previous max, e.g.
                frame_max = num if num > frame_max else frame_max  
                frame_min = num if num < frame_min else frame_min
    
        self.report({'OPERATOR'},"max= "+ str(frame_max))
        self.report({'OPERATOR'},"min= "+ str(frame_min))

        #create nodes 
        curr_scene.use_nodes = True
        curr_scene.node_tree.use_opencl = True
        tree_nodes = curr_scene.node_tree.nodes
        tree_links = curr_scene.node_tree.links
        tree_nodes.clear() #delete all nodes

        ##image node
        node_image = tree_nodes.new(type = 'CompositorNodeImage')
        node_image.name = 'SRTI_IMAGE'
        node_image.location = (0,0)
        node_image.image = image
        if not node_image.has_layers:
            self.report({'ERROR'}, "Image is not valid.")
            curr_scene.use_nodes = False
            return{'CANCELLED'}
        node_image.layer = 'View Layer'
        image.source = 'SEQUENCE'
        node_image.use_auto_refresh = True
        node_image.frame_duration = frame_max

        ##Normal nodes
        #Normal multiply 0.5
        node_normal_mult = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_normal_mult.name = 'SRTI_NORMAL_MULT'
        node_normal_mult.label = 'NORMAL_MULT'
        node_normal_mult.location = (300,500)
        node_normal_mult.blend_type = 'MULTIPLY'
        node_normal_mult.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['Normal'],node_normal_mult.inputs[1])
        node_normal_mult.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
                
        #Normal add 0.5
        node_normal_add = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_normal_add.name = 'SRTI_NORMAL_ADD'
        node_normal_add.label = 'NORMAL_ADD'
        node_normal_add.location = (480,500)
        node_normal_add.blend_type = 'ADD'
        node_normal_add.inputs[0].default_value = 1
        tree_links.new(node_normal_mult.outputs[0],node_normal_add.inputs[1])
        node_normal_add.inputs[2].default_value = (0.5, 0.5, 0.5, 1)

        ##Material Index
        #divide IndexMA by 65535
        node_index_div = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_index_div.name = 'SRTI_INDEX_DIV'
        node_index_div.label = 'INDEX_DIV'
        node_index_div.location = (300,300)
        node_index_div.blend_type = 'DIVIDE'
        node_index_div.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['IndexMA'],node_index_div.inputs[1])
        node_index_div.inputs[2].default_value = (65535, 65535, 65535, 1)

        ##intermediate nodes
        #DIFF
        node_diff = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_diff.name = 'SRTI_DIFF'
        node_diff.label = 'DIFF'
        node_diff.location = (300,20)
        node_diff.blend_type = 'MULTIPLY'
        node_diff.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['DiffDir'],node_diff.inputs[1])
        tree_links.new(node_image.outputs['DiffCol'],node_diff.inputs[2])

        #INDIFF
        node_indiff = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_indiff.name = 'SRTI_INDIFF'
        node_indiff.label = 'INDIFF'
        node_indiff.location = (460, -60)
        node_indiff.blend_type = 'MULTIPLY'
        node_indiff.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['DiffInd'],node_indiff.inputs[1])
        tree_links.new(node_image.outputs['DiffCol'],node_indiff.inputs[2])

        #SPEC
        node_spec = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_spec.name = 'SRTI_SPEC'
        node_spec.label = 'SPEC'
        node_spec.location = (620,-140)
        node_spec.blend_type = 'MULTIPLY'
        node_spec.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['GlossDir'],node_spec.inputs[1])
        tree_links.new(node_image.outputs['GlossCol'],node_spec.inputs[2])

        #INSPEC
        node_inspec = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_inspec.name = 'SRTI_INSPEC'
        node_inspec.label = 'INSPEC'
        node_inspec.location = (780,-220)
        node_inspec.blend_type = 'MULTIPLY'
        node_inspec.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['GlossInd'],node_inspec.inputs[1])
        tree_links.new(node_image.outputs['GlossCol'],node_inspec.inputs[2])

        #DIFF-INDIFF
        node_fiff_c = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_fiff_c.name = 'SRTI_DIFF-INDIFF'
        node_fiff_c.label = 'DIFF-INDIFF'
        node_fiff_c.location = (940,20)
        node_fiff_c.blend_type = 'ADD'
        node_fiff_c.inputs[0].default_value = 1
        tree_links.new(node_diff.outputs[0],node_fiff_c.inputs[1])
        tree_links.new(node_indiff.outputs[0],node_fiff_c.inputs[2])
                
        #DIFF-SPEC-INDIFF-INSPEC
        node_spec_c = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_spec_c.name = 'SRTI_DIFF-SPEC-INDIFF-INSPEC'
        node_spec_c.label = 'DIFF-SPEC-INDIFF-INSPEC'
        node_spec_c.location = (1420,-220)
        node_spec_c.blend_type = 'ADD'
        node_spec_c.inputs[0].default_value = 1
        tree_links.new(node_spec.outputs[0],node_spec_c.inputs[1])
        tree_links.new(node_inspec.outputs[0],node_spec_c.inputs[2])

        ##Outputs node
        #OUT_NORMAL
        node_out_normal = tree_nodes.new(type = 'CompositorNodeOutputFile')
        node_out_normal.name = 'SRTI_OUT_NORMAL'
        node_out_normal.label = 'OUT_SINGLE'
        node_out_normal.location = (660, 400)
        node_out_normal.file_slots.clear()
        node_out_normal.file_slots.new(project_name + "NORMAL-")
        tree_links.new(node_normal_add.outputs[0],node_out_normal.inputs[0])
        node_out_normal.file_slots.new(project_name + "MATID-")
        tree_links.new(node_index_div.outputs[0],node_out_normal.inputs[1])
        node_out_normal.base_path = os.path.abspath(folder_path + "\..\PNG")
        node_out_normal.format.file_format = 'PNG'
        node_out_normal.format.color_mode = 'RGB'
        node_out_normal.format.color_depth = '16'
        node_out_normal.format.compression = 0

        #OUT_COMPOSITE
        node_out_composite = tree_nodes.new(type = 'CompositorNodeOutputFile')
        node_out_composite.name = 'SRTI_OUT_COMPOSITE'
        node_out_composite.label = 'OUT_COMPOSITE'
        node_out_composite.location = (1640, 0)
        node_out_composite.file_slots.clear()
        node_out_composite.file_slots.new(project_number + "COMB\\"+project_name+"COMB-")
        tree_links.new(node_image.outputs["Combined"],node_out_composite.inputs[0])
        node_out_composite.file_slots.new(project_number + "DIFF\\"+project_name+"DIFF-")
        tree_links.new(node_fiff_c.outputs[0],node_out_composite.inputs[1])
        node_out_composite.file_slots.new(project_number + "SPEC\\"+project_name+"SPEC-")
        tree_links.new(node_spec_c.outputs[0],node_out_composite.inputs[2])
        node_out_composite.file_slots.new(project_number + "SHADOWS\\"+project_name+"SHADOWS-")
        tree_links.new(node_image.outputs["Shadow"],node_out_composite.inputs[3])
        node_out_composite.base_path = os.path.abspath(folder_path + "\..\PNG")
        node_out_composite.format.file_format = 'PNG'
        node_out_composite.format.color_mode = 'RGB'
        node_out_composite.format.color_depth = '16'
        node_out_composite.format.compression = 0

        #need a folder to save images
        curr_scene.render.filepath = os.path.abspath(folder_path + "\..\PNG\\tmp")+"\\tmp"
        curr_scene.render.resolution_percentage = 1

        #enable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = True
        curr_scene.frame_end = frame_max
        curr_scene.frame_start = 1
        
        #set output format
        curr_scene.render.image_settings.file_format = 'PNG'
        curr_scene.render.image_settings.color_mode = 'RGB'
        curr_scene.render.image_settings.color_depth = '16'
        curr_scene.render.image_settings.compression = 0

        #set color management to linear
        curr_scene.display_settings.display_device = 'None'
        
        #set rendering to not overwrrite
        curr_scene.render.use_overwrite = True

        return{'FINISHED'}

class SRTI_OT_export_normals(bpy.types.Operator):
    """Export a normal map image PNG 16 bit linear."""
    bl_idname = "srti.export_normals"
    bl_label = "Export ID and normals"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.scene.node_tree == None or context.scene.node_tree.nodes.find("SRTI_OUT_COMPOSITE") == -1 or context.scene.node_tree.nodes.find("SRTI_OUT_NORMAL") == -1:
            return False
        else: 
            return True

    def execute(self, context):
        curr_scene = context.scene
        node_out_composite = curr_scene.node_tree.nodes["SRTI_OUT_COMPOSITE"]
        node_out_normal = curr_scene.node_tree.nodes["SRTI_OUT_NORMAL"]
        
        #mute composite output
        node_out_composite.mute = True
        node_out_normal.mute = False
        curr_scene.frame_current = 1

        #set output format
        curr_scene.render.image_settings.file_format = 'PNG'
        curr_scene.render.image_settings.color_mode = 'RGB'
        curr_scene.render.image_settings.color_depth = '16'
        curr_scene.render.image_settings.compression = 0

        #enable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = True

        #set color management to linear
        curr_scene.display_settings.display_device = 'None'
        
        #set rendering to overwrrite
        curr_scene.render.use_overwrite = True
 
        #render normal
        bpy.ops.render.render("INVOKE_DEFAULT")
        #bpy.ops.render.view_cancel()

        return{'FINISHED'}

class SRTI_OT_export_composite(bpy.types.Operator):
    """Export all composite images. (! It may take time !)"""
    bl_idname = "srti.export_composite"
    bl_label = "Export Composite"
    bl_options = {'REGISTER'}
        
    @classmethod
    def poll(cls, context):
        if context.scene.node_tree == None or context.scene.node_tree.nodes.find("SRTI_OUT_COMPOSITE") == -1 or context.scene.node_tree.nodes.find("SRTI_OUT_NORMAL") == -1:
            return False
        else: 
            return True

    def execute(self, context):
        curr_scene = context.scene
        node_out_composite = curr_scene.node_tree.nodes["SRTI_OUT_COMPOSITE"]
        node_out_normal = curr_scene.node_tree.nodes["SRTI_OUT_NORMAL"]
        
        #mute normal output
        node_out_normal.mute = True
        node_out_composite.mute = False
        curr_scene.frame_current = 1
        
        #enable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = True

        #render composite animation
        bpy.ops.render.render("INVOKE_DEFAULT", animation = True, write_still=False)
        return{'FINISHED'}

class SRTI_OT_delete_nodes(bpy.types.Operator):
    """Reset compositing workspace deleting all nodes."""
    bl_idname = "srti.delete_nodes"
    bl_label = "Delete Nodes"
    bl_options = {'REGISTER', 'UNDO' }

    @classmethod
    def poll(cls, context):
        return context.scene.node_tree != None

    def execute(self, context):
        #reset all to normal
        curr_scene = context.scene
        set_render_exr(context)
        curr_scene.node_tree.nodes.clear()
        curr_scene.render.resolution_percentage = 100
        return{'FINISHED'}

class SRTI_OT_subdivide_sets(bpy.types.Operator):
    """Subdivide rendered and exported images sets in multiple folder, one for each material combination."""
    bl_idname = 'srti.subdivide_sets'
    bl_label = 'Subdivide Sets'
    bl_options = {'REGISTER'}

    def execute(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props

        csvpath = bpy.path.abspath(props.T_SF_input_file)
        origin_f = bpy.path.abspath(props.T_SF_origin_folder)
        output_f = bpy.path.abspath(props.T_SF_output_folder)
        mode = props.T_SF_mode
        cr_files = props.T_SF_create_csv
        recursive = props.T_SF_recursive
        addfilename = props.T_SF_additional_filename

        if csvpath == '*.csv' or origin_f == '' or output_f == '':
            self.report({'ERROR'}, 'Missing inputs!')
            return {'CANCELLED'}
        else:
            print('='*40)
            print("||\n|| -- Begin subdivide file --")
            print("|| CSV file: %s"%csvpath)
            print("|| Origin folder: %s"%origin_f)
            print("|| Output Folder: %s"%output_f)
            print("|| Mode: %s"%mode)
            print("|| Recursive folders: %s"%recursive)
            print("|| Create files: %s"%cr_files)
            print("|| Additional file name: %s\n||"%addfilename)

            #open csv file
            csvfile = open(csvpath, newline='')
            reader = csv.reader(csvfile, delimiter=',')
                  
            #prepare list of keys of values
            params = next(reader)[4:]
            params_num = len(params)
            print("|| Found %i parameters:"%params_num)
            print(params)
            
            #load all rows to enable multiple reads
            csvrows = []
            for row in reader:
                csvrows.append(row)
                
            csvfile.close()
            
            #load all folders
            folders = []
 
            if recursive:
                folderlist = os.listdir(origin_f)
                for folder in folderlist:
                    fold = os.path.normpath(origin_f+"/"+folder)
                    if os.path.isdir(fold):
                        folders.append(folder)
            else:
                folders.append("/.")
            
            #store errors number
            err_num = 0
            
            #Loop for all folders
            for fold in folders:  
                sub_origin_f = os.path.normpath(origin_f+fold)
                sub_output_f = os.path.normpath(output_f+fold)
                
                print("||")
                print('='*40)
                print("|  | Origin: %s"%sub_origin_f)
                print("|  | Output: %s"%sub_output_f)
                print("|  |"+'-'*40)
                #get files list
                filelist = os.listdir(sub_origin_f)
                if filelist:
                
                    #obtaing file structure number and extension from first file aviable
                    firstfileelements = filelist[0].split('-')
                    numandext = firstfileelements[-1].split('.')
                    
                    #calculate number length
                    numlength = len(numandext[0])
                    print("|  | File number length: %i"%numlength)
                    
                    #get file extension
                    filext = numandext[1]
                    print("|  | File ext: %s"%filext)
                    
                    #recreate file name
                    filename = "-".join(filelist[0].split('-')[:-1])
                    print("|  | File name: %s"%filename)
                    
                    #check if parameters combination's folder already exist
                    parameter_old = ""
                    
                    #additional file
                    addfile = False
                    
                    #files copy/move loop
                    for row in csvrows:
                        parameter = filename
                        for index in range(0,params_num):
                            parameter += "-"+params[index] +"_"+ row[index+4]

                        if(parameter != parameter_old):  
                            new_dir = os.path.normpath(sub_output_f+"/"+parameter) 
                            print("|  | Parameter: %s"%parameter[len(filename)+1:])
                            
                            #need tocheck if already exist
                            try:
                                os.makedirs(new_dir)
                            except FileExistsError as why:
                                print('>>>> Folder already exist! Error: %s'%why)
                                err_num += 1
                                
                            #close old file if open
                            if addfile:
                                addfile.close()
                            
                            #create additional file if create additional files is selected
                            if cr_files:
                                addfile = open(os.path.normpath(sub_output_f+"/"+parameter+"/"+addfilename), "w")
                                       
                            parameter_old = parameter
                            
                        
                            
                        index = row[0].split('-')[-1]
                        file = filename+"-"+num_to_fixed_len_str(int(index),numlength)+"."+filext
                        
                        #create file path
                        file_origin = os.path.normpath(sub_origin_f+"/"+file)
                        file_output = os.path.normpath(sub_output_f+"/"+parameter+"/"+file)
                        #print(file_origin)
                        #print(file_output)
                        
                        #copy or move the files with error handlings
                        try:
                            if mode == "copy":
                                shutil.copyfile(file_origin,file_output)
                            else:
                                shutil.move(file_origin,file_output)
                            
                            #Add image to the file
                            if addfile:
                                addfile.write("%s,%s,%s,%s\n"%(row[1],row[2],row[3],file))
                                
                        except FileNotFoundError as why:
                            print('>>>> File not found! Error: %s'%why)
                            err_num += 1
                else:
                    print('>>>> No files found on %s!'%sub_origin_f)
                    err_num += 1
                print('='*40)
                
            if err_num:
                self.report({'WARNING'}, '%i warnings found! Look in console for details.'%err_num)
                      
            return {'FINISHED'}


classes = (SRTI_OT_export_as_lamp, SRTI_OT_create_export_node, SRTI_OT_export_normals, SRTI_OT_export_composite, SRTI_OT_delete_nodes, SRTI_OT_subdivide_sets)
register, unregister = bpy.utils.register_classes_factory(classes)


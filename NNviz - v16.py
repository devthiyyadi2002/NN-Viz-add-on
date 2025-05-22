# progress 16 custom world color added 

import bpy
import math
import random
from bpy.props import (
    IntProperty, FloatProperty, EnumProperty,
    CollectionProperty, PointerProperty, FloatVectorProperty, BoolProperty, StringProperty
)
from bpy.types import PropertyGroup, Operator, Panel
from mathutils import Vector
from colorsys import hsv_to_rgb

bl_info = {
    "name": "3D Neural Network Visualizer",
    "author": "Dev Thiyyadi",
    "version": (1, 25),  # Added world color option
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > NN Viz",
    "description": "Visualize simple neural networks (CNN/ANN) in 3D",
    "category": "Object",
}

class LayerSettings(PropertyGroup):
    name: StringProperty(name="Layer Name", default="Layer")
    color: FloatVectorProperty(name="Layer Color", subtype='COLOR', size=4,
        default=(1.0, 0.5, 0.5, 1.0), min=0.0, max=1.0)
    neuron_count: IntProperty(name="Neurons", default=1, min=1, max=1024)
    grid_rows: IntProperty(name="Grid Rows", default=0, min=0)
    grid_cols: IntProperty(name="Grid Columns", default=0, min=0)
    neuron_size: FloatProperty(name="Neuron Size", default=0.3, min=0.01)
    layer_spacing: FloatProperty(name="Layer Spacing", default=0.0, min=0.0)
    cube_roundness: FloatProperty(name="Cube Roundness", default=0.0, min=0.0, max=1.0)
    randomize_color: BoolProperty(name="Randomize Colors", default=False)
    color_variance: FloatProperty(name="Color Variance", default=0.3, min=0.0, max=1.0)

class NNVisualizerProperties(PropertyGroup):
    layer_count: IntProperty(name="Number of Layers", default=3, min=1, max=10)
    neuron_shape: EnumProperty(name="Neuron Shape",
        items=[('SPHERE','Sphere',''),('CUBE','Cube',''),('CYLINDER','Cylinder','')],
        default='SPHERE')
    use_even_spacing: BoolProperty(name="Even Spacing", default=False)
    spacing: FloatProperty(name="Global Spacing", default=2.0, min=0.5)
    total_width: FloatProperty(name="Total Width", default=5.0, min=1.0)
    align_to_ground: BoolProperty(name="Align to Ground", default=True)
    add_stage: BoolProperty(name="Add Stage", default=False)
    stage_radius: FloatProperty(name="Stage Radius", default=5.0, min=0.1)
    stage_color: FloatVectorProperty(name="Stage Color", subtype='COLOR', size=4,
        default=(0.2, 0.2, 0.2, 1.0), min=0.0, max=1.0)
    enable_lighting: BoolProperty(name="Enable Lighting", default=False)
    camera_radius: FloatProperty(name="Camera Circle Radius", default=0.0, min=0.0)
    show_connections: BoolProperty(name="Show Connections", default=False)
    connection_thickness: FloatProperty(name="Connection Thickness", default=0.02, min=0.001)
    connection_opacity: FloatProperty(name="Connection Opacity", default=0.5, min=0.0, max=1.0)
    connection_color_mode: EnumProperty(name="Connection Color",
        items=[('UNIFORM','Uniform','All connections same color'),
               ('RANDOM','Random','Random colors for each connection'),
               ('LAYER','Layer Based','Color based on connected layers')],
        default='UNIFORM')
    connection_color: FloatVectorProperty(name="Base Color", subtype='COLOR', size=4,
        default=(0.8, 0.8, 0.8, 1.0), min=0.0, max=1.0)
    connection_color_variance: FloatProperty(name="Color Variance", default=0.3, min=0.0, max=1.0)
    use_world_color: BoolProperty(name="Use World Color", default=False)
    world_color: FloatVectorProperty(name="World Color", subtype='COLOR', size=4,
        default=(0.05, 0.05, 0.05, 1.0), min=0.0, max=1.0)
    layer_settings: CollectionProperty(type=LayerSettings)

    def randomize_colors(self, context):
        for ls in self.layer_settings[:self.layer_count]:
            if ls.randomize_color:
                base_color = ls.color
                for i in range(3):
                    variation = random.uniform(-ls.color_variance, ls.color_variance)
                    ls.color[i] = max(0.0, min(1.0, base_color[i] + variation))

class OBJECT_OT_generate_nn(Operator):
    bl_idname = "object.generate_nn"
    bl_label = "Generate Network"
    bl_description = "Create neurons, connections, camera rig, optional stage, and lighting"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        props = context.scene.nn_viz_props
        
        props.randomize_colors(context)
        
        if "NN_Vis" in bpy.data.collections:
            old = bpy.data.collections["NN_Vis"]
            for o in list(old.objects): bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(old)
        col = bpy.data.collections.new("NN_Vis")
        context.scene.collection.children.link(col)
        
        # Set world color if enabled
        if props.use_world_color:
            if not context.scene.world:
                context.scene.world = bpy.data.worlds.new("NN_World")
            context.scene.world.use_nodes = False
            context.scene.world.color = props.world_color[:3]
        
        while len(props.layer_settings) < props.layer_count:
            props.layer_settings.add()
        while len(props.layer_settings) > props.layer_count:
            props.layer_settings.remove(len(props.layer_settings)-1)
            
        default_step = props.total_width/(props.layer_count-1) if (props.use_even_spacing and props.layer_count>1) else props.spacing
        x_positions = [0.0]
        for i in range(1, props.layer_count):
            ls = props.layer_settings[i]
            step = ls.layer_spacing if ls.layer_spacing > 0 else default_step
            x_positions.append(x_positions[i-1] + step)
            
        all_layers = []
        prev_cy = prev_cz = 0.0
        
        for idx, ls in enumerate(props.layer_settings[:props.layer_count]):
            neurons = []
            count = ls.neuron_count
            rows = 1 if ls.grid_rows==1 else (ls.grid_rows or int(count**0.5+0.999))
            cols = count if ls.grid_rows==1 else (ls.grid_cols or int(count**0.5+0.999))
            grid_step = ls.neuron_size * 2 * 1.2
            x = x_positions[idx]
            y_pos = [(c - cols/2 + 0.5) * grid_step for c in range(cols)]
            z_pos = [(r - rows/2 + 0.5) * grid_step for r in range(rows)]
            cy = (min(y_pos) + max(y_pos)) / 2 if cols else 0.0
            cz = (min(z_pos) + max(z_pos)) / 2 if rows else 0.0
            off_y, off_z = prev_cy - cy, prev_cz - cz
            shift_z = 0.0
            
            if props.align_to_ground:
                extent = ls.neuron_size if props.neuron_shape!='CUBE' else ls.neuron_size/2
                shift_z = extent - (min(z_pos) + off_z)
                
            for i in range(count):
                r, c = divmod(i, cols)
                loc = Vector((x, y_pos[c] + off_y, z_pos[r] + off_z + shift_z))
                if props.neuron_shape=='SPHERE':
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=ls.neuron_size, location=loc)
                elif props.neuron_shape=='CUBE':
                    bpy.ops.mesh.primitive_cube_add(size=ls.neuron_size, location=loc)
                else:
                    bpy.ops.mesh.primitive_cylinder_add(radius=ls.neuron_size, depth=ls.neuron_size*2, location=loc)
                    
                ob = context.active_object
                if props.neuron_shape=='CUBE' and ls.cube_roundness>0:
                    mod = ob.modifiers.new('Bevel','BEVEL')
                    mod.width=ls.cube_roundness*ls.neuron_size
                    mod.segments=4
                ob.name = f"{ls.name}_{i}"
                
                mat = bpy.data.materials.new(f"{ls.name}_Mat")
                if ls.randomize_color:
                    color = [max(0.0, min(1.0, ls.color[j] + random.uniform(-ls.color_variance, ls.color_variance))) 
                            for j in range(3)]
                    color.append(ls.color[3])
                    mat.diffuse_color = color
                else:
                    mat.diffuse_color = ls.color
                    
                ob.data.materials.append(mat)
                col.objects.link(ob)
                neurons.append(ob)
                
            prev_cy, prev_cz = cy + off_y, cz + off_z + shift_z
            all_layers.append(neurons)
            
        if props.show_connections:
            for layer_idx, (a_layer, b_layer) in enumerate(zip(all_layers, all_layers[1:])):
                for a in a_layer:
                    for b in b_layer:
                        curve = bpy.data.curves.new('Conn','CURVE')
                        curve.dimensions='3D'
                        sp = curve.splines.new('POLY')
                        sp.points.add(1)
                        sp.points[0].co = (*a.location,1)
                        sp.points[1].co = (*b.location,1)
                        curve.bevel_depth = props.connection_thickness
                        conn = bpy.data.objects.new('Connection', curve)
                        
                        matc = bpy.data.materials.new('ConnMat')
                        if props.connection_color_mode == 'UNIFORM':
                            color = list(props.connection_color[:3]) + [props.connection_opacity]
                            matc.diffuse_color = color
                        elif props.connection_color_mode == 'RANDOM':
                            hue = random.random()
                            saturation = 0.7 + random.uniform(-0.2, 0.2)
                            value = 0.8 + random.uniform(-0.2, 0.2)
                            r, g, b = hsv_to_rgb(hue, saturation, value)
                            matc.diffuse_color = (r, g, b, props.connection_opacity)
                        elif props.connection_color_mode == 'LAYER':
                            a_color = a.active_material.diffuse_color
                            b_color = b.active_material.diffuse_color
                            blended = [(a_color[i] + b_color[i])/2 for i in range(3)]
                            matc.diffuse_color = (*blended, props.connection_opacity)
                            
                        matc.blend_method='BLEND'
                        matc.use_nodes=False
                        conn.data.materials.append(matc)
                        col.objects.link(conn)
                        
        min_co, max_co = Vector((1e6,1e6,1e6)), Vector((-1e6,-1e6,-1e6))
        for layer in all_layers:
            for o in layer:
                for v in o.bound_box:
                    w = o.matrix_world @ Vector(v)
                    min_co.x, min_co.y = min(min_co.x,w.x), min(min_co.y,w.y)
                    max_co.x, max_co.y = max(max_co.x,w.x), max(max_co.y,w.y)
        center = (min_co + max_co)/2
        auto_r = max(max_co.x-min_co.x, max_co.y-min_co.y)/2 * 1.2
        bpy.ops.curve.primitive_bezier_circle_add(
            radius=(props.camera_radius if props.camera_radius>0 else auto_r), 
            location=center)
        rig = context.active_object
        rig.name='CameraRig'
        
        if context.scene.camera:
            cam = context.scene.camera
        else:
            bpy.ops.object.camera_add()
            cam = context.active_object
            context.scene.camera=cam
        cam.parent = rig
        cam.location = (center.x+auto_r, center.y, center.z+auto_r*0.5)
        tr = cam.constraints.new('TRACK_TO')
        tr.target=rig
        tr.track_axis='TRACK_NEGATIVE_Z'
        tr.up_axis='UP_Y'
        
        if props.add_stage and props.align_to_ground:
            bpy.ops.mesh.primitive_circle_add(
                radius=props.stage_radius, 
                fill_type='NGON', 
                location=(center.x, center.y, 0))
            stage = context.active_object
            stage.name='NN_Stage'
            mat_s = bpy.data.materials.new('StageMat')
            mat_s.diffuse_color = props.stage_color
            stage.data.materials.append(mat_s)
            col.objects.link(stage)
            
        if props.enable_lighting:
            radius = props.camera_radius if props.camera_radius > 0 else auto_r
            light_height = auto_r * 0.8
            
            angles = [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]
            for angle in angles:
                lx = center.x + radius * math.cos(angle)
                ly = center.y + radius * math.sin(angle)
                bpy.ops.object.light_add(type='POINT', location=(lx, ly, light_height))
                light = context.active_object
                light.data.energy = 1000
                light.parent = rig
                col.objects.link(light)
                
        return {'FINISHED'}

class VIEW3D_PT_nn_viz(Panel):
    bl_label="NN Visualizer"
    bl_idname="VIEW3D_PT_nn_viz"
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category="NN Viz"
    
    def draw(self, context):
        l = self.layout
        p = context.scene.nn_viz_props
        
        # World settings at the top
        box = l.box()
        box.prop(p, "use_world_color", text="Custom World Color")
        if p.use_world_color:
            box.prop(p, "world_color", text="")
        
        # Main settings
        l.prop(p, "layer_count")
        l.prop(p, "neuron_shape")
        l.prop(p, "use_even_spacing")
        if p.use_even_spacing:
            l.prop(p, "total_width")
        else:
            l.prop(p, "spacing")
        l.prop(p, "align_to_ground")
        l.prop(p, "add_stage")
        if p.add_stage:
            l.prop(p, "stage_radius")
            l.prop(p, "stage_color")
        l.prop(p, "enable_lighting")
        l.prop(p, "show_connections")
        if p.show_connections:
            box = l.box()
            box.prop(p, "connection_thickness")
            box.prop(p, "connection_opacity")
            box.prop(p, "connection_color_mode", text="Color Mode")
            if p.connection_color_mode == 'UNIFORM':
                box.prop(p, "connection_color", text="Color")
            elif p.connection_color_mode == 'RANDOM':
                box.prop(p, "connection_color_variance", text="Variance")
        l.prop(p, "camera_radius")
        l.label(text='Layer Settings:')
        
        for i, ls in enumerate(p.layer_settings[:p.layer_count]):
            b = l.box()
            b.prop(ls, 'name')
            b.prop(ls, 'neuron_count')
            b.prop(ls, 'grid_rows')
            b.prop(ls, 'grid_cols')
            row = b.row()
            row.prop(ls, 'color')
            row.prop(ls, 'randomize_color', text="", icon='RNDCURVE')
            if ls.randomize_color:
                b.prop(ls, 'color_variance')
            b.prop(ls, 'neuron_size')
            if i > 0:
                b.prop(ls, 'layer_spacing')
            if p.neuron_shape == 'CUBE':
                b.prop(ls, 'cube_roundness')
        l.operator('object.generate_nn', icon='MESH_UVSPHERE')

classes = (LayerSettings, NNVisualizerProperties, OBJECT_OT_generate_nn, VIEW3D_PT_nn_viz)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.nn_viz_props = PointerProperty(type=NNVisualizerProperties)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.nn_viz_props

if __name__ == '__main__':
    register()
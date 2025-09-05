import bpy # type: ignore
import os
import math

print("Script started")

# Set output directory
output_dir = r"D:\Uni\Work\3rd Year\R&D\OutPut Textures\Cubemap"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print("Output directory created")

# Get the camera
camera_name = "Cubemap_Camera"
camera = bpy.data.objects.get(camera_name)
if not camera:
    print(f"ERROR: Camera '{camera_name}' not found!")
    exit()

# Set render settings
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.image_settings.file_format = 'PNG'
scene.render.use_file_extension = True

# Define camera rotations for each frame
camera_rotations = {
    1: (0, 0, 0),                     
    2: (0, math.radians(180), 0),     
    3: (0, math.radians(90), 0),      
    4: (0, math.radians(-90), 0),     
    5: (math.radians(-90), 0, 0),     
    6: (math.radians(90), 0, 0)       
}

# Apply keyframes for each frame (camera rotation)
for frame, rotation in camera_rotations.items():
    camera.rotation_euler = rotation
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    print(f"Keyframe set for frame {frame}")

# Ensure compositor is active and reset it for normal rendering
scene.use_nodes = True
tree = scene.node_tree

# Remove old nodes (compositor reset)
for node in tree.nodes:
    tree.nodes.remove(node)

# Add the Render Layer node to connect with the compositor
render_layer_node = tree.nodes.new(type="CompositorNodeRLayers")
render_layer_node.location = (-200, 0)

# Composite output node
composite_node = tree.nodes.new(type="CompositorNodeComposite")
composite_node.location = (600, 0)
composite_node.use_alpha = True

# Link the Render Layer node to the composite node
tree.links.new(render_layer_node.outputs["Image"], composite_node.inputs["Image"])

# Render each frame
for frame in range(1, 7):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    
    # Set file path for each rendered frame
    output_path = os.path.join(output_dir, f"Render_Frame_{frame}.png")
    scene.render.filepath = output_path
    print(f"Rendering frame {frame} to {output_path}...")

    # Render and save
    bpy.ops.render.render(write_still=True)

print("ALL cubemap images rendered successfully!")



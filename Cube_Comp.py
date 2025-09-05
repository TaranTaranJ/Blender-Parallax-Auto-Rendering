import bpy # type: ignore
import os

print("Starting cubemap compositing...")

# Set output directory
output_dir = r"D:\Uni\Work\3rd Year\R&D\OutPut Textures\Cubemap"
final_image_path = os.path.join(output_dir, "Render_Final.png")

Image_Tile_Size = 1024

# Ensure compositor is active
scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree

# Remove any existing nodes
for node in tree.nodes:
    tree.nodes.remove(node)

# Load the six cubemap face images
images = {}
for i in range(1, 7):
    image_path = os.path.join(output_dir, f"Render_Frame_{i}.png")
    images[i] = bpy.data.images.load(image_path)

# Create image nodes for each cubemap face
image_nodes = {}
for i in range(1, 7):
    image_nodes[i] = tree.nodes.new(type="CompositorNodeImage")
    image_nodes[i].image = images[i]
    image_nodes[i].location = (-600, 200 - (i * 150))  # Arrange nodes vertically

# Create a blank image with resolution 4096x3072 for the final cubemap
final_image_width = Image_Tile_Size * 2
final_image_height = Image_Tile_Size * 3
final_image = bpy.data.images.new("Cubemap_Final", width=final_image_width, height=final_image_height)

# Create an image node for the final cubemap
final_image_node = tree.nodes.new(type="CompositorNodeImage")
final_image_node.image = final_image
final_image_node.location = (600, 0)

# Create a blank image node for the base (4096x3072)
blank_image_node = tree.nodes.new(type="CompositorNodeImage")
blank_image_node.image = bpy.data.images.new("Blank_Cubemap", width=final_image_width, height=final_image_height)
blank_image_node.location = (-1000, 0)

# Overlay the cubemap faces using "Alpha Over" and "Translate" nodes to move them into place

# Function to create a Translate node for a given cubemap face with specific position
def create_translate_node(image_node, x, y):
    translate_node = tree.nodes.new(type="CompositorNodeTranslate")
    translate_node.location = (image_node.location[0] + 400, image_node.location[1])  # Position translate nodes
    translate_node.inputs[1].default_value = x  # X position
    translate_node.inputs[2].default_value = y  # Y position
    tree.links.new(image_node.outputs["Image"], translate_node.inputs[0])  # Link image to translate node
    return translate_node

# Apply translate for each image to position it correctly

# Front - position (0, 0)
translate_front = create_translate_node(image_nodes[1], -512, -1024)

# Back - position (1024, 0)
translate_back = create_translate_node(image_nodes[2], 512, -1024)

# Right - position (0, 1024)
translate_right = create_translate_node(image_nodes[3], -512, 0)

# Left - position (1024, 1024)
translate_left = create_translate_node(image_nodes[4], 512, 0)

# Top - position (0, 2048)
translate_top = create_translate_node(image_nodes[5], -512, 1024)

# Bottom - position (1024, 2048)
translate_bottom = create_translate_node(image_nodes[6], 512, 1024)

# Now overlay the translated images using "Alpha Over" nodes

# Combine Front + Back
alpha_over_1 = tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_over_1.location = (1500, 0)
tree.links.new(blank_image_node.outputs["Image"], alpha_over_1.inputs[1])  # Blank base
tree.links.new(translate_front.outputs["Image"], alpha_over_1.inputs[2])  # Front image

# Combine Front + Back into a single layer
alpha_over_2 = tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_over_2.location = (1500, -200)
tree.links.new(alpha_over_1.outputs["Image"], alpha_over_2.inputs[1])  # Combine Front with Back
tree.links.new(translate_back.outputs["Image"], alpha_over_2.inputs[2])  # Back image

# Combine Front + Back with Right
alpha_over_3 = tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_over_3.location = (1500, -400)
tree.links.new(alpha_over_2.outputs["Image"], alpha_over_3.inputs[1])  # Combine Front + Back
tree.links.new(translate_right.outputs["Image"], alpha_over_3.inputs[2])  # Right image

# Combine Front + Back + Right with Left
alpha_over_4 = tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_over_4.location = (1500, -600)
tree.links.new(alpha_over_3.outputs["Image"], alpha_over_4.inputs[1])  # Combine Front + Back + Right
tree.links.new(translate_left.outputs["Image"], alpha_over_4.inputs[2])  # Left image

# Combine Front + Back + Right + Left with Top
alpha_over_5 = tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_over_5.location = (1500, -800)
tree.links.new(alpha_over_4.outputs["Image"], alpha_over_5.inputs[1])  # Combine Front + Back + Right + Left
tree.links.new(translate_top.outputs["Image"], alpha_over_5.inputs[2])  # Top image

# Combine Front + Back + Right + Left + Top with Bottom
alpha_over_6 = tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_over_6.location = (1500, -1000)
tree.links.new(alpha_over_5.outputs["Image"], alpha_over_6.inputs[1])  # Combine Front + Back + Right + Left + Top
tree.links.new(translate_bottom.outputs["Image"], alpha_over_6.inputs[2])  # Bottom image

# Create a File Output node to save the final image
file_output_node = tree.nodes.new(type="CompositorNodeOutputFile")
file_output_node.location = (2000, -1000)
file_output_node.base_path = output_dir
file_output_node.file_slots[0].path = "Render_Final"  # Output filename (Render_Final.png)
file_output_node.format.file_format = 'PNG'

# Link the final composited image to the File Output node
tree.links.new(alpha_over_6.outputs["Image"], file_output_node.inputs["Image"])

print(f"Final cubemap saved to {final_image_path}")




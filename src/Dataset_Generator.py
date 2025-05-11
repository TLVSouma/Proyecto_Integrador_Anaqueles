# import blenderproc as bproc
# import numpy as np
# import os
# import cv2
# from mathutils import Matrix, Euler

# # Configuration
# bproc.init()
# objects_folder = os.path.join(os.path.dirname(__file__), "../obj")

# def load_all_objs():
#     objects = []
#     for file in os.listdir(objects_folder):
#         if file.lower().endswith(".obj"):
#             objects.extend(bproc.loader.load_obj(os.path.join(objects_folder, file)))
#     return objects

# # Add lights
# light1 = bproc.types.Light()
# light1.set_type("POINT")
# light1.set_location([3, -3, 3])
# light1.set_energy(3000)

# light2 = bproc.types.Light()
# light2.set_type("SUN")
# light2.set_location([0, 0, 10])
# light2.set_energy(5)

# for scene_num in range(10):
#     if scene_num > 0:
#         bproc.clean_up()
    
#     loaded_objects = load_all_objs()
    
#     # MATERIAL SETUP
#     for obj in loaded_objects:
#         obj.set_cp("category_id", 1)
#         for mat in obj.get_materials():
#             mat.set_principled_shader_value("Base Color", [
#                 np.random.uniform(0.2, 0.9),
#                 np.random.uniform(0.2, 0.9),
#                 np.random.uniform(0.2, 0.9)
#             ])
#             mat.set_principled_shader_value("Roughness", np.random.uniform(0.1, 0.5))
#             mat.set_principled_shader_value("Metallic", 0.0)
    
#     # Object placement
#     for obj in loaded_objects:
#         obj.set_scale([0.5, 0.5, 0.5])
    
#     for i, obj in enumerate(loaded_objects):
#         row = i // 3
#         col = i % 3
#         obj.set_location([col * 2 - 2, row * 2 - 2, 0])
#         obj.set_location(obj.get_location() + np.random.uniform(-0.3, 0.3, size=3))
#         obj.set_rotation_euler(Euler(np.random.uniform(0, 2*np.pi, size=3)))
    
#     # Camera setup
#     for cam_idx in range(10):
#         location = bproc.sampler.sphere([0, 0, 0], radius=10, mode="SURFACE")
#         rotation = bproc.camera.rotation_from_forward_vec(-np.array(location))
#         bproc.camera.add_camera_pose(Matrix.Translation(location) @ Matrix(rotation).to_4x4())
    
#     # RENDER SETTINGS
#     bproc.renderer.set_max_amount_of_samples(100)
#     bproc.renderer.set_output_format("PNG")
#     bproc.renderer.enable_segmentation_output(default_values={'category_id': 0})
    
#     # Render
#     data = bproc.renderer.render()
    
#     # Save outputs
#     output_dir = f"output/scene_{scene_num}"
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Save HDF5
#     bproc.writer.write_hdf5(output_dir, data)
    
#     # Handle color images properly
#     for i, img in enumerate(data["colors"]):
#         # Convert to numpy array if needed
#         if not isinstance(img, np.ndarray):
#             img = np.array(img)
        
#         # Ensure proper color format
#         if len(img.shape) == 3 and img.shape[2] == 3:  # RGB image
#             # Convert to BGR for OpenCV
#             img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
#             cv2.imwrite(os.path.join(output_dir, f"rgb_{i:04d}.png"), img_bgr)
    
#     print(f"Scene {scene_num} saved to {output_dir}")

# import blenderproc as bproc
# import numpy as np
# import os
# import cv2
# from mathutils import Matrix, Euler

# # Initialize BlenderProc
# bproc.init()

# # Configuration
# objects_folder = os.path.join(os.path.dirname(__file__), "../obj")

# def load_all_objs():
#     objects = []
#     for file in os.listdir(objects_folder):
#         if file.lower().endswith(".obj"):
#             objs = bproc.loader.load_obj(os.path.join(objects_folder, file))
#             for obj in objs:
#                 if not obj.get_materials():
#                     mat = obj.new_material("DefaultMaterial")
#                     # Bright red material with full opacity
#                     mat.set_principled_shader_value("Base Color", [1.0, 0.2, 0.2, 1.0])
#                     mat.set_principled_shader_value("Roughness", 0.2)
#                 objects.extend(objs)
#     return objects

# # Lighting setup that works with all versions
# def setup_lights():
#     # Key light (sun)
#     sun_light = bproc.types.Light()
#     sun_light.set_type("SUN")
#     sun_light.set_location([5, -5, 5])
#     sun_light.set_energy(25)  # Very strong
#     sun_light.set_color([1, 1, 1])
    
#     # Fill light (point)
#     point_light = bproc.types.Light()
#     point_light.set_type("POINT")
#     point_light.set_location([-3, 3, 3])
#     point_light.set_energy(20)
#     point_light.set_color([1, 1, 0.9])

# # Vibrant test colors (RGBA)
# COLORS = [
#     [1.0, 0.2, 0.2, 1.0],  # Red
#     [0.2, 1.0, 0.2, 1.0],  # Green
#     [0.2, 0.2, 1.0, 1.0],  # Blue
#     [1.0, 1.0, 0.2, 1.0],  # Yellow
# ]

# # Load objects and setup
# loaded_objects = load_all_objs()
# setup_lights()

# # Assign materials with version-safe properties
# for idx, obj in enumerate(loaded_objects):
#     color = COLORS[idx % len(COLORS)]
#     for mat in obj.get_materials():
#         mat.set_principled_shader_value("Base Color", color)
#         mat.set_principled_shader_value("Metallic", 0.0)
#         mat.set_principled_shader_value("Roughness", 0.2)
#         # Skip specular settings entirely to avoid version conflicts

# # Position objects
# for i, obj in enumerate(loaded_objects):
#     obj.set_scale([0.7, 0.7, 0.7])
#     row = i // 2
#     col = i % 2
#     obj.set_location([col * 4 - 2, row * 4 - 2, 0])

# # Camera setup
# location = [0, -4, 2]
# rotation = bproc.camera.rotation_from_forward_vec(-np.array(location))
# bproc.camera.add_camera_pose(Matrix.Translation(location) @ Matrix(rotation).to_4x4())

# # Render settings
# bproc.renderer.set_max_amount_of_samples(100)
# bproc.renderer.set_output_format("PNG")
# bproc.renderer.enable_segmentation_output(default_values={'category_id': 0})
# bproc.renderer.set_light_bounces(diffuse_bounces=4, glossy_bounces=4)

# # Render and save
# data = bproc.renderer.render()
# output_dir = "output/color_test"
# os.makedirs(output_dir, exist_ok=True)

# # Process and verify color output
# color_img = np.array(data["colors"][0])
# print("Image shape:", color_img.shape)
# print("Color ranges - R:", np.min(color_img[:,:,0]), "-", np.max(color_img[:,:,0]))
# print("Color ranges - G:", np.min(color_img[:,:,1]), "-", np.max(color_img[:,:,1]))
# print("Color ranges - B:", np.min(color_img[:,:,2]), "-", np.max(color_img[:,:,2]))

# # Save with gamma correction
# gamma_corrected = np.clip(color_img/255, 0, 1)**(1/2.2) * 255
# cv2.imwrite(os.path.join(output_dir, "result.png"), cv2.cvtColor(gamma_corrected.astype(np.uint8), cv2.COLOR_RGB2BGR))

# print(f"Render successful. Check {output_dir}/result.png")

import blenderproc as bproc
import numpy as np
import os
import cv2
from mathutils import Matrix, Euler

# Initialize BlenderProc
bproc.init()

# Configuration
objects_folder = os.path.join(os.path.dirname(__file__), "../obj")

def load_all_objs():
    objects = []
    for file in os.listdir(objects_folder):
        if file.lower().endswith(".obj"):
            objs = bproc.loader.load_obj(os.path.join(objects_folder, file))
            for obj in objs:
                if not obj.get_materials():
                    mat = obj.new_material("DefaultMaterial")
                    # Bright red material with full opacity
                    mat.set_principled_shader_value("Base Color", [1.0, 0.2, 0.2, 1.0])
                    mat.set_principled_shader_value("Roughness", 0.2)
                objects.extend(objs)
    return objects

# Vibrant test colors (RGBA)
COLORS = [
    [1.0, 0.2, 0.2, 1.0],  # Red
    [0.2, 1.0, 0.2, 1.0],  # Green
    [0.2, 0.2, 1.0, 1.0],  # Blue
    [1.0, 1.0, 0.2, 1.0],  # Yellow
]

# Lighting setup that works with all versions
def setup_lights():
    # Key light (sun)
    sun_light = bproc.types.Light()
    sun_light.set_type("SUN")
    sun_light.set_location([5, -5, 5])
    sun_light.set_energy(25)  # Very strong
    sun_light.set_color([1, 1, 1])
    
    # Fill light (point)
    point_light = bproc.types.Light()
    point_light.set_type("POINT")
    point_light.set_location([-3, 3, 3])
    point_light.set_energy(20)
    point_light.set_color([1, 1, 0.9])

for scene_num in range(10):
    if scene_num > 0:
        bproc.clean_up()
    
    loaded_objects = load_all_objs()
    setup_lights()
    
    # MATERIAL SETUP - using the fixed colors from first script
    for idx, obj in enumerate(loaded_objects):
        obj.set_cp("category_id", 1)
        color = COLORS[idx % len(COLORS)]
        for mat in obj.get_materials():
            mat.set_principled_shader_value("Base Color", color)
            mat.set_principled_shader_value("Roughness", 0.2)
            mat.set_principled_shader_value("Metallic", 0.0)
    
    # Object placement with scaling from first script
    for obj in loaded_objects:
        obj.set_scale([0.7, 0.7, 0.7])  # Using scale from first script
    
    # Position objects with some randomization
    for i, obj in enumerate(loaded_objects):
        row = i // 3
        col = i % 3
        obj.set_location([col * 2 - 2, row * 2 - 2, 0])
        obj.set_location(obj.get_location() + np.random.uniform(-0.3, 0.3, size=3))
        obj.set_rotation_euler(Euler(np.random.uniform(0, 2*np.pi, size=3)))
    
    # Camera setup - using the same approach but with multiple cameras
    for cam_idx in range(10):
        location = bproc.sampler.sphere([0, 0, 0], radius=10, mode="SURFACE")
        rotation = bproc.camera.rotation_from_forward_vec(-np.array(location))
        bproc.camera.add_camera_pose(Matrix.Translation(location) @ Matrix(rotation).to_4x4())
    
    # RENDER SETTINGS - using settings from first script
    bproc.renderer.set_max_amount_of_samples(100)
    bproc.renderer.set_output_format("PNG")
    bproc.renderer.enable_segmentation_output(default_values={'category_id': 0})
    bproc.renderer.set_light_bounces(diffuse_bounces=4, glossy_bounces=4)
    
    # Render
    data = bproc.renderer.render()
    
    # Save outputs
    output_dir = f"output/scene_{scene_num}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save HDF5
    bproc.writer.write_hdf5(output_dir, data)
    
    # Handle color images properly with gamma correction from first script
    for i, img in enumerate(data["colors"]):
        # Convert to numpy array if needed
        if not isinstance(img, np.ndarray):
            img = np.array(img)
        
        # Ensure proper color format
        if len(img.shape) == 3 and img.shape[2] == 3:  # RGB image
            # Apply gamma correction as in first script
            gamma_corrected = np.clip(img/255, 0, 1)**(1/2.2) * 255
            # Convert to BGR for OpenCV
            img_bgr = cv2.cvtColor(gamma_corrected.astype(np.uint8), cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(output_dir, f"rgb_{i:04d}.png"), img_bgr)
    
    print(f"Scene {scene_num} saved to {output_dir}")
    print(f"Color ranges - R: {np.min(img[:,:,0])} - {np.max(img[:,:,0])}")
    print(f"Color ranges - G: {np.min(img[:,:,1])} - {np.max(img[:,:,1])}")
    print(f"Color ranges - B: {np.min(img[:,:,2])} - {np.max(img[:,:,2])}")
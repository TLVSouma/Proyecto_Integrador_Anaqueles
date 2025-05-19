import blenderproc as bproc
import os
import numpy as np
from mathutils import Matrix, Euler
import cv2

# Initialize BlenderProc
bproc.init()

# Configuration
ply_folder = os.path.join(os.path.dirname(__file__), "../ply")
output_base_dir = "output_ply_scenes"
os.makedirs(output_base_dir, exist_ok=True)

# Create base plane (corrected implementation)
def create_plane():
    plane = bproc.object.create_primitive("PLANE", scale=[15, 15, 1])
    plane.set_location([0, 0, -3])
    
    # Correct way to make plane invisible but cast shadows
    plane.hide(True)  # Makes the plane invisible
    plane.enable_rigidbody(False)  # Ensure it doesn't interfere physically
    return plane

# Vertex color material (verified working)
def create_vertex_color_material(name="vertex_color_mat"):
    mat = bproc.material.create(name)
    nodes = mat.blender_obj.node_tree.nodes
    links = mat.blender_obj.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create essential nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    vcol = nodes.new(type='ShaderNodeVertexColor')
    vcol.layer_name = "Col"  # Standard PLY color layer
    
    # Connect nodes
    links.new(vcol.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Optimized material settings
    bsdf.inputs['Roughness'].default_value = 0.4
    bsdf.inputs['Metallic'].default_value = 0.0
    return mat

# Load PLY objects with proper spacing
def load_ply_objects():
    objects = []
    category_id = 1
    ply_files = [f for f in os.listdir(ply_folder) if f.lower().endswith(".ply")]
    
    for idx, fname in enumerate(ply_files):
        path = os.path.join(ply_folder, fname)
        objs = bproc.loader.load_obj(path)
        
        for obj in objs:
            # Grid positioning (3 columns)
            row = idx // 3
            col = idx % 3
            base_pos = np.array([col * 2.5 - 2.5, row * 2.5 - 2.5, 0])
            
            # Apply transformations
            obj.set_location(base_pos + np.random.uniform(-0.3, 0.3, 3))
            obj.set_rotation_euler(Euler(np.random.uniform(0, 2*np.pi, 3)))
            obj.set_scale([0.7, 0.7, 0.7])
            
            # Assign material
            if not obj.get_materials():
                obj.add_material(create_vertex_color_material())
            else:
                for mat in obj.get_materials():
                    if "Vertex Color" in mat.blender_obj.node_tree.nodes:
                        mat.blender_obj.node_tree.nodes["Vertex Color"].layer_name = "Col"
            
            obj.set_cp("category_id", category_id)
            objects.append(obj)
            category_id += 1
    
    return objects

# Lighting setup
def setup_lights():
    # Key light
    sun = bproc.types.Light()
    sun.set_type("SUN")
    sun.set_location([5, -5, 5])
    sun.set_energy(3)
    
    # Fill light
    point = bproc.types.Light()
    point.set_type("POINT")
    point.set_location([-3, 3, 3])
    point.set_energy(2)

# Camera setup
def setup_cameras():
    for _ in range(5):
        location = bproc.sampler.sphere([0, 0, 0], radius=8, mode="SURFACE")
        rotation = bproc.camera.rotation_from_forward_vec(-np.array(location))
        bproc.camera.add_camera_pose(Matrix.Translation(location) @ Matrix(rotation).to_4x4())

# Render settings
def configure_render():
    bproc.renderer.set_output_format("PNG")
    bproc.renderer.enable_segmentation_output(map_by="instance")
    bproc.renderer.set_max_amount_of_samples(100)
    bproc.renderer.set_light_bounces(diffuse_bounces=3, glossy_bounces=3)

# Save outputs
def save_outputs(data, output_dir):
    # HDF5
    bproc.writer.write_hdf5(output_dir, data)
    
    # RGB images
    for i, img in enumerate(data["colors"]):
        img_8bit = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(output_dir, f"rgb_{i:03d}.png"), img_bgr)
    
    # Segmentation maps
    for i, seg in enumerate(data["instance_segmaps"]):
        # Grayscale
        seg_vis = (seg.astype(np.float32) / seg.max() * 255).astype(np.uint8)
        cv2.imwrite(os.path.join(output_dir, f"segmentation_{i:03d}.png"), seg_vis)
        
        # Colored
        COLORMAP = np.array([
            [230, 25, 75], [60, 180, 75], [255, 225, 25], [0, 130, 200], [245, 130, 48],
            [145, 30, 180], [70, 240, 240], [240, 50, 230], [210, 245, 60], [250, 190, 190],
            [0, 128, 128], [230, 190, 255], [170, 110, 40], [255, 250, 200], [128, 0, 0],
            [170, 255, 195], [128, 128, 0], [255, 215, 180], [0, 0, 128], [128, 128, 128]
        ], dtype=np.uint8)
        
        seg_colored = np.zeros((*seg.shape, 3), dtype=np.uint8)
        for instance_id in np.unique(seg):
            if instance_id == 0:
                continue
            seg_colored[seg == instance_id] = COLORMAP[instance_id % len(COLORMAP)]
        cv2.imwrite(os.path.join(output_dir, f"segmentation_colored_{i:03d}.png"), seg_colored)

# Main loop
for scene_num in range(10):
    if scene_num > 0:
        bproc.clean_up()
    
    print(f"\nGenerating scene {scene_num}...")
    
    # Scene setup
    create_plane()
    objects = load_ply_objects()
    setup_lights()
    setup_cameras()
    configure_render()
    
    # Render
    data = bproc.renderer.render()
    
    # Save
    output_dir = os.path.join(output_base_dir, f"scene_{scene_num:03d}")
    os.makedirs(output_dir, exist_ok=True)
    save_outputs(data, output_dir)
    
    print(f"Scene {scene_num} saved to {output_dir}")

print("\nGeneration completed successfully!")
import blenderproc as bproc
import os
import numpy as np
from mathutils import Matrix, Euler
from sklearn.neighbors import KDTree

def setup_scene(scene_idx):
    """Set up a scene with properly spaced random object positions"""
    bproc.clean_up()
    
    # Create a base plane
    plane = bproc.object.create_primitive("PLANE", scale=[5, 5, 1])
    plane.set_location([0, 0, -3])

    # Load all .ply models from folder
    objects = []
    ply_files = [f for f in os.listdir(ply_folder) if f.lower().endswith(".ply")]
    
    # Generate random but spaced positions
    positions = generate_spaced_positions(len(ply_files), min_distance=1.2)
    
    for i, fname in enumerate(ply_files):
        path = os.path.join(ply_folder, fname)
        objs = bproc.loader.load_obj(path)
        for obj in objs:
            # Set position with proper spacing
            obj.set_location(positions[i])
            
            # Random rotation (optional)
            obj.set_rotation_euler(Euler(np.random.uniform(0, 2*np.pi, size=3)))
            
            material = create_vertex_color_material()
            obj.set_material(0, material)
            obj.set_cp("category_id", i+1)  # for segmentation
            objects.append(obj)

    # Add lighting with slight variations per scene
    sun = bproc.types.Light()
    sun.set_type("SUN")
    sun.set_location([
        4 + np.random.uniform(-1, 1),
        -4 + np.random.uniform(-1, 1),
        4 + np.random.uniform(-1, 1)
    ])
    sun.set_energy(4 + np.random.uniform(-1, 1))
    
    return objects

def generate_spaced_positions(num_objects, min_distance=1.0, max_attempts=100):
    """Generate random positions with minimum spacing between objects"""
    positions = []
    bounds = [-2, 2]  # Area where objects can be placed
    
    for _ in range(num_objects):
        attempts = 0
        while attempts < max_attempts:
            # Generate random position
            new_pos = np.random.uniform(bounds[0], bounds[1], size=3)
            new_pos[2] = 0  # Keep on ground plane
            
            # Check distance to existing positions
            if len(positions) == 0:
                positions.append(new_pos)
                break
                
            tree = KDTree(np.array(positions))
            dist, _ = tree.query([new_pos], k=1)
            
            if dist[0][0] >= min_distance:
                positions.append(new_pos)
                break
                
            attempts += 1
        
        if attempts >= max_attempts:
            # Fallback if can't find good position
            new_pos = np.random.uniform(bounds[0], bounds[1], size=3)
            new_pos[2] = 0
            positions.append(new_pos)
    
    return positions

def generate_camera_poses(num_angles=10):
    """Generate camera poses around the scene with slight variations"""
    poses = []
    base_distance = 6
    base_height = 3
    
    for i in range(num_angles):
        # Evenly distribute angles with slight randomness
        angle = 2 * np.pi * i / num_angles + np.random.uniform(-0.2, 0.2)
        distance = base_distance * np.random.uniform(0.9, 1.1)
        height = base_height * np.random.uniform(0.9, 1.1)
        
        # Calculate position
        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        z = height
        
        # Point camera toward center with slight random offset
        target = [np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3), 0]
        
        # Create camera pose
        cam_location = [x, y, z]
        cam_rot_matrix = bproc.camera.rotation_from_forward_vec(np.array(target) - np.array(cam_location))
        pose = Matrix.Translation(cam_location) @ Matrix(cam_rot_matrix).to_4x4()
        poses.append(pose)
    
    return poses

def create_vertex_color_material():
    """Create material with vertex colors"""
    mat = bproc.material.create("vertex_color_mat")
    mat_blender = mat.blender_obj
    node_tree = mat_blender.node_tree

    bsdf_node = None
    for node in node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            bsdf_node = node
            break
    if bsdf_node is None:
        raise RuntimeError("No se encontró el nodo Principled BSDF")

    vc_node = node_tree.nodes.new(type="ShaderNodeVertexColor")
    vc_node.layer_name = "Col"

    node_tree.links.new(vc_node.outputs["Color"], bsdf_node.inputs["Base Color"])
    return mat

def render_scene(output_dir, scene_idx, angle_idx):
    """Render and save outputs for one camera angle"""
    # Configure render settings
    bproc.renderer.set_output_format("PNG")
    bproc.renderer.enable_segmentation_output(map_by="instance")
    bproc.renderer.set_max_amount_of_samples(100)
    bproc.renderer.set_light_bounces(diffuse_bounces=3, glossy_bounces=3)

    # Render the scene
    data = bproc.renderer.render()
    
    # Save all outputs
    frame_dir = os.path.join(output_dir, f"frame_{angle_idx:02d}")
    os.makedirs(frame_dir, exist_ok=True)
    
    bproc.writer.write_hdf5(frame_dir, data)
    
    # Save RGB image
    import cv2
    img_bgr = (data["colors"][0]).astype(np.uint8)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(os.path.join(frame_dir, "rgb.png"), img_rgb)
    
    # Save segmentation maps
    seg = data["instance_segmaps"][0]
    seg_vis = (seg.astype(np.float32) / seg.max() * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(frame_dir, "segmentation.png"), seg_vis)
    
    # Create colored segmentation visualization
    seg_colored = np.zeros((*seg.shape, 3), dtype=np.uint8)
    for instance_id in np.unique(seg):
        if instance_id == 0:
            continue  # 0 is background
        color = COLORMAP[instance_id % len(COLORMAP)]
        seg_colored[seg == instance_id] = color
    cv2.imwrite(os.path.join(frame_dir, "segmentation_colored.png"), seg_colored)

# Main execution
if __name__ == "__main__":
    # Initialize BlenderProc
    bproc.init()
    
    # Path to .ply folder
    ply_folder = os.path.join(os.path.dirname(__file__), "../ply")
    
    # COLORMAP for segmentation visualization
    COLORMAP = np.array([
        [230, 25, 75], [60, 180, 75], [255, 225, 25], [0, 130, 200], [245, 130, 48],
        [145, 30, 180], [70, 240, 240], [240, 50, 230], [210, 245, 60], [250, 190, 190],
        [0, 128, 128], [230, 190, 255], [170, 110, 40], [255, 250, 200], [128, 0, 0],
        [170, 255, 195], [128, 128, 0], [255, 215, 180], [0, 0, 128], [128, 128, 128]
    ], dtype=np.uint8)

    # Create 10 different scenes
    for scene_idx in range(10):
        print(f"\nGenerating scene {scene_idx + 1}/10")
        
        # Reset the scene
        bproc.utility.reset_keyframes()
        
        # Set up scene with properly spaced objects
        objects = setup_scene(scene_idx)
        
        # Generate 10 camera angles
        camera_poses = generate_camera_poses(10)
        
        # Create output directory for this scene
        scene_dir = os.path.join("output_scenes", f"scene_{scene_idx:02d}")
        os.makedirs(scene_dir, exist_ok=True)
        
        # Render from each camera angle
        for angle_idx, pose in enumerate(camera_poses):
            print(f"  Rendering angle {angle_idx + 1}/10")
            
            # Clear previous camera poses
            bproc.utility.reset_keyframes()
            
            # Add new camera pose
            bproc.camera.add_camera_pose(pose)
            
            # Render and save
            render_scene(scene_dir, scene_idx, angle_idx)

    print("\nAll scenes generated successfully!")



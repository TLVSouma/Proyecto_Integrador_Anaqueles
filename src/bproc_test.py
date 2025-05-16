import blenderproc as bproc
import os
import numpy as np
from mathutils import Matrix, Euler

# Inicializa BlenderProc
bproc.init()

# Ruta a la carpeta con los modelos .ply
ply_folder = os.path.join(os.path.dirname(__file__), "../ply")

# Crea un plano base para colocar los objetos
plane = bproc.object.create_primitive("PLANE", scale=[5, 5, 1])
plane.set_location([0,0,-3])

# Crea material con vertex color (usando nodos manualmente)
def create_vertex_color_material():
    # Crear material con BlenderProc
    mat = bproc.material.create("vertex_color_mat")

    # Acceder al nodo tree de Blender
    mat_blender = mat.blender_obj
    node_tree = mat_blender.node_tree

    # Buscar el nodo Principled BSDF (por nombre o tipo)
    bsdf_node = None
    for node in node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            bsdf_node = node
            break
    if bsdf_node is None:
        raise RuntimeError("No se encontró el nodo Principled BSDF")

    # Crear nodo Vertex Color
    vc_node = node_tree.nodes.new(type="ShaderNodeVertexColor")
    vc_node.layer_name = "Col"  # nombre por defecto para vertex colors en PLY

    # Conectar Vertex Color al Base Color del BSDF
    node_tree.links.new(vc_node.outputs["Color"], bsdf_node.inputs["Base Color"])

    return mat

# Cargar todos los modelos .ply desde carpeta
objects = []
i = 1
for fname in os.listdir(ply_folder):
    if fname.lower().endswith(".ply"):
        path = os.path.join(ply_folder, fname)
        objs = bproc.loader.load_obj(path)
        for obj in objs:
            
            obj.set_location(np.random.uniform(-1.5, 1.5, size=3))
            obj.set_rotation_euler(Euler(np.random.uniform(0, 2 * np.pi, size=3)))
            material = create_vertex_color_material()
            obj.set_material(0, material)
            obj.set_cp("category_id", i)  # para segmentación
            i+=1
            objects.append(obj)

# Agrega luz
sun = bproc.types.Light()
sun.set_type("SUN")
sun.set_location([5, -5, 5])
sun.set_energy(5)

# Cámara fija
cam_location = [5.0, -5.0, 3.0]
cam_target = [0, 0, 0]
cam_rot_matrix = bproc.camera.rotation_from_forward_vec(np.array(cam_target) - np.array(cam_location))
cam_pose = Matrix.Translation(cam_location) @ Matrix(cam_rot_matrix).to_4x4()
bproc.camera.add_camera_pose(cam_pose)

# Configurar render
bproc.renderer.set_output_format("PNG")
bproc.renderer.enable_segmentation_output(map_by="instance")
bproc.renderer.set_max_amount_of_samples(100)
bproc.renderer.set_light_bounces(diffuse_bounces=3, glossy_bounces=3)

# Renderizar
data = bproc.renderer.render()

# Guardar imágenes
output_dir = "output_ply_vertex"
os.makedirs(output_dir, exist_ok=True)
bproc.writer.write_hdf5(output_dir, data)

# Guardar imagen RGB
import cv2
img_bgr = (data["colors"][0]).astype(np.uint8)
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
cv2.imwrite(os.path.join(output_dir, "rgb.png"), img_rgb)

# Guardar segmentación por instancia
seg = data["instance_segmaps"][0]
seg_vis = (seg.astype(np.float32) / seg.max() * 255).astype(np.uint8)
cv2.imwrite(os.path.join(output_dir, "segmentation_instance.png"), seg_vis)

# Crear colormap de 20 colores únicos (tipo tab20)
COLORMAP = np.array([
    [230, 25, 75], [60, 180, 75], [255, 225, 25], [0, 130, 200], [245, 130, 48],
    [145, 30, 180], [70, 240, 240], [240, 50, 230], [210, 245, 60], [250, 190, 190],
    [0, 128, 128], [230, 190, 255], [170, 110, 40], [255, 250, 200], [128, 0, 0],
    [170, 255, 195], [128, 128, 0], [255, 215, 180], [0, 0, 128], [128, 128, 128]
], dtype=np.uint8)

# Crear imagen RGB con color por instancia
seg_colored = np.zeros((*seg.shape, 3), dtype=np.uint8)
for instance_id in np.unique(seg):
    if instance_id == 0:
        continue  # 0 is background
    color = COLORMAP[instance_id % len(COLORMAP)]
    seg_colored[seg == instance_id] = color

cv2.imwrite(os.path.join(output_dir, "segmentation_instance_colored.png"), seg_colored)

print(f"Render completado. Resultados guardados en: {output_dir}")

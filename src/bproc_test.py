import blenderproc as bproc
import os
import random

# Inicializa BlenderProc
bproc.init()

# Luz principal
sun = bproc.types.Light()
sun.set_type("SUN")
sun.set_location([5, 5, 5])
sun.set_energy(4)

# Crea un plano base
plane = bproc.object.create_primitive("PLANE", scale=[2, 2, 1])
mat_plane = bproc.material.create("plain")
plane.set_material(mat_plane)

# Función para crear material con vertex color usando nodos
def create_vertex_color_material():
    mat = bproc.types.Material()
    mat.new("vertex_color_mat")

    # Crear nodos manualmente
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    # Agregar nodo de Vertex Color
    vc_node = mat.node_tree.nodes.new(type="ShaderNodeVertexColor")
    vc_node.layer_name = "Col"  # nombre por defecto del canal

    # Conectar vertex color a base color del shader
    mat.node_tree.links.new(vc_node.outputs["Color"], bsdf.inputs["Base Color"])

    return mat

# Carga modelos .ply desde carpeta
models_dir = "ply"
for fname in os.listdir(models_dir):
    if fname.lower().endswith(".ply"):
        path = os.path.join(models_dir, fname)
        objs = bproc.loader.load_obj(path)
        for obj in objs:
            obj.set_scale_uniform(0.1)
            obj.set_location([random.uniform(-1, 1), random.uniform(-1, 1), 0])

            vc_mat = create_vertex_color_material()
            obj.set_material(vc_mat)

# Cámara estática
bproc.camera.add_camera_pose([
    [1, 0, 0, 0],
    [0, 1, 0, -3],
    [0, 0, 1, 2],
    [0, 0, 0, 1]
])

# IDs para segmentación por instancia
for obj in bproc.object.get_all_mesh_objects():
    obj.set_cp("category_id", 1)
    obj.set_cp("instance_id", obj.get_id())

# Renderizar imágenes y máscaras
bproc.renderer.set_output_format("PNG")
bproc.renderer.enable_segmentation_output(map_by="instance")

bproc.renderer.render("output")

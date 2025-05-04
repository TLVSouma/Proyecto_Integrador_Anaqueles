# import blenderproc as bproc
# import numpy as np
# import os
# from mathutils import Matrix

# # Fix para el error de collections.Sequence
# try:
#     from collections.abc import Sequence
# except ImportError:
#     from collections import Sequence

# def load_all_objs_from_folder(folder_path):
#     """Carga todos los archivos .obj de una carpeta"""
#     all_objects = []
#     category_id = 1  # Empezamos a asignar IDs desde 1
    
#     for file in os.listdir(folder_path):
#         if file.lower().endswith(".obj"):  # Busca .obj en mayúsculas o minúsculas
#             # Carga cada archivo OBJ
#             objects = bproc.loader.load_obj(os.path.join(folder_path, file))
            
#             # Asigna categorías (mismo ID para objetos del mismo archivo)
#             for obj in objects:
#                 obj.set_cp("category_id", category_id)
#                 obj.set_name(f"{os.path.splitext(file)[0]}_{len(all_objects)}")
            
#             all_objects.extend(objects)
#             category_id += 1  # Siguiente categoría
    
#     return all_objects

# # Inicializa BlenderProc
# bproc.init()

# # Construye la ruta a la carpeta obj en el directorio padre
# current_dir = os.path.dirname(os.path.abspath(__file__))  # Ruta del script actual
# parent_dir = os.path.dirname(current_dir)  # Directorio padre
# obj_folder = os.path.join(parent_dir, "obj")  # Ruta a la carpeta obj

# # Verifica que la carpeta exista
# if not os.path.exists(obj_folder):
#     raise Exception(f"No se encontró la carpeta 'obj' en: {parent_dir}")

# # Carga todos los objetos
# loaded_objects = load_all_objs_from_folder(obj_folder)

# if not loaded_objects:
#     raise Exception("No se encontraron archivos .obj en la carpeta especificada!")

# # Configura materiales aleatorios
# for obj in loaded_objects:
#     for material in obj.get_materials():
#         material.set_principled_shader_value("Roughness", np.random.uniform(0, 1))
#         material.set_principled_shader_value("Specular", np.random.uniform(0, 1))

# # Configura iluminación
# light = bproc.types.Light()
# light.set_type("POINT")
# light.set_location([5, -5, 5])
# light.set_energy(1000)

# # Configura cámaras (10 ángulos)
# poses = 10
# for i in range(poses):
#     location = np.array(bproc.sampler.sphere([0, 0, 0], radius=2, mode="SURFACE"))
#     rotation = bproc.camera.rotation_from_forward_vec(-location, inplane_rot=np.random.uniform(0, 2*np.pi))
#     cam2world_matrix = Matrix.Translation(location) @ Matrix(rotation).to_4x4()
#     bproc.camera.add_camera_pose(cam2world_matrix)

# # Configuración de render
# bproc.renderer.set_max_amount_of_samples(50)
# bproc.renderer.set_output_format("PNG")

# # Habilita segmentación
# bproc.renderer.enable_segmentation_output(
#     map_by=["instance", "class"],
#     default_values={'category_id': 0}  # 0 = fondo
# )

# # Renderiza la escena
# data = bproc.renderer.render()

# # Guarda los resultados
# bproc.writer.write_hdf5("output/", data)
# print(f"Escena renderizada con {len(loaded_objects)} objetos desde: {obj_folder}")

import blenderproc as bproc
import numpy as np
import os
from mathutils import Matrix, Euler

# Configuración inicial
bproc.init()
objects_folder = os.path.join(os.path.dirname(__file__), "../obj")  # Carpeta obj en el directorio padre

# Función para cargar objetos
def load_all_objs():
    objects = []
    for file in os.listdir(objects_folder):
        if file.lower().endswith(".obj"):
            objects.extend(bproc.loader.load_obj(os.path.join(objects_folder, file)))
    return objects

# 10 escenas distintas
for scene_num in range(10):
    # Limpia la escena anterior (excepto la primera vez)
    if scene_num > 0:
        bproc.clean_up()
    
    # Carga objetos y asigna materiales
    loaded_objects = load_all_objs()
    for obj in loaded_objects:
        obj.set_cp("category_id", 1)  # Misma categoría para todos (o personaliza)
        for mat in obj.get_materials():
            mat.set_principled_shader_value("Roughness", np.random.uniform(0.1, 0.5))
    
    # Posicionamiento aleatorio de objetos
    for obj in loaded_objects:
        obj.set_location(np.random.uniform(-1, 1, size=3))
        obj.set_rotation_euler(Euler(np.random.uniform(0, 2*np.pi, size=3)))
    
    # 10 ángulos de cámara por escena
    for cam_idx in range(10):
        location = bproc.sampler.sphere([0, 0, 0], radius=3, mode="SURFACE")
        rotation = bproc.camera.rotation_from_forward_vec(-np.array(location))
        bproc.camera.add_camera_pose(Matrix.Translation(location) @ Matrix(rotation).to_4x4())
    
    # Render y guardado
    bproc.renderer.set_output_format("PNG")
    bproc.renderer.enable_segmentation_output(default_values={'category_id': 0})
    data = bproc.renderer.render()
    
    # Carpeta por escena (organización clara)
    output_dir = f"output/scene_{scene_num}"
    os.makedirs(output_dir, exist_ok=True)
    bproc.writer.write_hdf5(output_dir, data)
    print(f"Escena {scene_num} guardada en {output_dir}")
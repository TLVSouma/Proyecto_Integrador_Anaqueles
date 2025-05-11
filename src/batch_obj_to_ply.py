import os

def convert_obj_with_vertex_colors_to_ply(obj_path, ply_path):
    vertices = []
    faces = []

    with open(obj_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                if len(parts) >= 7:
                    x, y, z = map(float, parts[1:4])
                    r, g, b = map(float, parts[4:7])
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                    vertices.append((x, y, z, r, g, b))
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                faces.append(face)

    with open(ply_path, 'w') as f:
        f.write('ply\n')
        f.write('format ascii 1.0\n')
        f.write(f'element vertex {len(vertices)}\n')
        f.write('property float x\n')
        f.write('property float y\n')
        f.write('property float z\n')
        f.write('property uchar red\n')
        f.write('property uchar green\n')
        f.write('property uchar blue\n')
        f.write(f'element face {len(faces)}\n')
        f.write('property list uchar int vertex_indices\n')
        f.write('end_header\n')

        for v in vertices:
            f.write(f'{v[0]} {v[1]} {v[2]} {v[3]} {v[4]} {v[5]}\n')

        for face in faces:
            f.write(f'{len(face)} {" ".join(map(str, face))}\n')

    print(f"✅ {os.path.basename(obj_path)} → {os.path.basename(ply_path)}")


def convert_all_objs_in_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".obj"):
            obj_path = os.path.join(input_folder, filename)
            ply_filename = os.path.splitext(filename)[0] + ".ply"
            ply_path = os.path.join(output_folder, ply_filename)
            convert_obj_with_vertex_colors_to_ply(obj_path, ply_path)


# === USO ===
# Modifica estas rutas según tus carpetas

input_folder = "../obj"
output_folder = "../ply"

convert_all_objs_in_folder(input_folder, output_folder)

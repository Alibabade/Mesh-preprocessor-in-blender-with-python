"""
Mesh Triangulation
run within blender 2.82

This script aims to triangulate the mesh, and 
export the obj filename as:
    file_in[:-4] + '_tri.obj'
"""
import bpy 
import os
import time
import re


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def triangulate_mesh(data_path, dir_names):
    file_ins = []
    #filenames = []
    
    for dir_name in dir_names:
        filenames = os.listdir(os.path.join(data_path, dir_name))
        verts_cnt_max = 0
        idx_max = None
        for idx, filename in enumerate(filenames):
            # only obj with max number of vertex will be triangulated.
            if filename.endswith(".obj") or filename.endswith(".OBJ"):
                if re.search(r'(.*)-(.*)k.obj', filename, re.M|re.I):
                    verts_cnt = int(re.search('-(.+?)k.obj', filenames[idx]).group(1)) 
                    
                    if verts_cnt > verts_cnt_max or (verts_cnt == 0 and verts_cnt_max == 0):
                        verts_cnt_max = verts_cnt
                        idx_max = idx
        if idx_max is not None:         
            file_ins.append(os.path.join(data_path, dir_name, filenames[idx_max]))
        #print(verts_cnt_max, idx_max)
        print(f"    triangulate mesh file_ins: {file_ins}")
        #assert 1 == 0
        
    for file_in in file_ins:     
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)     
        
        bpy.ops.import_scene.obj(filepath=file_in)
        obj = bpy.context.scene.objects[0]
        bpy.context.view_layer.objects.active = obj
        # Perform triangulation
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

        file_out = file_in[:-4] + '_tri.obj'
        bpy.ops.export_scene.obj(filepath=file_out)
    

def main():
    
    root_path = "/media/li/alibaba_2/FILES_OFFICE/github_repos/Python_tools_for_mesh_processing_in_blender/data/"
    dir_names = ['bear']
    start_time = time.time()
    filename = "bbr-45k.obj"
    #file_in = os.path.join(root_path, dir_names)

    triangulate_mesh(root_path, dir_names)
    print('execute time is : %.2f min'%((time.time()-start_time)/60))
    print('Done!')
    
if __name__ == "__main__":
    
    main()
    

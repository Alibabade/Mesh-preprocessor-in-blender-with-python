import bpy 
import os
import bmesh
import re
import time
import bisect
import numpy as np
from random import randint

"""
run within blender 2.8!!!

Data augment for meshes
each mesh produces 1000 arbitrary sub surfaces
Method: Enter 'Object' Mode -> import mesh obj
        -> while loop for data augment
           -> random seed face and wanted face nums
           -> find neighbour faces sharing edges of curr face
           -> preserve found faces for propogation
           -> determine whether selected face nums > wanted face nums 
        -> extract vertex index from selected faces
        -> save vertex index (start with 0) into file (.npy) 

"""
"""
Li Wang
27 June 2020

"""
# read vertex coordinates from obj file
def read_obj(filename):
    obj_file = open(filename, 'r')
    lines = obj_file.readlines()
    vertices = []
    #vertices = np.array([[float(x) for x in np.random.rand(3)]])
    for line in lines:    
        if re.search(r'v (.+?) (.+?) (.+?)', line, re.M|re.I):
            #v = np.array([[ float(x) for x in line[2:-1].split(' ')]])
            #vertices = np.concatenate((vertices,v), axis=0) 
            values = line[2:-1].split(' ')
            vertices.append([ float(x) for x in line[2:-1].split(' ') ])
    #vertices = vertices[1:]
    
    return vertices


def extract_arbitrary_surfaces_from_mesh(data_root, dir_names, nums_surface, min_wanted_faces):

    
    print("start to process mesh...")
    
    mesh_paths = []
    
    
    for dir_name in dir_names:
        filenames = os.listdir(os.path.join(data_root, dir_name))
        for filename in filenames:
            mesh_paths.append(os.path.join(data_root, dir_name, filename))
        
    
            
    for mesh_idx, file_in in enumerate(mesh_paths): 
      # here only triangulated mesh will be processed
      if 'tri.obj' in file_in:
        #relative_path = path[2:-1]  
        print('processing the %dth mesh: %s'%(mesh_idx, file_in) )
        
        
        out_path = os.path.join('/'.join(file_in.split('/')[:-1]), "vertex_indinces_of_arbitrary_surfaces")
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        print(f"    out_path: {out_path}")
        #assert 1 == 0
        #file_in = data_root + relative_path
        
        vertices = read_obj(file_in)
        print('    len vertices: ', len(vertices))
        # get into object model to select obj in the scene
        objs = bpy.context.scene.objects
        if len(objs) > 0:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)


        bpy.ops.import_scene.obj(filepath=file_in)

        # active the imported object
        obj = bpy.context.scene.objects[0]
        mesh = obj.data
        bpy.context.view_layer.objects.active = obj

        # change into edit mode to edit the mesh
        bpy.ops.object.mode_set(mode = 'EDIT')


        bm = bmesh.from_edit_mesh(mesh)

        # this is for ensure_lookup_table for
        # operations like bm.verts[i], bm.faces[i] and bm.edges[i]
        
        if hasattr(bm.verts, "ensure_lookup_table"): 
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()   
            bm.faces.ensure_lookup_table()
        
        
        n_faces = len(bm.faces)
        print('    faces len: ',n_faces)
        
        print('    vertices[0]: ', vertices[0])
        st = time.time()
        # give unique vertex index to b.faces->verts->index
        res = set()
        for f in bm.faces:
            for vtx in f.verts:
                #vtx_co = np.array([vtx.co[0], vtx.co[1], vtx.co[2]])
                #vtx_idx = np.where( (np.abs(vertices-vtx_co)<1e-6 ).all(axis=1) )[0]
                #vtx.index = vtx_idx.item()
                vtx_co = [ float('%.6f'%vtx.co[0]), float('%.6f'%vtx.co[1]), float('%.6f'%vtx.co[2]) ]
                #vtx_idx = find_idx(vertices, vtx_co)
                vtx_idx = vertices.index(vtx_co)
                if vtx_idx not in res:
                    res.add(vtx_idx)
                vtx.index = vtx_idx
                
        print('    len res: ', len(res))        
        print('    give unique index to vertex: %.4f s' %(time.time()-st))
        data_verts = []
        curr_idx = 0
        while curr_idx < nums_surface:
            print('        processing %d th surface...' % (curr_idx))
            # generate a random face to start
            start_face_idx = randint(0, n_faces-1)
            face = bm.faces[start_face_idx]
            for f in bm.faces:
                f.select = False

            #print(face, face.verts[0].index)
            #print('edge.link_faces:', face.edges[0].link_faces)

            # choosing set() is because set is faster than list 
            # when checking if an element (not) in  
            # record the idx of selected faces
            selected_faces = set()
            
            # record  current selected faces
            curr_faces = set()
            curr_faces.add(face)
            # record the selected verts
            selected_verts = set()
            #bmesh.update_edit_mesh(mesh, True)
            #bpy.ops.object.mode_set(mode = 'OBJECT')
            wanted_faces_nums = randint(min_wanted_faces, n_faces)
            print('            wanted faces: ', wanted_faces_nums)
            
            
            previous_selected_faces = set()
            # select random surface via connected faces 
            while len(selected_faces) < wanted_faces_nums:
                previous_selected_faces = selected_faces.copy()
                next_faces = set()
                for f in curr_faces:
                    for edge in f.edges:
                        linked_faces = edge.link_faces
                        for l_f in linked_faces:
                            # only add faces not in selected_faces, next_faces and curr_faces 
                            if l_f not in next_faces:
                                if l_f not in selected_faces :
                                    if l_f not in curr_faces:                           
                                        #face.select = True
                                        next_faces.add(l_f)
                                
                    if f not in selected_faces:
                        selected_faces.add(f)
                        
                curr_faces = next_faces
                
                # this is for detecting if the seed face locates
                # in a loop area in the obj mesh
                # if the len(previous_selected_faces) == curr_selected_face and
                # len(curr_selected_faces) < wanted_faces_nums,which mean the
                # seed face locates in a loop area, then reseed the face                    
                if len(previous_selected_faces) == len(selected_faces):
                    if len(selected_faces) < wanted_faces_nums:
                        start_face_idx = randint(0, n_faces-1)
                        face = bm.faces[start_face_idx]
                        for bmf in bm.faces:
                            bmf.select = False
                        selected_faces = set()
            
                        curr_faces = set()
                        curr_faces.add(face)
                         # record the selected verts
                        selected_verts = set()
            
                        wanted_faces_nums = randint(min_wanted_faces, n_faces)
                        print('            re-wanted faces: ', wanted_faces_nums)
                
            
            print('            selected faces: ',len(selected_faces))
            #print('        selected faces: ',selected_faces.totverts)
            
            for f in selected_faces:
                f.select = True
                #print( '%.6f %.6f %.6f'%(f.verts[0].co[0], f.verts[0].co[1], f.verts[0].co[2]) )
                for v in f.verts:
                    #if v.index not in selected_verts:
                    #print( 'v_co:(%.6f %.6f %.6f)'%(v.co[0], v.co[1], v.co[2]) )
                    #v_co = np.array([v.co[0], v.co[1], v.co[2]])
                    #v_idx = np.where( (np.abs(vertices-v_co)<1e-6 ).all(axis=1) )[0]
                    #v_idx = v_idx.item()
                    #print('v_idx:',v_idx)
                    v_idx = v.index
                    if v_idx not in selected_verts:
                        selected_verts.add(v_idx)
                        #print('vertices %d=(%.6f, %.6f, %.6f) '%(v_idx, vertices[v_idx][0],
                        #                                        vertices[v_idx][1], 
                        #                                        vertices[v_idx][2] ))
            #print('selected verts: ', selected_verts)            
            print('            selected verts:', len(selected_verts))    
            
        
            # save each unseen selected_verts to data_verts
            if selected_verts not in data_verts:
                data_verts.append(selected_verts)
                curr_idx += 1
            bmesh.update_edit_mesh(mesh, True)
            #time.sleep(5)

        
        data_verts_final = np.asarray(data_verts)
        #out_path =  "/media/li/alibaba2/FILES_OFFICE/Researches/" + \
        #            "geometry_texture_synthesis/test_scripts/mesh_autoencoder/data_augment/" + \
        #         dataset_category + "_tri/"
        
        out_file = os.path.join(out_path, file_in.split('/')[-1][:-4] + ".npy") 
        print(f"    out_file: {out_file}")
        if os.path.exists(out_file):
            os.remove(out_file) 
        np.save(out_file, data_verts_final)
    
    
        data_loaded = np.load(out_file, allow_pickle=True)
    
        print('    saved vertex : ', len(data_loaded[0]))
        #print('data: ', data)
        
        # free memory by deleting bm object    
        bm.free()
        
        
        
       
def main():
    data_root = {your_work_path+'/data'}
    #dir_names = 'bear'    
    nums_surface = 2
    min_wanted_faces = 1000
    start_time = time.time()
    extract_arbitrary_surfaces_from_mesh(data_root, \
                                          nums_surface, min_wanted_faces)
    
    print('execute time is : %.2f min'%((time.time()-start_time)/60))
    print('Done!')
    
    
    
if __name__ == '__main__':
    main()
    
    

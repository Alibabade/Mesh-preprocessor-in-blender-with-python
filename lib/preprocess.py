import bpy
import bmesh
import os
import time
import re


"""
Tips
    run within blender 2.8.2!!!

Tish script aims to reduce the vertex number of an obj file
when its vertex number is bigger than a threshold, otherwise, 
do nothing. And rename the exported filename with a format:
    "{}-{}k.obj".format(original_filename, vertex_count//1000)
    
Variables:
    1. verts_thres: exported obj with max vertex count, usually, 200K
    2. verts_max  : reduce vertex number by DECIMATE to verts_thres.   

"""

def preprocess(root_path, dir_names, verts_thres):


    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print(f"start to process preparation for mesh operation...")
    
    """
    dir_names = ['bear', 'bird', 'buddha', 'bull', 'bunny', 'butterfly', \
               'cat', 'cock', 'cow', 'crocodile', \
               'deer', 'dog', 'dolphin', 'dragon', 
               'elephant','fish', 'fox', 'frog', \
               'giraffe', 'goose', 'gorilla', \
               'head', 'horse', 'human_body', 'kangaroo', \
               'lion', 'lizard', 'mix', 'mouse', \
               'panda', 'parrot', 'penguin', 'pig', 'pillow', \
               'rabbit', 'sheep', 'snake', 'squirrel', \
               'tiger', 'turtle', 'whale', 'wolf']
    """
    verts_max = verts_thres * 4 // 3  
    
    file_root = []
    for name in dir_names:
        file_root.append(os.path.join(root_path, name)+"/")
    #print(file_root)
    start_time = time.time()
    for path in file_root:
        for subdir, dirs, files in os.walk(path):
            for file in files:
          
               if file.endswith(".obj") or file.endswith(".OBJ"):
                   if not re.search(r'-(.*)k.obj', file, re.M|re.I):
                       print('file:', file) 
             
                       bpy.ops.object.select_all(action='SELECT')
                       bpy.ops.object.delete(use_global=False)
                       file_in = os.path.join(subdir, file) 
                       print(file_in)

                       bpy.ops.import_scene.obj(filepath=file_in)
  
                       # active the imported object
                       obj = bpy.context.scene.objects[0]
             
                       bpy.context.view_layer.objects.active = obj
                       # get the original vertex count of selected object
                       bm_ori = bmesh.new()
                       depsgraph = bpy.context.evaluated_depsgraph_get()
                       bm_ori.from_object(bpy.context.object, depsgraph)
             
                       v_count_ori = len(bm_ori.verts)
                       print('  ori verts:',v_count_ori)
             

                       if v_count_ori < verts_thres:
                          # rename the name 
                          name = v_count_ori // 1000
                          file_out = file_in[:-4] + "-" + str(name) + "k.obj"
                          print(f"    file_out:{file_out}")
                          #assert 1 == 0
                          if not os.path.exists(file_out):   
                              bpy.ops.export_scene.obj(filepath=file_out)
                          else:
                              print('  file exists.') 
                       elif v_count_ori < verts_max: #66k,132k,199k,266k
                          # reduce the vertex number
                          bpy.ops.object.modifier_add(type='DECIMATE')
                          # process separately according to vertex number
                
                
                          ratio = verts_thres / v_count_ori
                     
                          if ratio > 0.75 and ratio <= 1:
                              bpy.context.object.modifiers["Decimate"].ratio = ratio 
                
                
                          #mod.use_collapse_triangulate=True
                          bm_mod = bmesh.new()
                          depsgraph = bpy.context.evaluated_depsgraph_get()
                          bm_mod.from_object(bpy.context.object, depsgraph)
                          v_count_mod = len(bm_mod.verts)
                          print('  mod verts:',v_count_mod)
                          rough_count = v_count_mod // 1000
                          # save decimated object
                          file_out = file_in[:-4] + "-" + str(rough_count) + "k.obj"
                          if not os.path.exists(file_out):
                             bpy.ops.export_scene.obj(filepath=file_out)
                          else:
                             print('  file exists.')
                
                
    print('run time : {:4f}m'.format((time.time() - start_time)/60))
    print('done!')
    
def main():
    path_to_data = "./data/"
    # change the following variables
    dir_names = ['bear']
    #verts_min = 150000 #50k,100k,150k,200k
    verts_thres = 50000

    preprocess(root_path, dir_names, verts_thres)
       
    
    
    
if __name__ == "__main__":
    main()
    


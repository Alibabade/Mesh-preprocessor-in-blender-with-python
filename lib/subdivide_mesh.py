import os
import bpy
import time
import bmesh
import re

"""
Tips:
    run within blender 2.8.2!!!
    
This script aims to subdivide obj by adding new vertices to
a desired number. And it's capble of processing multiple objs.

Basic idea:
    1. get the vertex count from imported obj file.
    2. set desired vertex count Threshold
    3. subdivide obj until it reachs the closest 
       vertex number to Threshold.
"""

def subdivide_mesh(root_path, dir_names, verts_min, verts_max, verts_threshold):


    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
  
    

    file_root = []
    for name in dir_names:
        file_root.append(os.path.join(root_path, name)+"/")
    print(f"file_root: {file_root}")
    
    start_time = time.time()
    # record the count not produced by subdivision
    iscontinue = 0
    # record the count total reviewed in this subdir
    total_cnt = 0
    first_pass = True

    while (first_pass or iscontinue != total_cnt):
        iscontinue = 0
        total_cnt = 0
        first_pass = False
        for path in file_root:
            for subdir, dirs, files in os.walk(path):
              print('subdir:',subdir) 
              files_underdir = []
              for file in files:
                  # get the files 
                  if file.endswith(".obj") or file.endswith(".OBJ"):
                      if re.search(r'(.*)-(.*)k.obj', file, re.M|re.I):
                          #print(file)
                          files_underdir.append(file)
              print(f"    files_underdir:{files_underdir}")  
                       
              # make sure there is obj file under the dir          
              if (len(files_underdir) > 0):
                  print('    files_underdir:', files_underdir)
                  # find the max vertex number
                  count_max = 0
                  idx = None
                  for i in range(len(files_underdir)):
                      cnt = int(re.search('-(.+?)k.obj', files_underdir[i]).group(1)) 

                      # very important!!!!!!
                      # suitable for [verts_min,verts_max)
                      if cnt >= verts_min and cnt < verts_max:
                          if cnt > count_max or (cnt == 0 and count_max == 0):
                            count_max = cnt
                            idx = i
                  total_cnt += 1
                  if idx is not None:
                    #print('count_max:',count_max)
                    #print('idx: ',idx)
                    num_cnt_in = len(str(count_max))
                    #print('num_cnt_in: ',num_cnt_in)
                    file_in = os.path.join(subdir, files_underdir[idx])
                    print('    file_in:', file_in)
                    # record the count of total processed object
            
                    #"""
                    bpy.ops.object.select_all(action='SELECT')
                    bpy.ops.object.delete(use_global=False)
                    #file_in = os.path.join(subdir, file) 
                    #print(file_in)
  
                    # import obj file into blender
                    bpy.ops.import_scene.obj(filepath=file_in)
  
                    # active the imported object
                    obj = bpy.context.scene.objects[0]
                    bpy.context.view_layer.objects.active = obj
                    # get the original vertex count of selected object
                    bm_ori = bmesh.new()
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    bm_ori.from_object(bpy.context.object, depsgraph)
                    v_count_ori = len(bm_ori.verts)
                    print('    ori verts:',v_count_ori)
              
                    if v_count_ori < verts_threshold: #50k,100k,150k,200k
                        # perform subdivision
                        bpy.ops.object.modifier_add(type='SUBSURF')
                        bpy.context.object.modifiers["Subdivision"].render_levels = 0
                        bpy.context.object.modifiers["Subdivision"].levels = 1

                        #time.sleep(20)
                        bm = bmesh.new()
                        depsgraph = bpy.context.evaluated_depsgraph_get()
                        bm.from_object(bpy.context.object, depsgraph)
                        v_count = len(bm.verts)
                        print('    subdivided verts:',v_count)
               
                        # get the rough count in thousand unit
                        rough_count = v_count // 1000
                        #print(rough_count)
                        # do not produce objects with vertices more than verts_min 
                        if v_count < verts_threshold:
                            print(f"    {rough_count}k vertices")
                            # save processed object
                            file_out = file_in[:-(6+num_cnt_in)] + "-" + str(rough_count) + "k.obj"  
                            print('    file_out:',file_out)
                            if not os.path.exists(file_out):
                                bpy.ops.export_scene.obj(filepath=file_out)
                            else:
                                print('file exists.')
                                iscontinue += 1       
                   
                        else:
                            iscontinue += 1     
                
                    else:
                        iscontinue += 1
                  else:
                    iscontinue += 1
    
  
    if iscontinue == total_cnt:
        print('no more subdivision!')
        print('done!')
        


def main():
    root_path = {your_work_path+'/data'}
    dir_names = ['bear']
    # change the following variables
    verts_min = 0 #represent 9k,50k,100k,150k #9
    verts_max = 150 #represent 50k,100k,150k
    verts_threshold = 200000 #50k,100k,150k,200k
    
    subdivide_mesh(root_path, dir_names, verts_min, verts_max, verts_threshold)
    

if __name__ == "__main__":
    main()
    

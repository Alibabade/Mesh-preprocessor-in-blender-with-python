import bpy
import bmesh
import os
import time
import re
import sys
import argparse


"""
There are four steps for mesh processing in this script, which are:
    1. preprocess				: rename filename into a certen format and 
                                                   reduce vertex number if it's bigger than verts_thres
    2. subdivide_mesh				: subdivide the mesh into desired vertex number,
                                                   or closest vertex number
    3. triangulate_mesh				: triangulate the mesh
    4. generate_arbitrary_surfaces_from_mesh	: extract intact sub-surfaces from the triangulated mesh
"""

class mesh_processer:
    name = "mesh_processer"
    
    def __init__(self, args):
        self.args = args
         
    def process(self):
        #assert 1 == 0
        start_time = time.time()
        if self.args.work_path not in sys.path:
             sys.path.append(self.args.work_path)
        import lib
        from lib.preprocess import preprocess
        from lib.subdivide_mesh import subdivide_mesh
        from lib.triangulate_mesh import triangulate_mesh
        from lib.extract_arbitrary_surfaces_from_mesh import extract_arbitrary_surfaces_from_mesh
        print(preprocess)
        #assert 1 == 0
        if not self.args.skip_preprocess:
            preprocess(self.args.data_path, self.args.mesh_folders, self.args.verts_thres)
        #assert 1 == 0    
        if not self.args.skip_subdivide_mesh:
            subdivide_mesh(self.args.data_path, self.args.mesh_folders, \
                          self.args.verts_min, self.args.verts_max, self.args.verts_thres)
        #assert 1 == 0      
        if not self.args.skip_triangulate_mesh:
            triangulate_mesh(self.args.data_path, self.args.mesh_folders)
        #assert 1 == 0     
        if not self.args.skip_extract_subsurface_from_mesh:
            extract_arbitrary_surfaces_from_mesh(self.args.data_path,self.args.mesh_folders, \
                                                  self.args.nums_surface, self.args.min_wanted_faces)
        
        end_time = time.time()
        print('execute time is : %.2f min'%((end_time-start_time)/60))
        
        
    def start(self):
        self.process()
        
        
def main():
    parser = argparse.ArgumentParser(description='parser for mesh processer')
    # please change work_path to your own work path#########################################################
    work_path = {your_work_path}
    ########################################################################################################
    parser.add_argument("--work_path", type=str, required=False, default = work_path,
                        help="please add the path to your mesh data (.obj format).")
    parser.add_argument("--data_path", type=str, required=False, default = os.path.join(work_path,"data"),
                        help="please add the path to your mesh data (.obj format).")
    parser.add_argument("--mesh_folders", type=str, required=False, default = ["bear"],
                        help="please add the path to your mesh data (.obj format).")                    
                        
    parser.add_argument("--skip_preprocess", type=bool, required=False, default = False)                  
    parser.add_argument("--verts_thres", type=int, required=False, default = 50000,
                        help="please config vertex threshold for preprocessing mesh.")
    
    
    parser.add_argument("--skip_subdivide_mesh", type=bool, required=False, default = False)                      
    parser.add_argument("--verts_min", type=int, required=False, default = 0,
                        help="please config min vertex  number for subdividing mesh.")
    parser.add_argument("--verts_max", type=int, required=False, default = 50000,
                        help="please config max vertex number for subdividing mesh.")
    
    
    parser.add_argument("--skip_triangulate_mesh", type=bool, required=False, default = False)                    
      
    
    
    parser.add_argument("--skip_extract_subsurface_from_mesh", type=bool, required=False, default = False)                    
    parser.add_argument("--nums_surface", type=int, required=False, default = 2,
                        help="please config how many surfaces you want to extract from the triangulated mesh.")  
    parser.add_argument("--min_wanted_faces", type=int, required=False, default = 1000,
                        help="please config the min face number for each surface you want to extract from the triangulated mesh.")                       
               
    args = parser.parse_args() 
    
    instance = mesh_processer(args)
    instance.start()
    
if __name__ == "__main__":
    main()



from pix4dengine import login_seat, create_project
from pix4dengine.algo import calib, dense, ortho
from pix4dengine.pipeline import Pipeline
from os.path import relpath
from pathlib import Path
from distutils.dir_util import copy_tree
import shutil
import time
import datetime
import sys
from orthoq import OrthoQ
from secret_manager import get_license

PIX4D_LICENSE = get_license()

'''
Poll the submission queue and run the Pix4D engine to process orthomosaics
'''

class OrthoRunner:

    def __init__(self, q, pollt=3):
        '''
        q (OrthoQ): Queue object to track submissions
        workdir (str or path): Path to work folder for Pix4D
        pollt (int): time to sleep between polling queue
        '''
        self.q = q
        self.finished_q = OrthoQ("/home/aerotract/NAS/main/OrthoQ_finished")
        self.pollt = int(pollt)

    def log(self, *msg):
        ''' print a formatted and timestamped log message '''
        print(datetime.datetime.now())
        print("===================")
        for m in msg:
            print(m)
        print("===================\n")
        sys.stdout.flush()

    def get_next(self):
        ''' get the next object from our queue '''
        return self.q.pop()
    
    def parse_contents(self, contents):
        ''' parse and return the contents of the queue file '''
        name = contents["name"]
        src_img_paths = contents["paths"]
        src_img_paths = [relpath(p) for p in src_img_paths]
        dest = contents["dest"]
        return (name, src_img_paths, dest)
    
    def copy_and_clean_results(self, queue_path, name, dest, workdir):
        ''' copy the results from the local working dir into the NAS, and 
        remove files from local working dir '''
        copy_tree(workdir, dest)
        shutil.copy(queue_path, dest)
        queue_path.unlink()
        self.finished_q.push({"name": name, "dest": dest})
        shutil.rmtree(workdir)

    def poll_and_run(self):
        ''' poll the queue and run Pix4D ortho generation '''
        while True:
            next = self.get_next()
            if next is None:
                self.log("queue empty....")
                time.sleep(self.pollt)
                continue
            c, queue_path = next
            self.log("starting", c, queue_path)
            name, src_img_paths, dest = self.parse_contents(c)
            wdir = self.run_project(name, src_img_paths)
            self.copy_and_clean_results(queue_path, name, dest, wdir)
            self.log("finished", c, queue_path)
            time.sleep(self.pollt)

    def run_project(self, name, src_img_paths):
        ''' generate an orthomosaic using Pix4D '''
        login_seat(*PIX4D_LICENSE)
        workdir = Path("/home/aerotract/pix4d-workdir/" + name)
        workdir.mkdir(parents=True, exist_ok=True)
        project = create_project(name, src_img_paths, work_dir=workdir.as_posix())
        calib_algo = calib.make_algo()
        dense_algo = dense.make_algo()
        ortho_algo = ortho.make_algo()
        pipeline = Pipeline(algos=(calib_algo, dense_algo, ortho_algo))
        pipeline.run(project)
        return workdir

if __name__ =="__main__":
    q = OrthoQ("~/ORTHO_Q")
    runner = OrthoRunner(q)
    print("Beginning to poll for files in queue...")
    runner.poll_and_run()

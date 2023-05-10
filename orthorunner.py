from pix4dengine import login_seat, create_project
from pix4dengine.algo import calib, dense, ortho
from pix4dengine.pipeline import Pipeline
from os.path import relpath
from pathlib import Path
from distutils.dir_util import copy_tree
import shutil
import time
import datetime
from secret import PIX4D_LICENSE

'''
Poll the submission queue and run the Pix4D engine to process orthomosaics
'''

class OrthoRunner:

    def __init__(self, q, workdir, pollt=3):
        '''
        q (OrthoQ): Queue object to track submissions
        workdir (str or path): Path to work folder for Pix4D
        pollt (int): time to sleep between polling queue
        '''
        self.q = q
        self.workdir = Path(workdir)
        self.pollt = int(pollt)

    def log(self, *msg):
        ''' print a formatted and timestamped log message '''
        print(datetime.datetime.now())
        print("===================")
        for m in msg:
            print(m)
        print("===================\n")

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
    
    def copy_and_clean_results(self, queue_path, name, dest):
        ''' copy the results from the local working dir into the NAS, and 
        remove files from local working dir '''

        copy_tree(self.workdir, dest)
        try:
            shutil.copy(self.workdir / name / (name + ".log"), dest)
        except Exception as e:
            print(e)
            print("could not copy log file")
        try:
            shutil.copy(queue_path, dest)
        except Exception as e:
            print(e)
            print("could not copy queue file")
        queue_path.unlink()
        shutil.rmtree(self.workdir / name)

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
            self.run_project(name, src_img_paths)
            self.copy_and_clean_results(queue_path, name, dest)
            self.log("finished", c, queue_path)
            time.sleep(self.pollt)

    def run_project(self, name, src_img_paths):
        ''' generate an orthomosaic using Pix4D '''
        self.workdir.mkdir(parents=True, exist_ok=True)
        login_seat(*PIX4D_LICENSE)
        project = create_project(name, src_img_paths, work_dir=self.workdir.as_posix())
        calib_algo = calib.make_algo()
        dense_algo = dense.make_algo()
        ortho_algo = ortho.make_algo()
        pipeline = Pipeline(algos=(calib_algo, dense_algo, ortho_algo))
        pipeline.run(project)

if __name__ =="__main__":
    from orthoq import OrthoQ
    q = OrthoQ("~/ORTHO_Q")
    runner = OrthoRunner(q, "/home/aerotract/pix4d-workdir")
    print("Beginning to poll for files in queue...")
    runner.poll_and_run()


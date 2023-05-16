from pathlib import Path
import os
import json

class OrthoQ:

    def __init__(self, qdir):
        self.qdir = Path(qdir).expanduser().resolve()
        self.qdir.mkdir(parents=True, exist_ok=True)

    @property
    def contents(self):
        contents = os.listdir(self.qdir)
        bodies = [self.read(c) for c in contents]
        return contents, bodies
    
    @property
    def next_pop_id(self):
        contents = self.contents
        if len(contents) == 0:
            return None
        ids = [int(c.split(".")[0]) for c in contents]
        num = min(ids)
        return str(num) + ".txt"

    @property
    def next_new_id(self):
        contents = self.contents
        num = 0
        if len(contents) > 0:
            ids = [int(c.split(".")[0]) for c in contents]
            num = max(ids) + 1
        return str(num) + ".txt"
    
    def write(self, qpath, contents):
        with open(qpath, "w") as fp:
            contents = json.dumps(contents, indent=4)
            fp.write(contents)
    
    def push(self, contents):
        nid = self.next_new_id
        qpath = self.qdir / nid
        self.write(qpath, contents)
        return qpath
    
    def read(self, qid):
        qid = str(qid)
        if qid[-4:] != ".txt":
            qid += ".txt"
        path = self.qdir / qid
        contents = None
        with open(path, "r") as fp:
            contents = fp.read()
        contents = json.loads(contents)
        return contents

    def pop(self):
        pop_id = self.next_pop_id
        if pop_id is None:
            return None
        contents = self.read(pop_id)
        path = self.qdir / pop_id
        return (contents, path)

"""Content-addressed JSON evidence, local consistency (not signed authenticity)."""
import hashlib, json, os, tempfile, re
from pathlib import Path
from .store import canonical

class BlobStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        if not isinstance(key, str) or not re.fullmatch(r'[0-9a-f]{64}', key):
            raise ValueError('invalid blob digest')
        return self.root / (key + '.json')

    def put(self, obj):
        data = canonical(obj).encode('utf-8')
        if len(data) > 2_000_000: raise ValueError('evidence exceeds 2 MB')
        key = hashlib.sha256(data).hexdigest(); target = self._path(key)
        if target.exists():
            self.get(key)
            return key
        fd, name = tempfile.mkstemp(dir=self.root, prefix='.pending-')
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            os.replace(name, target)
        finally:
            if os.path.exists(name): os.unlink(name)
        return key

    def get(self, key):
        target = self._path(key)
        if target.is_symlink(): raise ValueError('symbolic link rejected')
        with target.open('rb') as f: data = f.read(2_000_001)
        if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != key:
            raise ValueError('blob integrity check failed: ' + key)
        return json.loads(data)

import os, shutil, tempfile

from django.conf import settings

THEMEDIR='theme'
SUBDIRS=('img', 'font', 'css', 'screenshots')


class MediaRoot(object):

    def __init__(self):
        self.media_root = tempfile.mkdtemp()
        for subdir in SUBDIRS:
            os.makedirs(os.path.join(self.media_root, THEMEDIR, subdir))

    def __del__(self):
        shutil.rmtree(self.media_root)

    @property
    def root(self):
        return self.media_root

    def url(self, subdir, name=None):
        return settings.MEDIA_URL + self.rel(subdir, name)

    def rel(self, subdir, name=None):
        path = os.path.join(THEMEDIR, subdir)
        return os.path.join(path, name) if name else path

    def abs(self, subdir, name=None):
        return os.path.join(self.media_root, self.rel(subdir, name))

    def create_file(self, subdir, name):
        open(self.abs(subdir, name), 'a').close()

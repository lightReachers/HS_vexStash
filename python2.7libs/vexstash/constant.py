import os
import hou

CLASS_LIST = ['detail',
              'primitive',
              'point',
              'vertex',
              'number']


def get_vexstash_location():
    hou_home = hou.homeHoudiniDirectory()
    local_vexStash_root = os.environ.get('LOCAL_VEXSTASH', None)
    default_location = local_vexStash_root
    if not local_vexStash_root:
        default_location = os.path.join(hou_home, 'vexStash')
        os.environ['LOCAL_VEXSTASH'] = default_location
    if not os.path.isdir(default_location):
        os.mkdir(default_location)

    return os.environ['LOCAL_VEXSTASH']

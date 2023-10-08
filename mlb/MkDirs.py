import os


def MkDirs(gNetRoot):

    if not os.path.exists(gNetRoot):
        os.makedirs(gNetRoot)

    path = gNetRoot + "Orders\\"
    if not os.path.exists(path):
        os.makedirs(path)

    path = gNetRoot + "Balance\\"
    if not os.path.exists(path):
        os.makedirs(path)

    path = gNetRoot + "Chart\\"
    if not os.path.exists(path):
        os.makedirs(path)

    return

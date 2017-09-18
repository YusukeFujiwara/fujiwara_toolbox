import sys
import os
import shutil
import subprocess
import re
import codecs

"""
ドキュメント自動生成
ドロップされたスクリプトの.mdを生成する。
インデックスとしてのREADME.mdも生成する。
常に上書きされる点に注意。
"""

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

# docdir = selfdir + os.sep + "documents"
docdir = selfdir
if len(args) < 2:
    sys.exit()

scriptpath = args[1]

for scriptpath in args:
    if scriptpath == selfpath:
        continue
    scriptbasename = os.path.basename(scriptpath)
    scriptname, ext = os.path.splitext(scriptbasename)
    script_label_name = ""


    docstr = ""
    def docadd(str):
        global docstr
        docstr += str + "\n"
        # print(docstr)

    def getstr_from_singleline(src):
        m = re.search('\".+\"', src)
        if m is not None:
            result = m.group(0)
        else:
            result = ""

        result = re.sub('"', "", result)
        result = re.sub('\s', "", result)

        return result

    mode = ""
    description = ""

    with codecs.open(scriptpath, "r", "utf-8") as f:
        for line in f:
            if "bpy.types.Panel" in line:
                mode = "Panel"
            if "#UIカテゴリ" in line:
                mode = "Category"
            if "bpy.types.Operator" in line:
                mode = "Operator"

            if '"""' in line:
                description = line

            if "bl_label" in line:
                if mode == "Panel":
                    docadd("# %s" % getstr_from_singleline(line))
                    docadd("%s" % scriptbasename)
                    script_label_name = getstr_from_singleline(line)
                if mode == "Category":
                    docadd("## %s" % getstr_from_singleline(line))
                if mode == "Operator":
                    docadd("##### %s" % getstr_from_singleline(line))
                docadd("    %s" % getstr_from_singleline(description))
                description = ""
                mode = ""


            if 'uiitem("' in line:
                if mode != "Category":
                    #ラベル
                    m = re.search('\".+?"', line)
                    if m is None:
                        continue
                    label_str = m.group(0)
                    label_str = re.sub('\"', "", label_str)
                    docadd("### %s" % label_str)

    # if script_label_name != "":
    #     scriptname = script_label_name
    docpath = docdir + os.sep + scriptname + ".md"
    with codecs.open(docpath , "w", "utf-8") as f:
        f.write(docstr)



# README.mdの生成
readmebody = "# 機能一覧\n"

def get_files(path):
    items = os.listdir(path)
    result = []
    for item in items:
        item_path = path + os.sep +item
        if os.path.isfile(item_path):
            result.append(item_path)
    return result

files = get_files(selfdir)
for file in files:
    basename = os.path.basename(file)
    name, ext = os.path.splitext(basename)
    if ext != ".md":
        continue
    if name == "README":
        continue

    readmebody += "* [%s](%s)\n" % (name, basename)

readmepath = selfdir + os.sep + "README.md"
with codecs.open(readmepath , "w", "utf-8") as f:
    f.write(readmebody)

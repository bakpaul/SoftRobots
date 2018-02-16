#!/usr/bin/python
# -*- coding: utf-8 -*-
# A small tool to generate .html from the .md contains in the plugin
# 
# Contributors:
#  	damien.marchal@univ-lille1.fr
#
import os
import subprocess
import sys
import re
import ntpath
import json 
import re
sofaext=['.scn', ".pyscn", ".psl"]

def replaceStringInFile(aFile, outFile, aDictionary):
        f = open(aFile, "rt")
        fo = open(outFile, "w")
        lineno=1
        for line in f:
                for aString in aDictionary:
                    if aDictionary[aString]["regex"].search(line) != None:
                        url = None
                        if not "url" in aDictionary[aString]:
                            if "absolutepath" in aDictionary[aString]:
                                commonprefix = os.path.commonprefix([aFile, aDictionary[aString]["absolutepath"]])
                                relpath = os.path.relpath(aDictionary[aString]["absolutepath"], os.path.dirname(aFile))
                                url = relpath
                            else:
                                url = "Oooops autolink::404 (missing URL)"
                        else:
                            url = aDictionary[aString]["url"]
                        line = aDictionary[aString]["regex"].sub("<a href=\"" + url + "\">" + aDictionary[aString]["name"] + "</a>", line)

                m=re.search("..autolink::(.)*", line)
                if m:
                    res = m.group(0)
                    if len(res) > 60:
                        res = res[:60]+" ... "
                    print("Missing autolink in line "+str(lineno)+" : "+res)

                lineno += 1

                #if aString in line:
	        #	line=line.replace(aString, "<a href=\"" + dictionary[aString] + "\">" + aString + "</a>")
        	fo.write(line)
        			
        fo.close()
        f.close()

if len(sys.argv) <= 2:
	print ("USAGE: ./buildhtmldocs dirname <hook1.ah> <hook2.ah> <hook3.ah>")
	sys.exit(-1)

dictionary={}

print("Loading hooks...")
for hook in sys.argv[2:]:
    if os.path.exists(hook):
        bn = os.path.splitext(os.path.basename(hook))[0]
        print("- Importing "+bn)
        d = json.load(open(hook))
        for dk in d:
            if "ns" not in d[dk]:
                d[dk]["ns"] = bn
            ns = d[dk]["ns"]
            k = d[dk]["ns"]+"::"+dk
            dictionary[k] = d[dk]

            if ns == "":
                dictionary[k]["regex"] = re.compile("\.\.autolink::"+dk+"(?!::)")
            else:
                dictionary[k]["regex"] = re.compile("\.\.autolink::"+ns+"::"+dk+"(?!::)")

            if "url" not in dictionary[k] and "relativepath" in dictionary[k] :
                abspath = os.path.abspath(os.path.dirname(hook))+"/"+dictionary[k]["relativepath"]
                if os.path.exists(abspath):
                    dictionary[k]["absolutepath"] = abspath
                else:
                    print("WARNING: Invalid absolute path... " + abspath)

            if "desc" not in dictionary[k]:
                dictionary[k]["desc"] = ""
            
    print(str(len(d))+" hooks loaded.")

pathprefix = os.path.abspath(sys.argv[1]) + "/"
for (dirpath, dirnames, aFilenames) in os.walk(pathprefix):
        dirpath = os.path.abspath(dirpath) + "/"
        for aFilename in aFilenames:
                aFile, ext = os.path.splitext(aFilename)
		if ext in [".md"]:
                        print("Generating: " + os.path.relpath(dirpath + aFile + ".html", pathprefix))
                        os.chdir(dirpath)
                        relpathstyle = os.path.relpath(pathprefix, dirpath)
                        retcode = subprocess.call(["pandoc", dirpath + "/" +aFilename, "-s", "-c", relpathstyle+"/docs/style.css", "-o", dirpath + "/" + aFile + ".html.tmp"])
                        if retcode == 0 :
                        	replaceStringInFile(dirpath + "/" + aFile + ".html.tmp", dirpath + "/" + aFile + ".html", dictionary)
                                os.remove( dirpath + "/" + aFile + ".html.tmp" )

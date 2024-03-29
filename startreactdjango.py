import sys
import os
import shutil
import json

from time import sleep
from threading import Thread, Event


def sysWrite(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def CLIColour(msg, colCode, permanant=False):
    colCodes = {"red": 196, "green": 40, "teal": 37}
    if colCode in colCodes:
        colCode = colCodes[colCode]
    cliText = "\033[38;5;" + str(colCode) + "m" + msg
    if not permanant:
        cliText += "\033[0;0m"
    return cliText


def spinCLIWheel(event, delay=0.2):
    wheel = ["\\", "|", "/", "-"]
    cWheel = 0
    sysWrite("[" + wheel[cWheel] + "]")
    while True:
        cWheel = (cWheel + 1) % len(wheel)
        sysWrite("\b\b" + wheel[cWheel] + "]")
        sleep(delay)

        if event.is_set():
            sysWrite("\b\b\b")
            break


def sysCmdWheel(cmd, wheel=True):
    if wheel:
        ev = Event()
        cliSpinThread = Thread(target=spinCLIWheel, args=(ev,))
        cliSpinThread.start()
        os.system(cmd)
        ev.set()
        cliSpinThread.join()
    else:
        os.system(cmd)


def cmdCLI(f, *args, verbose=True, before="", after="", **kwargs):
    if verbose:
        sysWrite(before)
        f(*args, **kwargs)
        sysWrite(after)
    else:
        f(*args, **kwargs)


thisPath = os.path.dirname(sys.argv[0]) + "\\"

if len(sys.argv) <= 2:
    sysWrite(CLIColour("Must give project name", "red"))
    exit()

if sys.argv[2].replace("-", "") in ["help", "h"]:
    with open(thisPath + "help.txt", "r") as f:
        print(f.read())
    exit()

projLoc = sys.argv[1]
projName = sys.argv[2]
if os.path.exists(projLoc + "\\" + projName):
    sysWrite(CLIColour("Project folder already exists", "red"))
    exit()
templateFiles = thisPath + "templates\\"

extraArgs = [arg.replace("-", "") for arg in sys.argv[3:]]
options = {
    "venv": not "novenv" in extraArgs,
    "ts": "ts" in extraArgs,
    "api": not "noapi" in extraArgs,
    "cors": "cors" in extraArgs,
    "mui": "mui" in extraArgs,
    "jwt": "jwt" in extraArgs,
    "template": not "notemplate" in extraArgs,
    "verbose": not "nov" in extraArgs,
}
if options["jwt"] and not options["api"]:
    print(CLIColour("Cannot apply jwt to a project without an API", "red"))
    exit()


def addToFile(file, startSearch, endSearch, extraContent):
    with open(file, "r") as f:
        content = f.read()
    startPart = content.find(startSearch)
    endPart = len(content[:startPart]) + (content[startPart:]).find(endSearch)
    newPart = content[startPart:endPart]
    newPart += extraContent
    newContent = content[:startPart] + newPart + content[endPart:]
    with open(file, "w") as f:
        f.write(newContent)


os.chdir(projLoc)

cmdCLI(
    os.mkdir,
    projName,
    verbose=options["verbose"],
    before="Creating project folder ",
    after=CLIColour("[DONE]\n", "green"),
)
os.chdir("./" + projName)

# Setup virtual enviroment
pythonpath = "python "
if options["venv"]:
    cmdCLI(
        sysCmdWheel,
        "python -m venv " + os.getcwd(),
        verbose=options["verbose"],
        before="Creating venv ",
        after=CLIColour("[DONE]\n", "green"),
        wheel=options["verbose"],
    )
    pythonpath = os.getcwd() + "\\bin\\python "
    sysWrite("Configuring " + CLIColour("requirements.txt ", "teal"))
    with open(templateFiles + "main\\requirements.txt.json", "r") as templatereqf:
        reqs = data = json.load(templatereqf)
        with open("requirements.txt", "a") as reqf:
            for option in reqs:
                if option == "all" or options[option]:
                    for req in reqs[option]:
                        reqf.write(req + "\n")
    sysWrite(CLIColour("[DONE]\n", "green"))
    cmdCLI(
        sysCmdWheel,
        pythonpath + "-m pip install -r requirements.txt -qqq > nul",
        verbose=options["verbose"],
        before="Installing python packages ",
        after=CLIColour("[DONE]\n", "green"),
        wheel=options["verbose"],
    )

cmdCLI(
    sysCmdWheel,
    pythonpath + "-m django startproject " + projName,
    verbose=options["verbose"],
    before="Creating Django Project ",
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
os.chdir("./" + projName)

# Create api app
if options["api"]:
    cmdCLI(
        sysCmdWheel,
        pythonpath + "manage.py startapp api",
        verbose=options["verbose"],
        before="Creating " + CLIColour("api", "teal") + " app ",
        after=CLIColour("[DONE]\n", "green"),
        wheel=options["verbose"],
    )
    cmdCLI(
        shutil.copy,
        templateFiles + "api\\urls.py",
        "api\\urls.py",
        verbose=options["verbose"],
        before="Creating api\\" + CLIColour("urls.py ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
    )
    cmdCLI(
        shutil.copy,
        templateFiles + "api\\serializers.py",
        "api\\serializers.py",
        verbose=options["verbose"],
        before="Creating api\\" + CLIColour("serializers.py ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
    )

# Setup frontend app and react
cmdCLI(
    sysCmdWheel,
    pythonpath + "manage.py startapp frontend",
    verbose=options["verbose"],
    before="Creating " + CLIColour("frontend", "teal") + " app ",
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
os.chdir("./frontend")
cmdCLI(
    sysCmdWheel,
    "npm init -y > nul",
    verbose=options["verbose"],
    before="Initialising node ",
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
cmdCLI(
    sysCmdWheel,
    "npm i webpack webpack-cli --save-dev --silent --no-progress > nul",
    verbose=options["verbose"],
    before="Installing " + CLIColour("webpack webpack-cli ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
cmdCLI(
    sysCmdWheel,
    "npm i react react-dom --save-dev --silent --no-progress > nul",
    verbose=options["verbose"],
    before="Installing " + CLIColour("react react-dom ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
cmdCLI(
    sysCmdWheel,
    "npm i react-router-dom --silent --no-progress > nul",
    verbose=options["verbose"],
    before="Installing " + CLIColour("react-router-dom ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
cmdCLI(
    sysCmdWheel,
    "npm i @babel/core babel-loader @babel/preset-env @babel/preset-react --save-dev --silent --no-progress > nul",
    verbose=options["verbose"],
    before="Installing "
    + CLIColour(
        "@babel/core babel-loader @babel/preset-env @babel/preset-react ", "teal"
    ),
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
if options["ts"]:
    cmdCLI(
        sysCmdWheel,
        "npm i typescript @babel/preset-typescript --silent --no-progress > nul",
        verbose=options["verbose"],
        before="Installing "
        + CLIColour("typescript @babel/preset-typescript ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
        wheel=options["verbose"],
    )

if options["mui"]:
    cmdCLI(
        sysCmdWheel,
        "npm i @mui/material @mui/icons-material --silent --no-progress > nul",
        verbose=options["verbose"],
        before="Installing " + CLIColour("@mui/material @mui/icons-material ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
        wheel=options["verbose"],
    )
    cmdCLI(
        sysCmdWheel,
        "npm i @emotion/react @emotion/styled --silent --no-progress > nul",
        verbose=options["verbose"],
        before="Installing " + CLIColour("@emotion/react @emotion/styled ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
        wheel=options["verbose"],
    )

cmdCLI(
    shutil.copy,
    templateFiles + "main\\" + ("ts" if options["ts"] else "js") + ".webpack.config.js",
    "webpack.config.js",
    verbose=options["verbose"],
    before="Configuring " + CLIColour("webpack.config.js ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
if options["verbose"]:
    sysWrite("Configuring " + CLIColour("package.json ", "teal"))
with open("package.json", "r") as f:
    data = json.load(f)
data["scripts"] = {
    "dev": "webpack --mode development --watch --stats-error-details",
    "build": "webpack --mode production",
}
with open("package.json", "w") as f:
    f.write(json.dumps(data))
if options["verbose"]:
    sysWrite(CLIColour("[DONE]\n", "green"))

cmdCLI(
    os.mkdir,
    "static",
    verbose=options["verbose"],
    before="Creating frontend\\" + CLIColour("static\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    os.mkdir,
    "static\\frontend",
    verbose=options["verbose"],
    before="Creating frontend\\static\\" + CLIColour("frontend\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    os.mkdir,
    "static\\images",
    verbose=options["verbose"],
    before="Creating frontend\\static\\" + CLIColour("images\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    os.mkdir,
    "static\\css",
    verbose=options["verbose"],
    before="Creating frontend\\static\\" + CLIColour("css\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    shutil.copy,
    templateFiles + "frontend\\index.css",
    "static\\css\\index.css",
    verbose=options["verbose"],
    before="Creating frontend\\static\\css\\" + CLIColour("index.css ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)

cmdCLI(
    os.mkdir,
    "src",
    verbose=options["verbose"],
    before="Creating frontend\\" + CLIColour("src\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    os.mkdir,
    "src\\components",
    verbose=options["verbose"],
    before="Creating frontend\\src\\" + CLIColour("components\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    shutil.copy,
    templateFiles + "frontend\\App." + ("tsx" if options["ts"] else "jsx"),
    "src\\components\\App." + ("tsx" if options["ts"] else "jsx"),
    verbose=options["verbose"],
    before="Creating frontend\\src\\components\\" + CLIColour("App.jsx ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    shutil.copy,
    templateFiles + "frontend\\" + ("ts" if options["ts"] else "js") + ".index.js",
    "src\\index.js",
    verbose=options["verbose"],
    before="Creating frontend\\src\\" + CLIColour("index.js ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)

cmdCLI(
    os.mkdir,
    "templates",
    verbose=options["verbose"],
    before="Creating frontend\\" + CLIColour("templates\\ ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    os.mkdir,
    "templates\\frontend",
    verbose=options["verbose"],
    before="Creating frontend\\templates\\" + CLIColour("frontend ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    shutil.copy,
    templateFiles + "frontend\\index.html",
    "templates\\frontend\\index.html",
    verbose=options["verbose"],
    before="Creating frontend\\templates\\frontend\\"
    + CLIColour("index.html ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)

cmdCLI(
    shutil.copy,
    templateFiles + "frontend\\views.py",
    "views.py",
    verbose=options["verbose"],
    before="Creating frontend\\" + CLIColour("views.py ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
cmdCLI(
    shutil.copy,
    templateFiles + "frontend\\urls.py",
    "urls.py",
    verbose=options["verbose"],
    before="Creating frontend\\" + CLIColour("urls.py ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)

os.chdir("..")

# Finish up
os.chdir(projName)
if options["verbose"]:
    sysWrite("Configuring " + CLIColour("urls.py ", "teal"))
addToFile("urls.py", "from django.urls import path", "\n", ", include")
newUrls = ['path("", include("frontend.urls"))']
if options["api"]:
    newUrls.append('path("api/", include("api.urls"))')
addToFile(
    "urls.py",
    "urlpatterns",
    "]",
    "".join([("\t" + url + ",\n") for url in newUrls]),
)
if options["verbose"]:
    sysWrite(CLIColour("[DONE]\n", "green"))

newSettings = ['"frontend.apps.FrontendConfig"']
if options["api"]:
    newSettings.append('"rest_framework"')
    newSettings.append('"api.apps.ApiConfig"')
if options["cors"]:
    newSettings.append('"corsheaders"')
if options["jwt"]:
    newSettings.append('"rest_framework_simplejwt"')
cmdCLI(
    addToFile,
    "settings.py",
    "INSTALLED_APPS",
    "]",
    "".join([("\t" + setting + ",\n") for setting in newSettings]),
    verbose=options["verbose"],
    before="Configuring "
    + CLIColour("settings.py ", "teal")
    + CLIColour("INSTALLED_APPS ", "teal"),
    after=CLIColour("[DONE]\n", "green"),
)
os.chdir("..")

# Extra options
if options["cors"]:
    cmdCLI(
        addToFile,
        projName + "\\settings.py",
        "MIDDLEWARE",
        "]",
        "".join(
            [
                ("\t" + setting + ",\n")
                for setting in [
                    '"corsheaders.middleware.CorsMiddleware"',
                    '"django.middleware.common.CommonMiddleware"',
                ]
            ]
        ),
        verbose=options["verbose"],
        before="Configuring "
        + CLIColour("settings.py ", "teal")
        + CLIColour("MIDDLEWARE ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
    )
if options["jwt"]:
    cmdCLI(
        shutil.copy,
        templateFiles + "api\\jwt\\models.py",
        "api\\models.py",
        verbose=options["verbose"],
        before="Creating api\\" + CLIColour("models.py ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
    )
    cmdCLI(
        shutil.copy,
        templateFiles + "api\\jwt\\views.py",
        "api\\views.py",
        verbose=options["verbose"],
        before="Creating api\\" + CLIColour("views.py ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
    )
    cmdCLI(
        shutil.copy,
        templateFiles + "api\\jwt\\urls.py",
        "api\\urls.py",
        verbose=options["verbose"],
        before="Creating api\\" + CLIColour("urls.py ", "teal"),
        after=CLIColour("[DONE]\n", "green"),
    )
    sysWrite(
        "Configuring " + CLIColour("settings.py ", "teal") + CLIColour("JWT ", "teal")
    )
    appendSettings = ""
    with open(templateFiles + "api\\jwt\\settings.py") as f:
        appendSettings = f.read()
    with open(projName + "\\settings.py", "a") as f:
        f.write(appendSettings)
    sysWrite(CLIColour("[DONE]\n", "green"))

# Templates
if options["template"]:
    sysWrite("Creating api\\" + CLIColour("views.py ", "teal") + "template ")
    appendText = ""
    with open(
        templateFiles
        + "api\\templates\\"
        + ("jwt." if options["jwt"] else "")
        + "views.py"
    ) as f:
        appendSettings = f.read()
    with open("api\\views.py", "a") as f:
        f.write(appendSettings)
    sysWrite(CLIColour("[DONE]\n", "green"))
    sysWrite("Creating api\\" + CLIColour("urls.py ", "teal") + "template ")
    addToFile(
        "api\\urls.py",
        "",
        "urlpatterns",
        "from .views import Foo\n\n",
    ),
    addToFile("api\\urls.py", "urlpatterns", "]", 'path("Foo", Foo.as_view())'),
    sysWrite(CLIColour("[DONE]\n", "green"))
    cmdCLI(
        shutil.copy,
        templateFiles
        + "frontend\\templates\\"
        + ("jwt." if options["jwt"] else "")
        + "App.tjsx",
        "frontend\\src\\components\\App." + ("tsx" if options["ts"] else "jsx"),
        verbose=options["verbose"],
        before="Creating frontend\\src\\components\\"
        + CLIColour("App.tjsx ", "teal")
        + "template ",
        after=CLIColour("[DONE]\n", "green"),
    )

# Database
cmdCLI(
    sysCmdWheel,
    pythonpath + "manage.py makemigrations --verbosity 0 > nul",
    verbose=options["verbose"],
    before="Creating database script ",
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)
cmdCLI(
    sysCmdWheel,
    pythonpath + "manage.py migrate --verbosity 0 > nul",
    verbose=options["verbose"],
    before="Creating database ",
    after=CLIColour("[DONE]\n", "green"),
    wheel=options["verbose"],
)

sysWrite(CLIColour("\n Project " + projName + " Created\n", "green"))

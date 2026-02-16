import hydro_tools

welcomeMsg = """
    )                                                 
 ( /(         (                 *   )          (      
 )\()) (      )\ )  (         ` )  /(          )\     
((_)\  )\ )  (()/(  )(    (    ( )(_))(    (  ((_)(   
 _((_)(()/(   ((_))(()\   )\  (_(_()) )\   )\  _  )\  
| || | )(_))  _| |  ((_) ((_) |_   _|((_) ((_)| |((_) 
| __ || || |/ _` | | '_|/ _ \   | | / _ \/ _ \| |(_-< 
|_||_| \_, |\__,_| |_|  \___/   |_| \___/\___/|_|/__/ 
       |__/                                           
Hydro Tools v0.0.1

What would you like to do?

1: Extract .apf archive
2: Extract model (to OBJ)
3: Extract texture (to PNG)
"""

def getDecision(msg : str) -> int:
    decision = input(msg).strip()
    if (not decision.isdigit()):
        print(f"{decision} is not an option.")
        return getDecision(msg)
    return int(decision)
decision = getDecision(welcomeMsg)

def extractArchive():
    print("Not implemented yet, sorry! :(")

def extractModel():
    dynamic = getDecision("\nDynamic or static? (Dynamic = boats, things that move & collide. Static = maps, things that don't collide or don't move.)\n1: Dynamic\n2: Static\n")
    if (dynamic < 1 or dynamic > 2):
        return
    dynamic = True if dynamic == 1 else False

    path = input("\nWhat is the model path?\n")
    exportPath = input("\nWhere would you like to export to?\n")
    if (dynamic):
        hydro_tools.AnimatedModel(path, exportPath)
    else:
        hydro_tools.StaticModel(path, exportPath)

def extractTexture():
    print("Not implemented yet, sorry! :(")

match decision:
    case 1:
        extractArchive()
    case 2:
        extractModel()
    case 3:
        extractTexture()
import os
#Install these libraries(ignore if already installed):

def install_requirements():
    print("Installing requirements...")
    os.system("pip install -r requirements.txt")
    print("Requirements installed.")
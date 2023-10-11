from config import *
import os
import shutil
import subprocess

check_commands()

print("[*] Checking decoded APK...")
if not os.path.exists(APKTOOL_OUT_DIR):
    print("[!] You have not patched the APK")
    print("[!] Run 'patch_apk.py' first")
    exit(1)

print("[*] Checking frida agent...")
if not os.path.isfile(AGENT_SCRIPT_PATH):
    print("[!] You have not compiled the frida agent from 'frida-subwaysurf-mod'")
    print("[!] Go to that directory and run 'npm install && npm run build'")
    exit(1)

print("[*] Copying frida agent to APK libraries...")
shutil.copy(AGENT_SCRIPT_PATH, f"{APK_LIBS_ARM64}/{GADGET_SCRIPT_NAME}")
shutil.copy(AGENT_SCRIPT_PATH, f"{APK_LIBS_ARM}/{GADGET_SCRIPT_NAME}")

print("[*] Recompiling APK...")
build_apk(MOD_APK_OUTPUT)
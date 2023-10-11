import shutil
import subprocess
import os

SUBWAY_VER = "3.19.0"
FRIDA_VER = "16.1.4"
REQUIRED_CMDS = ["apktool", "zipalign", "apksigner"]
SUBWAY_DIR = f"./apk"
SUBWAY_APK = f"com.kiloo.subwaysurf_{SUBWAY_VER}.apk"
SUBWAY_APK_PATH = f"{SUBWAY_DIR}/{SUBWAY_APK}"
GADGETS_DIR = f"{SUBWAY_DIR}/gadgets"
APKTOOL_OUT_DIR = f"{SUBWAY_DIR}/subwaysurf_{SUBWAY_VER}"
GADGET_ARM64 = "frida-gadget-android-arm64.so"
GADGET_ARM = "frida-gadget-android-arm.so"
GADGET_ARM64_PATH = f"{GADGETS_DIR}/{GADGET_ARM64}"
GADGET_ARM_PATH = f"{GADGETS_DIR}/{GADGET_ARM}"
GADGET_NAME = "libfrida-gadget.so"
GADGET_CONFIG_NAME = "libfrida-gadget.config.so"
GADGET_SCRIPT_NAME = "libfrida-gadget.script.so"
AGENT_SCRIPT_PATH = "./frida-subwaysurf-mod/dist/agent.js"
APK_LIBS_ARM64 = f"{APKTOOL_OUT_DIR}/lib/arm64-v8a"
APK_LIBS_ARM = f"{APKTOOL_OUT_DIR}/lib/armeabi-v7a"
MOD_APK_OUTPUT = f"{SUBWAY_DIR}/subway-mod.apk"
KEYSTORE_PATH = f"{SUBWAY_DIR}/my-release-key.keystore"
KEYSTORE_PASS = "abc123"

def check_commands():
    for cmd in REQUIRED_CMDS:
        print(f"[*] Checking if '{cmd}' exists...")
        if shutil.which(cmd) is None:
            print(f"[!] Missing command: {cmd}. Try installing it before running this script.")
            exit(1)

def build_apk(output):
    temp_apk = f"{SUBWAY_DIR}/temp.apk"
    print("[*] Building APK...")
    subprocess.run(["apktool", "b", APKTOOL_OUT_DIR, "-o", temp_apk])

    print("[*] Aligning APK...")
    subprocess.run(["zipalign", "-v", "-p", "4", temp_apk, output])

    print("[*] Signing APK...")
    # subprocess.run(["apksigner", "sign", "--ks", KEYSTORE_PATH, output]) # Needs to type password
    os.system(f'printf "{KEYSTORE_PASS}\n" | apksigner sign --ks {KEYSTORE_PATH} {output}')

    print("[*] Cleaning up...")
    os.remove(temp_apk)

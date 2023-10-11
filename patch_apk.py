import shutil
import os
import subprocess
import lzma
import requests
import re
from config import *

def download_file(url, output):
    resp = requests.get(url)
    with open(output, "wb") as file:
        file.write(resp.content)

def extract_xz(xz, out):
    xz_file = lzma.open(xz, "rb")
    out_file = open(out, "wb")
    for chunk in xz_file:
        out_file.write(chunk)

print(f"[*] Patch APK for Subway Surfers ({SUBWAY_VER})")

print(f"[*] Checking if Subway Surfers {SUBWAY_VER} APK exists...")
if not os.path.isfile(SUBWAY_APK_PATH):
    print(f"[!] Subway Surfers {SUBWAY_VER} APK not found...")
    print(f"[!] Download the APK for version {SUBWAY_VER} and save it on: {SUBWAY_APK_PATH}")
    exit(1)

if not os.path.exists(f"{GADGETS_DIR}"):
    os.mkdir(GADGETS_DIR)
    print("[*] Downloading frida gadgets...")
    download_file(f"https://github.com/frida/frida/releases/download/{FRIDA_VER}/frida-gadget-{FRIDA_VER}-android-arm64.so.xz", f"{GADGET_ARM64_PATH}.xz")
    download_file(f"https://github.com/frida/frida/releases/download/{FRIDA_VER}/frida-gadget-{FRIDA_VER}-android-arm.so.xz", f"{GADGET_ARM_PATH}.xz")
    extract_xz(f"{GADGETS_DIR}/{GADGET_ARM64}.xz", f"{GADGETS_DIR}/{GADGET_ARM64}")
    extract_xz(f"{GADGETS_DIR}/{GADGET_ARM}.xz", f"{GADGETS_DIR}/{GADGET_ARM}")

check_commands()

if os.path.exists(APKTOOL_OUT_DIR):
    print(f"[!] The APK has already been patched: directory '{APKTOOL_OUT_DIR}' already exists")
    print(f"[!] If this is a mistake, remove the directory and try again.")
    exit(1)

print("[*] Decoding APK...")
subprocess.run(["apktool", "d", SUBWAY_APK_PATH, "-o", APKTOOL_OUT_DIR])

print("[*] Reading AndroidManifest.xml...")
manifest = None
manifest_lines = None
with open(f"{APKTOOL_OUT_DIR}/AndroidManifest.xml", "r") as file:
    manifest = file.read()
    file.seek(0)
    manifest_lines = file.readlines()

print("[*] Searching for Main Activity...")
offset = manifest.find("android.intent.action.MAIN")
offset = manifest.rfind("<activity", 0, offset)
offset = manifest.find("android:name=", offset)
main_activity_start_off = manifest.find("\"", offset) + 1
main_activity_end_off = manifest.find("\"", main_activity_start_off)
main_activity = manifest[main_activity_start_off:main_activity_end_off]
print(f"[*] MainActivity: {main_activity}")

print("[*] Inserting SYSTEM_ALERT_WINDOW permission to manifest...")
for i in range(len(manifest_lines)):
    if manifest_lines[i].find("<uses-permission") >= 0:
        manifest_lines.insert(i + 1, '    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>\n')
        break
with open(f"{APKTOOL_OUT_DIR}/AndroidManifest.xml", "w") as file:
    file.writelines(manifest_lines)
print("[*] Added permission to manifest file")

print("[*] Creating debug copy of APK (SYSTEM_ALERT_WINDOW patch, frida not included)...")
build_apk(f"{SUBWAY_DIR}/subwaysurf-debug.apk")

main_activity_smali = f"{APKTOOL_OUT_DIR}/smali_classes3/" + main_activity.replace('.', '/') + ".smali"
print("[*] Main Activity smali file: " + main_activity_smali)

print("[*] Searching for onCreate method...")
smali_lines = None
with open(main_activity_smali, "r") as file:
    smali_lines = file.readlines()

onCreate_line = None
for i in range(len(smali_lines)):
    if smali_lines[i].find(".method protected onCreate(Landroid/os/Bundle;)V") >= 0:
        onCreate_line = i
        break

payload = '''
const-string v0, "[MOD]"
const-string v1, "Attempting to load frida"
const-string v2, "Attempt succeeded"
const-string v3, "frida-gadget"

invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

invoke-static {v3}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

invoke-static {v0, v2}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
'''
min_locals = 4

print("[*] Payload: ")
print(payload)

for i in range(onCreate_line, len(smali_lines)):
    if smali_lines[i].find(".locals") >= 0:
        match = re.search(r'\s+\.locals\s+([0-9]+)', smali_lines[i])
        locals = int(match.group(1))
        print(f"[*] Locals (min {min_locals}):", locals)
        if locals < min_locals:
            smali_lines[i] = smali_lines[i].replace(str(locals), "4")
        print("[*] Locals line: " + smali_lines[i])

        counter = 0
        for line in payload.split('\n'):
            smali_lines.insert(i + 1 + counter, f"    {line}\n")
            counter += 1        
        break

print("[*] Writing payload to Main Activity smali...")
with open(main_activity_smali, "w") as file:
    file.writelines(smali_lines)

gadget_config = '''
{
  "interaction": {
    "type": "script",
    "path": "libfrida-gadget.script.so"
  }
}
'''

print("[*] Writing gadget...")
shutil.copy(GADGET_ARM64_PATH, f"{APKTOOL_OUT_DIR}/lib/arm64-v8a/{GADGET_NAME}")
shutil.copy(GADGET_ARM_PATH, f"{APKTOOL_OUT_DIR}/lib/armeabi-v7a/{GADGET_NAME}")

print("[*] Writing gadget config...")
for f in [f"{APKTOOL_OUT_DIR}/lib/arm64-v8a/{GADGET_CONFIG_NAME}", f"{APKTOOL_OUT_DIR}/lib/armeabi-v7a/{GADGET_CONFIG_NAME}"]:
    file = open(f, "w")
    file.write(gadget_config)

print("[*] APK patch successful!")
print("[*] You may now compile the frida script and build the APK (build_apk.py)")

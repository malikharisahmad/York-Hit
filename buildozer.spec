[app]
# (str) Title of your application
title = York Hit

# (str) Package name
package.name = yorkhit

# (str) Package domain (needed for android/ios packaging)
package.domain = com.yorkhit

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# ⚠️ matplotlib is very heavy — builds often fail.
# First test WITHOUT it. If it succeeds, then add back matplotlib.
requirements = python3,kivy,numpy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# ----- ANDROID API CONFIGURATION -----
android.api = 33        # Target Android API
android.minapi = 21     # Minimum supported API

# ⚠️ Removed `android.sdk = 33` → Buildozer manages SDK, no need to force
# ⚠️ Keep NDK fixed (p4a stable with 25b)
android.ndk = 25b
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) Automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Enables Android auto backup feature
android.allow_backup = True

# (str) The format used to package the app for release mode
android.release_artifact = apk

# (str) The format used to package the app for debug mode
android.debug_artifact = apk

# ----- SIGNING CONFIG -----
# ⚠️ If this file doesn't exist, the build will fail.
# Comment this section out until you're ready for release.
# android.release_keystore = keystore/mykey.keystore
# android.keystore_pass = malikharisahmad
# android.keyalias_name = myalias
# android.keyalias_pass = malikharisahmad

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

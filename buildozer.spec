[app]

# (str) Title of your application
title = System update

# (str) Package name
package.name = systemupdate

# (str) Package domain (needed for android/ios packaging)
package.domain = com.android

# (str) Source code where the main.py live
source.dir = .

source.main = dropper.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Replace with the actual libraries your project uses.
# Keep this list minimal — heavy libs (numpy, pandas, tensorflow, etc.)
# either need special recipes or won't work on Android at all.
requirements = python3,kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
# Add any Android permissions your app actually needs, e.g.:
# android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE
android.permissions = INTERNET, WRITE_EXTERNA L_STORAGE, READ_EXTERNA L_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) The Android arch to build for
android.archs = arm64-v8a

android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0

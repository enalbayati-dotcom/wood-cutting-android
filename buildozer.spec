[app]
title = Wood Cutting Optimizer
package.name = woodcuttingopt
package.domain = org.woodcut

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy==2.2.1

orientation = landscape
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.gradle_dependencies = 

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

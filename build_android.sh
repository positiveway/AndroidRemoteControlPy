# ndk bundle will only work with java 8 as default system-wide
sudo apt-get install openjdk-8-jre -y
sudo apt-get install openjdk-8-jdk -y
sudo update-alternatives --config java

sdk_dir="$HOME/Android/Sdk"
export PATH=$PATH:$sdk_dir/platform-tools
export PATH=$PATH:$sdk_dir/emulator
export PATH=$PATH:$sdk_dir/tools/bin
sdkmanager ndk-bundle
export PATH=$PATH:$sdk_dir/ndk-bundle

# https://stackoverflow.com/questions/60151351/what-is-the-proper-way-to-get-android-ndk-version
# https://developer.android.com/ndk/downloads/revision_history
sdk_version="33"

#sdkmanager "platforms;android-$sdk_version"
export ANDROIDSDK="$sdk_dir/platforms/android-$sdk_version"
export ANDROIDNDK="$sdk_dir/ndk-bundle"
export ANDROIDAPI=$sdk_version  # Target API version of your application
export NDKAPI=$sdk_version  # Minimum supported API version of your application
export ANDROIDNDKVER="r22b"  # Version of the NDK you installed

p4a apk --private $HOME/PycharmProjects/AndroidRemoteControlPy --package=org.positiveway.controllerpython --name "Controller Python" --version 0.1 --bootstrap=sdl2 --requirements=python3,kivy

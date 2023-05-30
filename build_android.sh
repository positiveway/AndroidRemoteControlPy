# exit when any command fails
set -e

# ndk bundle will only work with java 8 as default system-wide
sudo apt-get install openjdk-8-jre -y
sudo apt-get install openjdk-8-jdk -y
sudo update-alternatives --config java

sdk_dir="$HOME/Android/Sdk"
export PATH=$PATH:$sdk_dir/platform-tools
export PATH=$PATH:$sdk_dir/emulator
export PATH=$PATH:$sdk_dir/tools/bin

# https://developer.android.com/ndk/downloads/
# place content of the folder in $sdk_dir/ndk-bundle

sdkmanager ndk-bundle
export PATH=$PATH:$sdk_dir/ndk-bundle

# https://github.com/kivy/python-for-android/blob/0.7.0/pythonforandroid/recipes/libffi/__init__.py#L13
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt install -y build-essential git zlib1g-dev python3 python3-dev libncurses5:i386 libstdc++6:i386 zlib1g:i386 unzip ant ccache autoconf libtool libssl-dev
sudo apt install -y automake libltdl-dev cmake gcc patch zip unzip

pip install cython virtualenv python-for-android

# https://stackoverflow.com/questions/60151351/what-is-the-proper-way-to-get-android-ndk-version
# https://developer.android.com/ndk/downloads/revision_history
# https://github.com/kivy/python-for-android/issues/2685
sdk_version="33"

sdkmanager "platforms;android-$sdk_version"
export ANDROIDSDK="$sdk_dir"
export ANDROIDNDK="$sdk_dir/ndk-bundle"
export ANDROIDAPI=$sdk_version  # Target API version of your application
export NDKAPI=$sdk_version  # Minimum supported API version of your application

echo $ANDROIDSDK

p4a apk --private $HOME/PycharmProjects/AndroidRemoteControlPy --package=org.positiveway.controllerpython --name "Controller Python" --version 0.1 --bootstrap=sdl2 --requirements=python3,kivy --arch=arm64-v8a

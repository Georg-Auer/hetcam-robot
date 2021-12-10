# How to set up a Raspberry 3b / 4 for use with the SPOC lab Microscope

# Download Raspberry Pi Imager and install the latest version of Raspberry OS
# on an SD card with at least 32 GB
# Create a file on the card named SSH (no file extension),
# the Raspberry can now be used "headless" over network without a display.
# https://www.raspberrypi.org/software/

# Now find the ip of the raspberry, it is displayed at the first boot
# (Display needed for this step)
# or found via Advanced IP Scanner (Windows) or nmap in linux
# Now install a X11 "X Server" on your machine,
# for instance VcXSrv https://sourceforge.net/projects/vcxsrv/ in Windows 10,
# or xquartz for Mac OS X http://xquartz.macosforge.org/
# Login via SSH, for instance PuTTy in Windows 10 or MacOS X (enable X11!)
# login with username: "pi" and password "raspberry"

# Now change password with raspi-config for security reasons with:
# sudo raspi-config
# Expand the filesystem with: “7 Advanced Options” menu item if applicable

# https://git-scm.com/book/en/v2/Git-Tools-Submodules
# git clone git@github.com:spoc-lab/delta-microscope.git
# git submodule init
# git submodule update

# clone with yolov5 submodule:
# cd ~
# git clone --recurse-submodules https://github.com/spoc-lab/delta-microscope.git
# git clone --recurse-submodules https://github.com/georg-auer/delta-microscope.git

# The rest is automatically done with this script
# or could be done by copying/executing its content
# first, go into the newly created git folder and make the .sh executable
# cd ~
# cd delta-microscope
# chmod +x ./raspberry-setup.sh
# # then execute the script with
# ./raspberry-setup.sh
# the local python3 will be modified (!)

# if raspberry os lite 64 is installed:
sudo apt install --upgrade python3-pip -y
sudo apt install --upgrade git -y
# upgrades:
sudo apt update -y
sudo apt upgrade -y
# cleanup
sudo apt clean -y
sudo apt autoremove -y
#sudo apt-get install -y libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev  libqtgui4  libqt4-test
# install opencv prerequisites on raspberry OS, using preinstalled python3.7
sudo apt install -y libaom0 libatk-bridge2.0-0 libatk1.0-0 libatlas3-base libatspi2.0-0
sudo apt install -y libavcodec58 libavformat58 libavutil56 libbluray2 libcairo-gobject2
sudo apt install -y libcairo2 libchromaprint1 libcodec2-0.8.1 libcroco3 libdatrie1 libdrm2
sudo apt install -y libepoxy0 libfontconfig1 libgdk-pixbuf2.0-0 libgfortran5 libgme0
sudo apt install -y libgraphite2-3 libgsm1 libgtk-3-0 libharfbuzz0b libilmbase23 libjbig0
sudo apt install -y libmp3lame0 libmpg123-0 libogg0 libopenexr23 libopenjp2-7 libopenmpt0
sudo apt install -y libopus0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0
sudo apt install -y librsvg2-2 libshine3 libsnappy1v5 libsoxr0 libspeex1 libssh-gcrypt-4
sudo apt install -y libswresample3 libswscale5 libthai0 libtheora0 libtiff5 libtwolame0
sudo apt install -y libva-drm2 libva-x11-2 libva2 libvdpau1 libvorbis0a libvorbisenc2
sudo apt install -y libvorbisfile3 libvpx5 libwavpack1 libwayland-client0 libwayland-cursor0
sudo apt install -y libwayland-egl1 libwebp6 libwebpmux3 libx264-155 libx265-165 libxcb-render0
sudo apt install -y libxcb-shm0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6
sudo apt install -y libxinerama1 libxkbcommon0 libxrandr2 libxrender1 libxvidcore4 libzvbi0
sudo apt install -y cmake # for scikit-image
sudo apt install -y libssl-dev # for scikit-image
sudo apt install -y libopenblas-dev libblas-dev m4 cmake cython
sudo pip3 install --upgrade pip
# install of the requirements:
sudo pip3 install -r requirements.txt
# torch and torchvision for armv7
# # for 64 bit emergency install only:
# sudo apt install -y python3-devpython3-yamlpython3-setuptools
# sudo apt install -y python3-matplotlib python3-numpy python3-scipy
# sudo apt install -y python3-opencv python3-pandas python3-dev
# installation of torch and torchvision for raspberry os 32bit:
# if 64 bit, this will be invalid anyways
# cd ~
# mkdir Downloads
# cd ~/Downloads
# git clone https://github.com/Kashu7100/pytorch-armv7l.git
# cd pytorch-armv7l
# sudo pip3 install torch-1.7.0a0-cp37-cp37m-linux_armv7l.whl
# sudo pip3 install torchvision-0.8.0a0+45f960c-cp37-cp37m-linux_armv7l.whl
# cd ~
#installing on 64bit, if it did not work earlier:
sudo pip3 install torch -f https://torch.kmtea.eu/whl/stable.html
sudo pip3 install torchvision -f https://torch.kmtea.eu/whl/stable.html
# building does not work because scipy==1.1 is installed via apt and >=1.5 needed
# building scipy does not work either
# command line only install:
# https://www.pjrc.com/teensy/td_download.html

mkdir Downloads
cd ~/Downloads
wget https://downloads.arduino.cc/arduino-1.8.16-linuxarm.tar.xz
wget https://www.pjrc.com/teensy/td_155/TeensyduinoInstall.linuxarm
wget https://www.pjrc.com/teensy/00-teensy.rules
sudo cp 00-teensy.rules /etc/udev/rules.d/
tar -xf arduino-1.8.16-linuxarm.tar.xz
cd arduino-1.8.16
sudo ./install.sh
cd ~/Downloads
chmod 755 TeensyduinoInstall.linuxarm
./TeensyduinoInstall.linuxarm --dir=arduino-1.8.16
cd arduino-1.8.16/hardware/teensy/avr/cores/teensy4
make
cd ~/Downloads

# wget https://www.pjrc.com/teensy/td_153/TeensyduinoInstall.linuxarm # compatible with arduino 1.8.13
# sudo chmod 755 TeensyduinoInstall.linuxarm
# ./TeensyduinoInstall.linuxarm
#choose where you put the installation files in the GUI(!) with X11
# sudo rm -rf TeensyduinoInstall.linuxarm
# cd ~
# wget https://downloads.arduino.cc/arduino-1.8.13-linuxarm.tar.xz
# wget https://www.pjrc.com/teensy/td_154/TeensyduinoInstall.linuxarm
# wget https://www.pjrc.com/teensy/00-teensy.rules
# sudo cp 00-teensy.rules /etc/udev/rules.d/
# tar -xf arduino-1.8.13-linuxarm.tar.xz
# chmod 755 TeensyduinoInstall.linuxarm
# ./TeensyduinoInstall.linuxarm --dir=arduino-1.8.13
# cd arduino-1.8.13/hardware/teensy/avr/cores/teensy4
# make


# install for 64bit
# for 64 bit:
# wget https://www.pjrc.com/teensy/td_153/TeensyduinoInstall.linuxaarch64 # compatible with arduino 1.8.13
# sudo chmod 755 TeensyduinoInstall.linuxaarch64
# ./TeensyduinoInstall.linuxaarch64
# #choose where you put the installation files in the GUI(!) with X11
# sudo rm -rf TeensyduinoInstall.linuxaarch64
# cd ~
# wget https://downloads.arduino.cc/arduino-1.8.15-linuxaarch64.tar.xz
# wget https://www.pjrc.com/teensy/td_154/TeensyduinoInstall.linuxaarch64
# wget https://www.pjrc.com/teensy/00-teensy.rules
# sudo cp 00-teensy.rules /etc/udev/rules.d/
# tar -xf arduino-1.8.15-linuxaarch64.tar.xz
# chmod 755 TeensyduinoInstall.linuxaarch64
# ./TeensyduinoInstall.linuxaarch64 --dir=arduino-1.8.15
# cd arduino-1.8.15/hardware/teensy/avr/cores/teensy4
# make

# now choose a picture folder, and install
# now just go to the ip of the raspberry in any browser, it should open the web interface

# how to run on boot:
# sudo nano /etc/rc.local
# insert:
# cd home/pi/delta-microscope
# sudo CAMERA=opencv python3 run.py &

# # python 3.8.9 install
# sudo mkdir ~/Downloads
# cd ~/Downloads
# wget https://www.python.org/ftp/python/3.8.9/Python-3.8.9.tgz
# # installing python 3.8 on raspberry os
# sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev tar wget vim
# sudo tar zxf Python-3.8.9.tgz
# cd Python-3.8.9
# sudo ./configure --enable-optimizations
# make altinstall 

# # python 3.9.6 install on raspberry os
# sudo apt install -y wget build-essential libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
# sudo mkdir ~/Downloads
# cd ~/Downloads
# wget https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz
# sudo tar zxf Python-3.9.5.tgz
# cd Python-3.9.5
# sudo ./configure --enable-optimizations
# make altinstall 

# check if any python processes are running
# pgrep -lf python
# killing a process
# ps -ef | grep python
# kill <PID found previously>
# or:
# kill -9 <PID found previously>

# install arduino with gui:
# #arduino:
# # to avoid a bug that stops creating the Arduino IDE icon:
# mkdir -p $HOME/.local/share/icons/hicolor
# cd ~
# mkdir Applications
# cd ~/Applications
# wget arduino-1.8.13-linuxarm.tar.xz https://downloads.arduino.cc/arduino-1.8.13-linuxarm.tar.xz
# tar xvJf arduino-1.8.13-linuxarm.tar.xz
# cd arduino-1.8.13/
# ./install.sh
# rm ../arduino-1.8.13-linuxarm.tar.xz

# #teensy:
# cd /etc/udev/rules.d/
# sudo wget https://www.pjrc.com/teensy/49-teensy.rules
# # sudo cp /tmp/49-teensy.rules /etc/udev/rules.d/
# cd ~
# mkdir Downloads
# cd ~/Downloads
# # for 32 bit:
# wget https://www.pjrc.com/teensy/td_153/TeensyduinoInstall.linuxarm # compatible with arduino 1.8.13
# sudo chmod 755 TeensyduinoInstall.linuxarm
# ./TeensyduinoInstall.linuxarm
# #choose where you put the installation files in the GUI(!) with X11
# sudo rm -rf TeensyduinoInstall.linuxarm
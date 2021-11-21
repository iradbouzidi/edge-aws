FROM arm32v7/python:3.7-slim-buster


RUN apt-get -qy clean \ 
        && apt-get -qy update \
        && apt-get -qy install cmake build-essential pkg-config \
        && apt-get -qy install libsm6 libxext6 libxrender-dev libhdf5-103 libaom0 libatk-bridge2.0-0 libatk1.0-0 libatlas3-base libatspi2.0-0 libavcodec58 libavformat58 libavutil56 libbluray2 libcairo-gobject2 libcairo2 libchromaprint1 libcodec2-0.8.1 libcroco3 libdatrie1 libdrm2 libepoxy0 libfontconfig1 libgdk-pixbuf2.0-0 libgfortran5 libgme0 libgraphite2-3 libgsm1 libgtk-3-0 libharfbuzz0b libilmbase23 libjbig0 libmp3lame0 libmpg123-0 libogg0 libopenexr23 libopenjp2-7 libopenmpt0 libopus0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 librsvg2-2 libshine3 libsnappy1v5 libsoxr0 libspeex1 libssh-gcrypt-4 libswresample3 libswscale5 libthai0 libtheora0 libtiff5 libtwolame0 libva-drm2 libva-x11-2 libva2 libvdpau1 libvorbis0a libvorbisenc2 libvorbisfile3 libvpx5 libwavpack1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libwebp6 libwebpmux3 libx264-155 libx265-165 libxcb-render0 libxcb-shm0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxinerama1 libxkbcommon0 libxrandr2 libxrender1 libxvidcore4 libzvbi0

RUN apt-get -qy clean \
	&& apt-get -qy autoclean \
	&& apt-get -qy autoremove \
	&& rm -rf /var/lib/{apt,dpkg,cache,log}


RUN pip3 install face_recognition==1.3.0 \
    requests==2.25.1 \
    numpy==1.20.2 \
    flask_opencv_streamer \
    opencv-python==4.5.1.48 -i https://www.piwheels.org/simple --no-cache-dir

EXPOSE 3030

ADD recognition/recognition.py /

CMD [ "python3", "./recognition.py" ]
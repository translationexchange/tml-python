FROM ubuntu:14.04
MAINTAINER Chris Rose <offline@offby1.net>

# ensure the base image has what we need
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -yqq install \
    build-essential python-pip software-properties-common \
    openjdk-7-jdk && \
    add-apt-repository ppa:fkrull/deadsnakes && \
    apt-get update

# install legacy python versions
RUN DEBIAN_FRONTEND=noninteractive apt-get -yqq install \
    memcached libmemcached-dev libxml2-dev libxslt1-dev zlib1g-dev libcurl4-openssl-dev \
    python-dev python3-dev python3.3-dev python3.4-dev python3.5-dev \
    python2.5 python2.6 python2.7 python3.1 python3.2 python3.3 python3.4 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# add Jython installer
# ADD jython-installer-2.7-b4.jar /tmp/
ADD http://search.maven.org/remotecontent?filepath=org/python/jython-installer/2.7-b4/jython-installer-2.7-b4.jar /tmp/jython-installer-2.7-b4.jar

# install pypy versions
# ADD pypy-2.5.0-linux64.tar.bz2 /opt/
# ADD pypy3-2.4.0-linux64.tar.bz2 /opt/
RUN mkdir -p /opt
ADD https://bitbucket.org/pypy/pypy/downloads/pypy3-2.4.0-linux64.tar.bz2 /tmp/
RUN cd /opt && tar -xf /tmp/pypy3-2.4.0-linux64.tar.bz2
ADD https://bitbucket.org/pypy/pypy/downloads/pypy-2.5.0-linux64.tar.bz2 /tmp/
RUN cd /opt && tar -xf /tmp/pypy-2.5.0-linux64.tar.bz2

# install Jython version
RUN java -jar /tmp/jython-installer-2.7-b4.jar -d /opt/jython-2.7-b4 -s -t all
ENV PATH /opt/jython-2.7-b4/bin:$PATH
# bootstrap jython JAR cache
RUN jython

# make PyPy available
ENV PATH /opt/pypy-2.5.0-linux64/bin:/opt/pypy3-2.4.0-linux64/bin:$PATH

ENV PYTHON_BUILD_DOCKER=true

# install tox
RUN pip install tox

ADD clean-launch.sh /tools/clean-launch.sh

VOLUME /src
WORKDIR /src

ENTRYPOINT ["/tools/clean-launch.sh"]
CMD ["tox", "tests/unit tests/integration"]
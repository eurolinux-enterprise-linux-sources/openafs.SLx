#!/bin/bash

l1=`grep elease /etc/redhat-release`

l=${l1##*elease }
l=${l%% \(*}

rls=unknown

echo $l | grep -q '^\(4\.9[0-9]\|5\.[0-9]\|5\.1[0-9]\|5\)$' && {
    rls=5
    echo '%define SL5 1'
    echo '%define SL6 0'
    echo '%define SL7 0'
    echo "%define SLrelease sl5"
}

echo $l | grep -q '^6\.[0-9]\( Beta\)\?$' && {
    rls=6
    echo '%define SL5 0'
    echo '%define SL6 1'
    echo '%define SL7 0'
    echo "%define SLrelease sl6"
}

echo $l | grep -q '^7\.[0-9]\( Beta\|\.[0-9][0-9][909][0-9]\)\?$' && {
    rls=7
    echo '%define SL5 0'
    echo '%define SL6 0'
    echo '%define SL7 1'
    echo "%define SLrelease sl7"
}

if [ $# -gt 0 -a "$1" != "" ]; then
    kernel=$1
else
    kernel=`uname -r`
fi

kernel=${kernel%.i686}
kernel=${kernel%.x86_64}
unamem=`uname -m`

if [ $rls = 5 ]; then
    unamer=$kernel
    ksrcdir=/usr/src/kernels/$kernel-$unamem
else
    unamer=$kernel.$unamem
    ksrcdir=/usr/src/kernels/$unamer
fi

kmoddir=/lib/modules/${unamer}/extra/openafs
kmoddst=/lib/modules/${unamer}/kernel/fs/openafs
kbuildreq="kernel-devel-$unamem = $kernel"
kreq="kernel-$unamem = $kernel"

kmodrelsfx=${kernel#*-}
kmodrelsfx=${kmodrelsfx%.*}

krelmajor=${kmodrelsfx%%.*}

echo "%define unamer $unamer"
echo "%define kernel $kernel"
echo "%define kmoddir $kmoddir"
echo "%define kmoddst $kmoddst"
echo "%define ksrcdir $ksrcdir"
echo "%define kbuildreq $kbuildreq"
echo "%define kreq $kreq"
echo "%define kmodrelsfx $kmodrelsfx"
echo "%define krelmajor $krelmajor"

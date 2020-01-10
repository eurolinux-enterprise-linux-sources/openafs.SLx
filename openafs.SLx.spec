%define afsvers 1.6.20
%define pkgrel 256
#define plevel .z2


# For betas, release candidates:
%if %(echo %{pkgrel} | grep -c '\(rc\|fc\|pre\)')
  %define pre_x %(echo %{pkgrel} |sed -e 's/.*\\(rc\\|fc\\|pre\\)/\\1/')
%else
  %define pre_x %nil
%endif
%define srcvers %{afsvers}%{pre_x}

# This script will define the following macros:
#
# SL5           1 on SL5, 0 on other releases
# SL6           1 on SL6, 0 on other releases
# SL7           1 on SL7, 0 on other releases
# ...
# SLrelease     sl5 on SL5, sl6 on SL6, sl7 on SL7, ...
# unamer        uname -r output
# kernel        uname -r output, with trailing arch stripped on SL6
# kmoddir       where the module is installed by make dest
# kmoddst       where the module will end up in the package
# ksrcdir       where to find the kernel headers to build against
# kbuildreq     the build time requirement on kernel-devel
# kreq          the runtime requirement of the module on the kernel
# kmodrelsfx    the suffix identifying the build kernel for the kmod release
# krelmajor     the first set of digits in the kernel release, after the dash

%{expand:%(%{_sourcedir}/openafs-sl-defs.sh %{?kernel})}

%if %SL7
  %if 0%{!?nsfx:1}
    %define nsfx -1.6-sl
  %endif
%endif

# Determine which elements of OpenAFS to build.  Since we now hopefully
# build usable debuginfo packages, building the module and userspace in
# one go is no longer possible:

%define build_modules_on_cmdline %{?build_modules:1}%{!?build_modules:0}
%define build_kmod_on_cmdline  %{?build_kmod:1}%{!?build_kmod:0}

%define build_userspace 1
%define debugpkgname openafs%{?nsfx}-debuginfo

%if %{build_modules_on_cmdline}
  %if %{build_modules}
    %define build_userspace 0
    %define debugpkgname kernel-module-openafs%{?nsfx}-%{kernel}-debuginfo
  %endif
%else
  %define build_modules 0
%endif

%if %{build_kmod_on_cmdline}
  %if %{build_kmod}
    %define build_userspace 0
    %define build_modules 0
    %define debugpkgname kmod-openafs%{?nsfx}-%{krelmajor}-debuginfo
  %endif
%else
  %define build_kmod 0
%endif

%if %SL5 || %SL6
  %define sbin /sbin
%else
  %define sbin %{_sbindir}
%endif
%define depmod %{sbin}/depmod

# The actual release tag for all binary packages:
%if %build_kmod
    %define pkgrelx %{pkgrel}%{?plevel}.%{SLrelease}.%{kmodrelsfx}
%else
    %define pkgrelx %{pkgrel}%{?plevel}.%{SLrelease}
%endif

# Override the debuginfo package name. On SL5, this could be done inline,
# but older RPM versions require the external script:
%{expand:%(%{_sourcedir}/openafs-debugpackage.sh)}

# Set 'debugspec' to 1 if you want to debug the spec file.  This will
# not remove the installed tree as part of the %clean operation
%if %{?debugspec:0}%{!?debugspec:1}
%define debugspec 0
%endif

# Build with '--without krb5' if you don't want to build the openafs-krb5
# package to distribute aklog and asetkey
%define krb5support %{?_without_krb5:0}%{!?_without_krb5:1}

# OpenAFS configuration options. E.g., build '--without fast_restart' .
%define enable_bitmap_later %{?_without_bitmap_later:0}%{!?_without_bitmap_later:1}
%define enable_bos_restricted_mode %{?_without_bos_restricted_mode:0}%{!?_without_bos_restricted_mode:1}
%define enable_bos_new_config %{?_without_bos_new_config:0}%{!?_without_bos_new_config:1}
%define enable_fast_restart %{?_without_fast_restart:0}%{!?_without_fast_restart:1}
%define enable_supergroups %{?_without_supergroups:0}%{!?_without_supergroups:1}
%define enable_largefile_fileserver %{?_without_largefile_fileserver:0}%{!?_without_largefile_fileserver:1}
%define enable_fuse_client %{?_without_fuse_client:0}%{!?_without_fuse_client:1}
%define enable_debugsyms %{?_without_debugsyms:0}%{!?_without_debugsyms:1}


# Define the location of your init.d directory
%define initdir /etc/rc.d/init.d

# Define the location of the PAM security module directory
%define pamdir /%{_lib}/security

# Define the default size (in KB) and the location of the client cache
%define defcachesize 100000
%if %SL5
  %define defcachedir /var/cache/openafs
%else
  %define defcachedir /var/cache/afs
%endif
%if %SL5 || %SL6
  %define defdynrootsparse off
%else
  %define defdynrootsparse on
%endif

#######################################################################
# You probably don't need to change anything beyond this line

Summary: OpenAFS Distributed Filesystem
Name: openafs.SLx
Version: %{afsvers}
Release: %{pkgrel}%{?plevel}
Epoch: 0
License: IBM Public License
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Vendor: Scientific Linux
Group: Networking/Filesystems
%if %build_modules || %build_kmod || ! %SL5
ExclusiveArch: i686 x86_64
%else
ExclusiveArch: i386 i686 x86_64
%endif
BuildRequires: make
BuildRequires: pam-devel
BuildRequires: gcc
BuildRequires: flex
BuildRequires: bison
BuildRequires: ncurses-devel
BuildRequires: perl
BuildRequires: redhat-rpm-config
# if we need to run regen.sh:
BuildRequires: autoconf
BuildRequires: automake
%if %enable_fuse_client
BuildRequires: fuse-devel
%endif
%if %SL7
BuildRequires: systemd
%endif
%if %{?_with_modsign:1}%{!?_with_modsign:0}
BuildRequires: openssl
%endif

Source0: http://www.openafs.org/dl/openafs/%{afsvers}/openafs-%{srcvers}-src.tar.bz2
Source1: http://www.openafs.org/dl/openafs/%{afsvers}/openafs-%{srcvers}-doc.tar.bz2
Source2: openafs-SL-ThisCell
Source3: openafs-SL-CellServDB.20130128
Source5: openafs-SL-CellServDB-hepix.org

Source7: openafs-LICENSE.Sun
Source8: openafs-README
Source12: openafs-CellAlias

Source30: http://www.tu-chemnitz.de/urz/afs/openafs/download/suse-7.2/SOURCES/openafs-killafs

Source42: openafs-rc.client
Source43: openafs-rc.server
Source44: openafs-sysconfig
Source45: afs.service
Source46: afs-server.service
Source47: afs.preset
Source48: afs-server.preset

Source60: ChangeLog
Source61: RELNOTES-%{srcvers}
Source62: SECURITY.txt

Source995: openafs-modules
Source996: patch-weak-modules.sh
Source997: kmodtool-el6-openafs.sh
Source998: openafs-debugpackage.sh
Source999: openafs-sl-defs.sh

# the last patch # used was 1079, future patches should use 1080+
#Patch1079: openafs-1.6-bos.patch
#Patch1080: openafs-1.6.5.1-gerrit10578.patch
# 1081/2/3 are the security fixes from 1.6.7:
#Patch1081: openafs-1.6.5.1-rx-Split-out-rxi_SendConnectionAbortLater.patch
#Patch1082: openafs-1.6.5.1-rx-Avoid-rxi_Delay-on-RXS_CheckResponse-failure.patch
#Patch1083: openafs-1.6.5.1-viced-fix-get-statistics64-buffer-overflow.patch
#Patch1084: openafs-1.6.10-revert-gerrit-11358.patch
#Patch1085: openafs-1.6.10-aklog524.patch

%description
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This is the source package common to all builds on Scientific Linux 5/6/7.
There is no corresponding binary package. Instead, all binary packages have
their conventional names, and a suffix .sl5 (6,...) added to the package
release.

Rebuilding this SRPM will yield either all the userspace packages, or a
kernel-module package for one particular kernel, or a kmod package:

o Without extra switches, the userland packages are built.

o With "--define 'build_modules 1'", the kernel-module- package is built (only).
  On 32bit SL5, the "--target i686" switch  still needs to be given, but
  it's not sufficient to get the module built.

o With "--define 'build_kmod 1'", the kmod-openafs package is built (only).
  This is not supported on SL5 and probably won't work there.

By default, the kernel module is built for the running kernel. To change
this, use "--define 'kernel <Version-ReleaseVariant>'". The right value
is the output "uname -r" would yield under the desired kernel. On SL6/7,
it doesn't matter whether the trailing architecture is stripped off.

As of SL7, signing the kernel module is supported. To do this, build with
"--with modsign". The default locations of the private and public keys are
%{_sysconfdir}/pki/SECURE-BOOT-KEY.{priv,der} but can be overridden with
"--define 'privkey /some/path'" and "--define 'pubkey /some/path/'".

The matching kernel-devel package must be installed on the build system.

The following server features are by default turned on but can be disabled
from the build command line:

   To disable            build with
   ===================   ==============================
   bitmap-later          --without bitmap_later          
   bos-restricted-mode   --without bos_restricted_mode 
   bos-new_config        --without bos_new_config
   fast-restart          --without fast_restart
   supergroups           --without supergroups
   largefile-fileserver  --without largefile_fileserver
   fuse-client           --without fuse_client
   debug(-kernel)        --with debugsyms

The following features are disabled by default but can be enabled
from the build command line:

   To enable             build with
   ====================  ===============================


%package -n openafs%{?nsfx}
Release: %{pkgrelx}
Summary: OpenAFS Distributed Filesystem
Group: Networking/Filesystem

%description -n openafs%{?nsfx}
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides common files shared across all the various
OpenAFS packages but are not necessarily tied to a client or server.

###############################################################################
#
# build the userspace side of things if so requested
#
###############################################################################
%if %{build_userspace}

%package -n openafs%{?nsfx}-client
Release: %{pkgrelx}
Requires: binutils, openafs%{?nsfx}-kernel >= 1.6, openafs%{?nsfx} = %{afsvers}
%if %SL7
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Provides: openafs-sl-client = %{version}
%endif
Summary: OpenAFS Filesystem Client
Group: Networking/Filesystem

%description -n openafs%{?nsfx}-client
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides basic client support to mount and manipulate
AFS.

Configure options enabled for this build:

  fuse-client:          %enable_fuse_client
  debugsyms:            %enable_debugsyms

%package -n openafs%{?nsfx}-server
Release: %{pkgrelx}
Requires: openafs%{?nsfx} = %{afsvers}
%if %SL7
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
Summary: OpenAFS Filesystem Server
Group: Networking/Filesystems

%description -n openafs%{?nsfx}-server
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides basic server support to host files in an AFS
Cell.

Configure options enabled for this build:

  bitmap-later:         %enable_bitmap_later
  bos-restricted-mode:  %enable_bos_restricted_mode
  bos-new-config:       %enable_bos_new_config
  fast-restart:         %enable_fast_restart
  supergroups:          %enable_supergroups
  largefile-fileserver: %enable_largefile_fileserver
  debugsyms:            %enable_debugsyms

%package -n openafs%{?nsfx}-authlibs
Release: %{pkgrelx}
Summary: OpenAFS Authentication Shared Libraries
Group: Networking/Filesystems

%description -n openafs%{?nsfx}-authlibs
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides a shared version of libafsrpc and libafsauthent. 
None of the programs included with OpenAFS currently use these shared 
libraries; however, third-party software that wishes to perform AFS 
authentication may link against them.

%package -n openafs%{?nsfx}-authlibs-devel
Release: %{pkgrelx}
Requires: openafs%{?nsfx}-authlibs = %{afsvers}
Requires: openafs%{?nsfx}-devel = %{afsvers}
AutoReq: Off
Summary: OpenAFS Shared Library Development
Group: Development/Filesystems

%description -n openafs%{?nsfx}-authlibs-devel
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package includes symlinks required for building against the dynamic 
version of libafsrpc and libafsauthent.

%package -n openafs%{?nsfx}-devel
Release: %{pkgrelx}
Summary: OpenAFS Development Libraries and Headers
Group: Development/Filesystems

%description -n openafs%{?nsfx}-devel
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides static development libraries and headers needed
to compile AFS applications.  Note: AFS currently does not provide
shared libraries.

%package -n openafs%{?nsfx}-plumbing-tools
Release: %{pkgrelx}
Summary: OpenAFS Additional Debugging Utilities
Group: Networking/Filesystems
Obsoletes: openafs-debug

%description -n openafs%{?nsfx}-plumbing-tools
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides additional tools useful for understanding and
debugging the client and server. It is completely optional.

%package -n openafs%{?nsfx}-module-tools
Release: %{pkgrelx}
Summary: OpenAFS analogon to weak-modules
Group: Networking/Filesystems
License: GPLv2+

%description -n openafs%{?nsfx}-module-tools
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides scripts for making the kernel module availabe to compatible kernels.


%endif
#build_userspace
###############################################################################
#
# build the kernel modules if so requested
#
###############################################################################
%if %{build_modules}

%package -n kernel-module-openafs%{?nsfx}-%{kernel}
Release: %{pkgrelx}
Summary: OpenAFS Kernel Module for Kernel %kernel
Requires: openafs%{?nsfx} = %{afsvers}
Requires: kernel-%{_target_cpu} = %{kernel}
%if %SL5 || %SL6
Requires(post): /%{sbin}/modprobe
Provides: openafs%{?nsfx}-kernel
%else
Requires(post): kmod
Provides: openafs%{?nsfx}-kernel = %{version}
%endif
Group: Networking/Filesystems
BuildRequires: %{kbuildreq}

%description -n kernel-module-openafs%{?nsfx}-%{kernel}
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides an openafs kernel module for
kernel %{kernel} and architecture %{_target_cpu}.

%endif
#build modules

%if %{build_kmod}

%package -n openafs%{?nsfx}-kmod
Summary: This is really just a dummy to get the build requirement
Group: Networking/Filesystems
BuildRequires: %{kbuildreq}

%description -n openafs%{?nsfx}-kmod
Dummy.

# *this* is the actual package:

# There are no kvariants.
%define kvariants ""

# Magic hidden here. The kmod_release=1 overrides the 
%define kmodtool kmod_release=1 sh %{SOURCE997}
%define kmod_name openafs%{?nsfx}-%{krelmajor}
%define kmod_release %{pkgrelx}
%{expand:%(%{kmodtool} rpmtemplate %{kmod_name} %{unamer} %{depmod} %{kvariants} 2>/dev/null)}

%endif
#build_kmod

%package -n openafs%{?nsfx}-kernel-source
Release: %{pkgrelx}
Summary: OpenAFS Kernel Module Source Tree
Group: Networking/Filesystems

%description -n openafs%{?nsfx}-kernel-source
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the source code to build your own AFS kernel
module.

%package -n openafs%{?nsfx}-compat
Release: %{pkgrelx}
Summary: OpenAFS Client Compatibility Symlinks
Requires: openafs%{?nsfx} = %{afsvers}, openafs%{?nsfx}-client = %{afsvers}
Group: Networking/Filesystems
Obsoletes: openafs-client-compat

%description -n openafs%{?nsfx}-compat
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides compatibility symlinks in /usr/afsws.  It is
completely optional, and is only necessary to support legacy
applications and scripts that hard-code the location of AFS client
programs.

%package -n openafs%{?nsfx}-kpasswd
Release: %{pkgrelx}
Summary: OpenAFS KA kpasswd Support
Requires: openafs%{?nsfx} = %{afsvers}
Group: Networking/Filesystems

%description -n openafs%{?nsfx}-kpasswd
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the compatibility symlink for kpasswd, in case
you are using KAserver instead of Krb5.

%if %{krb5support}
%package -n openafs%{?nsfx}-krb5
Release: %{pkgrelx}
Summary: OpenAFS Programs to use with krb5
Requires: openafs%{?nsfx} = %{afsvers}
Group: Networking/Filesystems
BuildRequires: krb5-devel

%description -n openafs%{?nsfx}-krb5
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides compatibility programs so you can use krb5
to authenticate to AFS services, instead of using AFS's homegrown
krb4 lookalike services.
%endif

###############################################################################
#
# preparation
#
###############################################################################

%prep

: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
: @@@ arch:                 %{_arch}
: @@@ target cpu:           %{_target_cpu}
: @@@ SL5:                  %SL5
: @@@ SL6:                  %SL6
: @@@ SL7:                  %SL7
: @@@ SLrelease:            %SLrelease
: @@@ name suffix:          %{?nsfx}
: @@@ kernel:               %{kernel}
: @@@ unamer:               %{unamer}
: @@@ kernel modules dir:   %{kmoddir}
: @@@ kernel modules dest:  %{kmoddst}
: @@@ kernel sources dir:   %{ksrcdir}
: @@@ kernel build req:     %{kbuildreq}
: @@@ kernel runtime req:   %{kreq}
: @@@ kernel RPM version:   kernel-module-openafs%{?nsfx}-%{kernel}
: @@@ build_userspace:      %{build_userspace}
: @@@ build_modules:        %{build_modules}
: @@@ build_kmod:           %{build_kmod}
: @@@ package release:      %{pkgrelx}
: @@@ kmod suffix:          %{kmodrelsfx}
: @@@ PAM modules dir:      %{pamdir}
: @@@
: @@@ bitmap-later:         %enable_bitmap_later
: @@@ bos-restricted-mode:  %enable_bos_restricted_mode
: @@@ bos-new-config:       %enable_bos_new_config
: @@@ fast-restart:         %enable_fast_restart
: @@@ supergroups:          %enable_supergroups
: @@@ largefile-fileserver: %enable_largefile_fileserver
: @@@ fuse-client:          %enable_fuse_client
: @@@ debugsyms:            %enable_debugsyms
: @@@ debugspec:            %{debugspec}
: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

%setup -q -b 1 -n openafs-%{srcvers}

#patch1078 -p1 -b .fix-8608
#patch1079 -p1 -b .bos
#patch1080 -p1 -b .gerrit10578
#patch1081 -p1 -b .rx-Split-out-rxi_SendConnectionAbortLater
#patch1082 -p1 -b .rx-Avoid-rxi_Delay-on-RXS_CheckResponse-failure
#patch1083 -p1 -b .viced-fix-get-statistics64-buffer-overflow
#patch1084 -p1 -b .revert-gerrit-11358
#patch1085 -p1 -b .aklog524

# add some info to "rxdebug -version" output:
sed -i s/built\ /built/ src/config/Makefile.version-NOCML.in
sed -i s/\'\"\;/\''(%{release}@%(hostname -d))'\"\;/ \
    src/config/Makefile.version-NOCML.in

# vim, your syntax highlighting needs some help '

###############################################################################
#
# building
#
###############################################################################

%build

case %{_arch} in
    x86_64)  sysname=amd64_linux26 ;;
    i?86)    sysname=i386_linux26  ;;
esac


config_opts=" \
%if %{enable_bitmap_later}
        --enable-bitmap-later \
%endif
%if %{enable_bos_restricted_mode}
        --enable-bos-restricted-mode \
%endif
%if %{enable_fast_restart}
        --enable-fast-restart \
%endif
%if %{enable_bos_new_config}
        --enable-bos-new-config \
%endif
%if %{enable_supergroups}
        --enable-supergroups \
%endif
%if ! %{enable_largefile_fileserver}
        --disable-largefile-fileserver \
%endif
%if ! %{enable_fuse_client}
        --disable-fuse-client \
%endif
%if %{enable_debugsyms}
        --enable-debug \
        --enable-debug-kernel \
%endif
        --enable-transarc-paths"

# Configure AFS

CFLAGS="$RPM_OPT_FLAGS"; export CFLAGS

%if %{krb5support}
PATH=/usr/kerberos/bin:$PATH \
%endif
./configure --with-afs-sysname=${sysname} \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --bindir=%{_bindir} \
        --sbindir=%{_sbindir} \
        --disable-strip-binaries \
%if %{build_modules} || %{build_kmod}
        --with-linux-kernel-packaging \
        --with-linux-kernel-headers=%{ksrcdir} \
%else
        --disable-kernel-module \
%endif
%if %{krb5support}
        --with-krb5-conf \
%endif
        $config_opts


%if %{build_userspace}
# Build the user-space AFS stuff
make %_smp_mflags dest_nolibafs

# Build the libafs tree
make %_smp_mflags only_libafs_tree

# additional debugging tools

make -C src/venus   afsio
make -C src/venus   cacheout
make -C src/venus   twiddle
make -C src/venus   whatfid
make -C src/tests   dumptool
make -C src/tests   afsdump_scan
make -C src/tests   afsdump_extract
make -C src/tests   fsx
make -C src/vol     vol-bless
make -C src/auth    setkey
make -C src/rx/test rxperf
make -C src/rx/test th_rxperf

%endif
#build_userspace

%if %{build_modules} || %{build_kmod}
  make %_smp_mflags dest_only_libafs
%endif

###############################################################################
#
# installation
#
###############################################################################

%install
[ %{buildroot} != / ] && rm -rf %{buildroot}

case %{_arch} in
    x86_64)  sysname=amd64_linux26 ;;
    i?86)    sysname=i386_linux26  ;;
esac

umask 022

# Build install tree
%if %{build_userspace}
mkdir -p %{buildroot}/afs
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}/%{sbin}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}/etc/sysconfig
mkdir -p %{buildroot}%{initdir}
mkdir -p %{buildroot}/etc/openafs
mkdir -p %{buildroot}%{pamdir}
mkdir -p %{buildroot}%{_prefix}/afs/logs
mkdir -p %{buildroot}%{_prefix}/afs/debug
mkdir -p %{buildroot}%{_prefix}/afs/etc
mkdir -p %{buildroot}%{_prefix}/vice/etc
mkdir -p %{buildroot}%{defcachedir}
chmod 700 %{buildroot}%{defcachedir}
mkdir -p %{buildroot}%{_mandir}/man1

# Copy files from dest to the appropriate places in BuildRoot
tar cf - -C ${sysname}/dest bin include | tar xf - -C %{buildroot}%{_prefix}
tar cf - -C ${sysname}/dest/lib . | tar xf - -C %{buildroot}%{_libdir}
tar cf - -C ${sysname}/dest/etc . | tar xf - -C %{buildroot}%{_sbindir}
tar cf - -C ${sysname}/dest/root.server%{_prefix}/afs bin | tar xf - -C %{buildroot}%{_prefix}/afs
tar cf - -C ${sysname}/dest/root.client%{_prefix}/vice/etc afsd{,.fuse} C | tar xf - -C %{buildroot}%{_prefix}/vice/etc

# Link kpasswd to kapasswd
mv -f %{buildroot}%{_bindir}/kpasswd %{buildroot}%{_bindir}/kpasswd.openafs
ln -f %{buildroot}%{_bindir}/kpasswd.openafs %{buildroot}%{_bindir}/kapasswd
mv -f %{buildroot}%{_bindir}/pagsh %{buildroot}%{_bindir}/pagsh.openafs

# Copy root.client config files
install -m 755 %{SOURCE44} %{buildroot}/etc/sysconfig/afs

# change default configuration
sed -i 's/^CACHESIZE=.*/CACHESIZE=%{defcachesize}/' \
    %{buildroot}/etc/sysconfig/afs
sed -i 's@^CACHEDIR=.*@CACHEDIR=%{defcachedir}@' \
    %{buildroot}/etc/sysconfig/afs
sed -i 's/ENABLE_DYNROOT_SPARSE=.*/ENABLE_DYNROOT_SPARSE=%{defdynrootsparse}/' \
    %{buildroot}/etc/sysconfig/afs

# Copy PAM modules
install -m 755 ${sysname}/dest/lib/pam* %{buildroot}%{pamdir}

# PAM symlinks
ln -sf pam_afs.so.1 %{buildroot}%{pamdir}/pam_afs.so
ln -sf pam_afs.krb.so.1 %{buildroot}%{pamdir}/pam_afs.krb.so


uve=%{buildroot}%{_prefix}/vice/etc
install -p -m 644 %{SOURCE2} $uve/ThisCell
install -p -m 644 %{SOURCE12} $uve/CellAlias
install -p -m 644 %{SOURCE3} $uve/CellServDB
echo "/afs:%{defcachedir}:%{defcachesize}" > $uve/cacheinfo
chmod 644 $uve/cacheinfo
#
install -p -m 755 %{SOURCE30} $uve/killafs

# add hepix.org
grep -q '>hepix.org' $uve/CellServDB || cat %{SOURCE5} >> $uve/CellServDB

# extra debugging tools
mkdir -p %{buildroot}%{_prefix}/afs/debug
for i in \
    src/viced/cbd \
    src/viced/fsprobe \
    src/viced/check_sysid \
    src/auth/setkey \
    src/fsprobe/fsprobe_test \
    src/rxdebug/rxdumptrace \
    src/venus/cacheout \
    src/venus/twiddle \
    src/venus/whatfid \
    src/venus/test/getinitparams \
    src/tests/dumptool \
    src/tests/afsdump_scan \
    src/tests/afsdump_extract \
    src/tests/fsx \
    src/ubik/utst_client \
    src/ubik/utst_server \
    src/vlserver/cnvldb \
    src/vlserver/vlclient \
    src/vol/vol-bless \
    src/ptserver/readgroup \
    src/ptserver/readpwd \
    src/ptserver/testpt \
    src/ptserver/db_verify \
    src/kauth/rebuild \
    src/libadmin/test/afscp \
    src/rx/test/rxperf \
    src/rx/test/th_rxperf \
    ;do
  install -p -m 755 $i %{buildroot}%{_prefix}/afs/debug
done

# extra tools
mkdir -p %{buildroot}%{_bindir}
for i in src/venus/afsio; do
    install -p -m 755 $i %{buildroot}%{_bindir}
done

# the kmod handling script:
mkdir -p %{buildroot}/%{sbin}
install -m 755 %{SOURCE995} %{buildroot}/%{sbin}
if [ "%{depmod}" != "/sbin/depmod" ]; then
   sed -i -e 's|/sbin/depmod|%{depmod}|' %{buildroot}/%{sbin}/openafs-modules
fi

#
# install kernel-source
#

# Install the kernel module source tree
mkdir -p %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/src
tar cf - -C libafs_tree . | \
        tar xf - -C %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/src

# Next, copy the LICENSE Files, README
install -m 644 src/LICENSE %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.IBM
install -m 644 %{SOURCE7} %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.Sun
install -m 644 %{SOURCE8} %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/README

install -m 755 %{SOURCE42} %{buildroot}%{initdir}/afs
install -m 755 %{SOURCE43} %{buildroot}%{initdir}/afs-server
%if %SL7
mkdir -p %{buildroot}%{_unitdir} %{buildroot}/%{sbin} %{buildroot}%{_presetdir}
install -m 644 %{SOURCE45} %{buildroot}%{_unitdir}/afs.service
install -m 644 %{SOURCE46} %{buildroot}%{_unitdir}/afs-server.service
install -m 644 %{SOURCE47} %{buildroot}%{_presetdir}/70-afs.preset
install -m 644 %{SOURCE48} %{buildroot}%{_presetdir}/70-afs-server.preset
touch %{buildroot}/etc/sysconfig/.afs.generated
touch %{buildroot}/etc/sysconfig/.afs-server.generated
%endif
#
# Install DOCUMENTATION
#

#
# Release Notes and Changelog
#
install -m 644 %SOURCE60 .
install -m 644 %SOURCE61 .

#
# Security note for 1.6.5
#
install -m 644 %SOURCE62 .

#
# man pages
#
tar cf - -C doc/man-pages man1 man5 man8 | \
    tar xf - -C %{buildroot}%{_mandir}

%if %{krb5support}
  # 
  mv %{buildroot}/usr/afs/bin/asetkey %{buildroot}%{_sbindir}
  ln -s klog.krb5 %{buildroot}%{_bindir}/k5log
  cp %{buildroot}%{_mandir}/man1/klog.krb5.1 %{buildroot}%{_mandir}/man1/k5log.1
%endif

# remove unused man pages
for f in 1/compile_et 1/copyauth 1/dlog 1/dpass 8/kdb 1/knfs 1/package_test \
         5/package 8/package 8/rmtsysd 8/aklog_dynamic_auth 8/xfs_size_check \
         1/symlink 1/symlink_list 1/symlink_make 1/symlink_remove; do
    rm -f %{buildroot}%{_mandir}/man$f.*
done

# gzip man pages
gzip -9 %{buildroot}%{_mandir}/man*/*

# rename kpasswd to kapasswd
mv %{buildroot}%{_mandir}/man1/kpasswd.1.gz %{buildroot}%{_mandir}/man1/kapasswd.1.gz
ln -f %{buildroot}%{_mandir}/man1/kapasswd.1.gz %{buildroot}%{_mandir}/man1/kpasswd.openafs.1.gz
mv %{buildroot}%{_mandir}/man1/pagsh.1.gz %{buildroot}%{_mandir}/man1/pagsh.openafs.1.gz

# create list of man pages that go in the 'openafs' package
/bin/ls %{buildroot}%{_mandir}/man1 \
        |egrep '^afs|^fs|^kas|^klog|pagsh|^pts|^restorevol|^rxdebug|scout|^sys|tokens|translate|udebug|unlog|^uss|^vos' \
        |egrep -v '^klog\.krb5|^afs_compile_et' \
        >openafs-man1files

/bin/ls %{buildroot}%{_mandir}/man5 \
        |egrep 'CellServDB|ThisCell|afsmonitor|^butc|^uss' \
        >openafs-man5files

/bin/ls %{buildroot}%{_mandir}/man8 \
        |egrep '^backup|^bos|^butc|^fms|^fstrace|^kas|^uss|^read_tape|^restorevol|^salvageserver|^vsys' \
        >openafs-man8files

#
# move this
#
mv %{buildroot}%{_prefix}/afs/bin/restorevol %{buildroot}%{_bindir}

#
# create filelist
#
grep -v "^#" >openafs-file-list <<EOF-openafs-file-list
%{_bindir}/afsmonitor
%{_bindir}/bos
%{_bindir}/fs
# in openafs-kpasswd
#%{_bindir}/kapasswd
#
#%{_bindir}/kpasswd
%{_bindir}/klog
%{_bindir}/klog.krb
%{_bindir}/pagsh.openafs
%{_bindir}/pagsh.krb
%{_bindir}/pts
%{_bindir}/restorevol
%{_bindir}/scout
%{_bindir}/sys
%{_bindir}/livesys
%{_bindir}/tokens
%{_bindir}/tokens.krb
%{_bindir}/translate_et
%{_bindir}/udebug
%{_bindir}/unlog
%{_sbindir}/backup
%{_sbindir}/butc
#%{_sbindir}/copyauth
%{_sbindir}/fms
%{_sbindir}/fstrace
%{_sbindir}/kas
#%{_sbindir}/kdump
#%{_sbindir}/kseal
%{_sbindir}/read_tape
%{_sbindir}/rxdebug
%{_sbindir}/uss
%{_sbindir}/vos
%{_sbindir}/vsys
EOF-openafs-file-list

# add man pages to the list
cat openafs-man1files \
        | ( while read x; do echo "%%doc %{_mandir}/man1/$x"; done ) \
        >>openafs-file-list
cat openafs-man5files \
        | ( while read x; do echo "%%doc %{_mandir}/man5/$x"; done ) \
        >>openafs-file-list
cat openafs-man8files \
        | ( while read x; do echo "%%doc %{_mandir}/man8/$x"; done ) \
        >>openafs-file-list

#
# Install compatibility links
#
for d in bin:bin etc:sbin; do
  olddir=`echo $d | sed 's/:.*$//'`
  newdir=`echo $d | sed 's/^.*://'`
  mkdir -p %{buildroot}%{_prefix}/afsws/$olddir
  for f in `cat openafs-file-list`; do
    if echo $f | grep -q /$newdir/; then
      fb=`basename $f`
      ln -sf %{_prefix}/$newdir/$fb %{buildroot}%{_prefix}/afsws/$olddir/$fb
    fi
  done
done

#
# Remove files we're not installing
#

# remove duplicated files from /usr/afs/bin
for f in bos fs kas klog klog.krb pts tokens tokens.krb udebug vos; do
  rm -f %{buildroot}%{_prefix}/afs/bin/$f
done

# compile_et is duplicated in e2fsprogs
# the rest are not needed.
for f in compile_et dlog dpass install knfs; do
  rm -f %{buildroot}%{_bindir}/$f
done

# put these into the debug package instead
for f in %{buildroot}%{_bindir}/xstat_*_test; do
    mv $f %{buildroot}%{_prefix}/afs/debug
done

# Remove empty files from the krb5 migration
for f in afs2k5db fakeka kpwvalid; do
  rm -f %{buildroot}%{_sbindir}/$f
done

# not supported on Linux or duplicated
for f in kdb rmtsysd ; do
  rm -f %{buildroot}%{_sbindir}/$f
done

rm -f %{buildroot}%{_sbindir}/kdump-*

# PAM modules are doubly-installed  Remove the version we don't need
for f in pam_afs.krb.so.1 pam_afs.so.1 ; do
  rm -f %{buildroot}%{_libdir}/$f
done

#??????? /usr/include/des_prototypes.h

%endif
#build_userspace

%if %{build_modules} || %{build_kmod}

mkdir -p -m 755 %{buildroot}%{kmoddst}
# Mark kernel modules as executable; otherwise they won't get stripped 
# by /usr/lib/rpm/brp-strip
install -m 744 ${sysname}/dest/root.client/%{kmoddir}/openafs.ko %{buildroot}%{kmoddst}

# Sign the module ?
%if %{?_with_modsign:1}%{!?_with_modsign:0}
# If the module signing keys are not defined, define them here.
%{!?privkey: %define privkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.priv}
%{!?pubkey: %define pubkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.der}
%define __modsign_install_post \
  %{__perl} %{ksrcdir}/scripts/sign-file -v sha256 %{privkey} %{pubkey} %{buildroot}%{kmoddst}/openafs.ko \
%{nil}
# Redefine __spec_install_post
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}} \
  %{__arch_install_post} \
  %{__os_install_post} \
  %{__modsign_install_post} \
%{nil}
%endif
#modsign

%endif
#build_modules

%clean
rm -f openafs-file-list openafs-man*files
[ "%{buildroot}" != "/" -a "x%{debugspec}" != "x1" ] && \
    rm -fr %{buildroot}

###############################################################################
###
### scripts
###
###############################################################################
%if %{build_userspace}

%post -n openafs%{?nsfx}-client
%if %SL5 || %SL6
chkconfig --list afs > /dev/null 2>&1 || {
    /%{sbin}/chkconfig --add afs
    /%{sbin}/chkconfig --level 345 afs off
}
%else
#systemd_post afs.service breaks other macros for some reason
if [ $1 -eq 1 ] ; then 
        # Initial installation 
        /usr/bin/systemctl preset afs.service >/dev/null 2>&1 || : 
fi 
%endif
[ -d /afs ] || {
    mkdir /afs
    chown root.root /afs
    chmod 0755 /afs
    chcon -u system_u -r object_r -t mnt_t /afs
}
:

%preun -n openafs%{?nsfx}-client
[ $1 -eq 0 ] || exit 0
%if %SL5 || %SL6
/%{sbin}/service afs stop
/%{sbin}/chkconfig --del afs
%else
#systemd_preun afs.service makes other macros break for some reason
if [ $1 -eq 0 ] ; then 
        # Package removal, not upgrade 
        /usr/bin/systemctl --no-reload disable afs.service > /dev/null 2>&1 || : 
        /usr/bin/systemctl stop afs.service > /dev/null 2>&1 || : 
fi 
%endif
[ -d /afs ] && rmdir /afs
:

%if %SL7
%postun -n openafs%{?nsfx}-client
#systemd_postun
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || : 
:
%endif


%post -n openafs%{?nsfx}-server
%if %SL5 || %SL6
chkconfig --list afs-server > /dev/null 2>&1 || {
    /%{sbin}/chkconfig --add afs-server
    /%{sbin}/chkconfig --level 345 afs-server off
}
%else
#systemd_post afs-server.service
if [ $1 -eq 1 ] ; then 
        # Initial installation 
        /usr/bin/systemctl preset afs-server.service >/dev/null 2>&1 || : 
fi 
%endif
%if %SL5
[ -x /usr/sbin/selinuxenabled ] && /usr/sbin/selinuxenabled && \
   /usr/bin/chcon system_u:object_r:unconfined_exec_t %{initdir}/afs-server || :
%else
[ -x /usr/sbin/selinuxenabled ] && /usr/sbin/selinuxenabled && \
   /usr/bin/chcon -u system_u -r object_r -t unconfined_exec_t %{initdir}/afs-server || :
%endif
:

%preun -n openafs%{?nsfx}-server
[ $1 -eq 0 ] || exit 0
%if %SL5 || %SL6
/%{sbin}/service afs-server stop
/%{sbin}/chkconfig --del afs-server
%else
#systemd_preun afs-server.service
if [ $1 -eq 0 ] ; then 
        # Package removal, not upgrade 
        /usr/bin/systemctl --no-reload disable afs-server.service > /dev/null 2>&1 || : 
        /usr/bin/systemctl stop afs-server.service > /dev/null 2>&1 || : 
fi 
%endif
:

%if %SL7
%postun -n openafs%{?nsfx}-server
#systemd_postun
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || : 
:
%endif

%post -n openafs%{?nsfx}-authlibs
[ $1 = 1 ] || exit 0
/%{sbin}/ldconfig >/dev/null 2>&1 || :

%postun -n openafs%{?nsfx}-authlibs
/%{sbin}/ldconfig >/dev/null 2>&1 || :

%endif
#build_userspace

%if %{build_modules}

%post -n kernel-module-openafs%{?nsfx}-%{kernel}
depmod -ae %{unamer} >/dev/null 2>&1 || :

%endif
#build_modules

###############################################################################
###
### file lists
###
###############################################################################
%if %{build_userspace}
%files -n openafs%{?nsfx} -f openafs-file-list
%defattr(-,root,root,-)
%config(noreplace) /etc/sysconfig/afs
%doc src/LICENSE
%doc doc/pdf
%doc doc/protocol/rfc5864.txt
%doc doc/arch
%doc doc/examples
%doc ChangeLog
%doc RELNOTES-%{srcvers}

%doc %{_mandir}/man1/livesys.1.gz
%doc %{_mandir}/man5/afs.5.gz

%files -n openafs%{?nsfx}-client
%defattr(-,root,root,-)
%ghost %dir /afs
%dir %{_prefix}/vice
%dir %{_prefix}/vice/etc
%config %{_prefix}/vice/etc/CellServDB
%config(noreplace) %{_prefix}/vice/etc/CellAlias
%config(noreplace) %{_prefix}/vice/etc/ThisCell
%config(noreplace) %{_prefix}/vice/etc/cacheinfo
%{_bindir}/cmdebug
%{_bindir}/up
%{_bindir}/afsio
%{_prefix}/vice/etc/afsd*
%{_prefix}/vice/etc/killafs
%{pamdir}/pam_afs.krb.so.1
%{pamdir}/pam_afs.krb.so
%{pamdir}/pam_afs.so.1
%{pamdir}/pam_afs.so
%dir %{defcachedir}
%doc %{_mandir}/man1/cmdebug.1.gz
%doc %{_mandir}/man1/up.1.gz
%doc %{_mandir}/man5/CellAlias.5.gz
%doc %{_mandir}/man5/afs_cache.5.gz
%doc %{_mandir}/man5/cacheinfo.5.gz
%doc %{_mandir}/man8/afsd.8.gz
%{initdir}/afs
%if %SL7
%{_unitdir}/afs.service
%{_presetdir}/70-afs.preset
/etc/sysconfig/.afs.generated
%endif

%files -n openafs%{?nsfx}-server
%defattr(-,root,root,-)
%dir %{_prefix}/afs
%dir %{_prefix}/afs/bin
%dir %{_prefix}/afs/logs
%dir %{_prefix}/afs/etc
%{_prefix}/afs/bin/bosserver
%{_prefix}/afs/bin/bos_util
%{_prefix}/afs/bin/buserver
%{_prefix}/afs/bin/fileserver
%{_prefix}/afs/bin/ka-forwarder
# Should we support KAServer?
%{_prefix}/afs/bin/kaserver
%{_prefix}/afs/bin/kpwvalid
%{_prefix}/afs/bin/pt_util
%{_prefix}/afs/bin/ptserver
%{_prefix}/afs/bin/salvager
%{_prefix}/afs/bin/upclient
%{_prefix}/afs/bin/upserver
%{_prefix}/afs/bin/vlserver
%{_prefix}/afs/bin/volinfo
%{_prefix}/afs/bin/volscan
%{_prefix}/afs/bin/volserver
%{_sbindir}/kadb_check
%{_sbindir}/prdb_check
%{_sbindir}/vldb_check
%{_sbindir}/vldb_convert
%{_sbindir}/voldump
%doc %{_mandir}/man5/AuthLog.5.gz
%doc %{_mandir}/man5/AuthLog.dir.5.gz
%doc %{_mandir}/man5/BackupLog.5.gz
%doc %{_mandir}/man5/BosConfig.5.gz
%doc %{_mandir}/man5/BosLog.5.gz
%doc %{_mandir}/man5/FORCESALVAGE.5.gz
%doc %{_mandir}/man5/FileLog.5.gz
%doc %{_mandir}/man5/KeyFile.5.gz
%doc %{_mandir}/man5/NetInfo.5.gz
%doc %{_mandir}/man5/NetRestrict.5.gz
%doc %{_mandir}/man5/NoAuth.5.gz
%doc %{_mandir}/man5/SALVAGE.fs.5.gz
%doc %{_mandir}/man5/SalvageLog.5.gz
%doc %{_mandir}/man5/UserList.5.gz
%doc %{_mandir}/man5/VLLog.5.gz
%doc %{_mandir}/man5/VolserLog.5.gz
%doc %{_mandir}/man5/afs_volume_header.5.gz
%doc %{_mandir}/man5/bdb.DB0.5.gz
%doc %{_mandir}/man5/fms.log.5.gz
%doc %{_mandir}/man5/kaserver.DB0.5.gz
%doc %{_mandir}/man5/kaserverauxdb.5.gz
%doc %{_mandir}/man5/krb.conf.5.gz
%doc %{_mandir}/man5/prdb.DB0.5.gz
%doc %{_mandir}/man5/salvage.lock.5.gz
%doc %{_mandir}/man5/sysid.5.gz
%doc %{_mandir}/man5/tapeconfig.5.gz
%doc %{_mandir}/man5/vldb.DB0.5.gz
#{_mandir}/man8/backup*.8.gz
#{_mandir}/man8/bosserver.8.gz
%doc %{_mandir}/man8/buserver.8.gz
#{_mandir}/man8/butc.8.gz
%doc %{_mandir}/man8/fileserver.8.gz
%doc %{_mandir}/man8/ka-forwarder.8.gz
%doc %{_mandir}/man8/kadb_check.8.gz
#{_mandir}/man8/fms.8.gz
%doc %{_mandir}/man8/prdb_check.8.gz
%doc %{_mandir}/man8/ptserver.8.gz
%doc %{_mandir}/man8/state_analyzer.8.gz
%doc %{_mandir}/man8/pt_util.8.gz
%doc %{_mandir}/man8/vldb_check.8.gz
%doc %{_mandir}/man8/vldb_convert.8.gz
%doc %{_mandir}/man8/vlserver.8.gz
%doc %{_mandir}/man8/voldump.8.gz
%doc %{_mandir}/man8/volinfo.8.gz
%doc %{_mandir}/man8/volscan.8.gz
%doc %{_mandir}/man8/volserver.8.gz
%doc %{_mandir}/man8/salvager.8.gz
%doc %{_mandir}/man8/upclient.8.gz
%doc %{_mandir}/man8/upserver.8.gz
%{initdir}/afs-server
%if %SL7
%{_unitdir}/afs-server.service
%{_presetdir}/70-afs-server.preset
/etc/sysconfig/.afs-server.generated
%endif
# DAFS
%{_prefix}/afs/bin/dafileserver
%{_prefix}/afs/bin/dasalvager
%{_prefix}/afs/bin/davolserver
%{_prefix}/afs/bin/salvageserver
%{_prefix}/afs/bin/salvsync-debug
%doc %{_mandir}/man8/dafileserver.8.gz
%doc %{_mandir}/man8/dasalvager.8.gz
%doc %{_mandir}/man8/davolserver.8.gz
# new with 1.5.76:
%doc %{_mandir}/man5/krb.excl.5.gz

%files -n openafs%{?nsfx}-authlibs
%defattr(-,root,root,-)
%{_libdir}/libafsauthent.so.*
%{_libdir}/libafsrpc.so.*
%{_libdir}/libkopenafs.so.1
%{_libdir}/libkopenafs.so.1.1

%files -n openafs%{?nsfx}-authlibs-devel
%defattr(-,root,root,-)
%{_includedir}/kopenafs.h
%{_libdir}/libafsauthent.so
%{_libdir}/libafsauthent.a
%{_libdir}/libafsauthent_pic.a
%{_libdir}/libafsrpc.a
%{_libdir}/libafsrpc.so
%{_libdir}/libafsrpc_pic.a
%{_libdir}/libkopenafs.a
%{_libdir}/libkopenafs.so

%files -n openafs%{?nsfx}-devel
%defattr(-,root,root,-)
%{_bindir}/afs_compile_et
%{_bindir}/rxgen
%{_includedir}/afs
%{_includedir}/des.h
%{_includedir}/des_conf.h
%{_includedir}/des_odd.h
%{_includedir}/des_prototypes.h
%{_includedir}/lock.h
%{_includedir}/lwp.h
%{_includedir}/mit-cpyright.h
%{_includedir}/preempt.h
%{_includedir}/rx
%{_includedir}/timer.h
%{_includedir}/ubik.h
%{_includedir}/ubik_int.h
%{_libdir}/afs
%{_libdir}/libafscp.a
%{_libdir}/libdes.a
%{_libdir}/liblwp.a
%{_libdir}/librx.a
%{_libdir}/librxkad.a
%{_libdir}/librxstat.a
%{_libdir}/libubik.a
%doc %{_mandir}/man1/afs_compile_et.1.gz
%doc %{_mandir}/man1/rxgen.1.gz

%files -n openafs%{?nsfx}-kernel-source
%defattr(-,root,root,-)
%{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.IBM
%{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.Sun
%{_prefix}/src/openafs-kernel-%{afsvers}/README
%{_prefix}/src/openafs-kernel-%{afsvers}/src

%files -n openafs%{?nsfx}-compat
%defattr(-,root,root,-)
%{_prefix}/afsws

%files -n openafs%{?nsfx}-kpasswd
%defattr(-,root,root,-)
%{_bindir}/kapasswd
%{_bindir}/kpasswd.openafs
%{_bindir}/kpwvalid
%doc %{_mandir}/man1/kapasswd.1.gz
%doc %{_mandir}/man1/kpasswd.openafs.*
%doc %{_mandir}/man8/kpwvalid.8.gz

%if %{krb5support}
%files -n openafs%{?nsfx}-krb5
%defattr(-,root,root,-)
%{_bindir}/aklog
%{_bindir}/klog.krb5
%{_bindir}/k5log
%{_sbindir}/asetkey
%doc %{_mandir}/man1/aklog.1.gz
%doc %{_mandir}/man1/klog.krb5.1.gz
%doc %{_mandir}/man1/k5log.1.gz
%doc %{_mandir}/man8/asetkey.8.gz
%endif

%files -n openafs%{?nsfx}-module-tools
%defattr(-,root,root,-)
/%{sbin}/openafs-modules

%files -n openafs%{?nsfx}-plumbing-tools
%defattr(-,root,root,-)
%{_prefix}/afs/debug
%{_prefix}/afs/bin/dafssync-debug
%{_prefix}/afs/bin/fssync-debug
%{_prefix}/afs/bin/state_analyzer
%{_prefix}/vice/etc/C
%doc %{_mandir}/man1/xstat_cm_test.1.gz
%doc %{_mandir}/man1/xstat_fs_test.1.gz
%doc %{_mandir}/man5/afszcm.cat.5.gz
%doc %{_mandir}/man8/fssync-debug.8.gz
%doc %{_mandir}/man8/fssync-debug_attach.8.gz
%doc %{_mandir}/man8/fssync-debug_callback.8.gz
%doc %{_mandir}/man8/fssync-debug_detach.8.gz
%doc %{_mandir}/man8/fssync-debug_error.8.gz
%doc %{_mandir}/man8/fssync-debug_header.8.gz
%doc %{_mandir}/man8/fssync-debug_leaveoff.8.gz
%doc %{_mandir}/man8/fssync-debug_list.8.gz
%doc %{_mandir}/man8/fssync-debug_mode.8.gz
%doc %{_mandir}/man8/fssync-debug_move.8.gz
%doc %{_mandir}/man8/fssync-debug_offline.8.gz
%doc %{_mandir}/man8/fssync-debug_online.8.gz
%doc %{_mandir}/man8/fssync-debug_query.8.gz
%doc %{_mandir}/man8/fssync-debug_stats.8.gz
%doc %{_mandir}/man8/fssync-debug_vgcadd.8.gz
%doc %{_mandir}/man8/fssync-debug_vgcdel.8.gz
%doc %{_mandir}/man8/fssync-debug_vgcquery.8.gz
%doc %{_mandir}/man8/fssync-debug_vgcscan.8.gz
%doc %{_mandir}/man8/fssync-debug_vgcscanall.8.gz
%doc %{_mandir}/man8/fssync-debug_vnode.8.gz
%doc %{_mandir}/man8/fssync-debug_volop.8.gz
%endif
#build_userspace

%if %{build_modules}
%files -n kernel-module-openafs%{?nsfx}-%{kernel}
%defattr(-,root,root,-)
%dir %attr(755,root,root) %{kmoddst}
%attr(644,root,root) %{kmoddst}/openafs.ko
%endif

###############################################################################
###
### openafs.spec change log
###
###############################################################################

%changelog
* Wed Dec   8 2016 Stephan Wiesand <stephan wiesand desy de> 1.6.20-256.SLx
- update to security release 1.6.20
- added RemainAfterExit=true in afs.service, to fix the case where only
  kernel threads remain after the client has started

* Fri Nov 11 2016 Stephan Wiesand <stephan wiesand desy de> 1.6.19-253.SLx
- update to release 1.6.19

* Fri Apr 29 2016 Stephan Wiesand <stephan wiesand desy de> 1.6.18-239.SLx
- update to release 1.6.18

* Wed Mar  2 2016 Stephan Wiesand <stephan wiesand desy de> 1.6.17-234.SLx
- update to release 1.6.17 (security release)
- install service unit files with mode 644, not 755 (rt.central.org #132662)

* Mon Dec 28 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.16-230.SLx
- update to release 1.6.16

* Fri Nov 20 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.16-226.SLx
- update to prerelease 1.6.16pre1

* Thu Oct 29 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.15-221.SLx
- update to release 1.6.15 (security release)
- addresses OPENAFS-SA-2015-007 (CVE-2015-7762, CVE-2015-7763)

* Thu Aug 13 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.14-218.SLx
- update to release 1.6.14
- fixes a 1.6.13 regression in vlserver when volumes are queried by regex
- the "backup" util does this, unless vols are specified with ".*" or "" only

* Mon Jul 27 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.13-215.SLx
- update to release 1.6.13 (security release)

* Mon Mar 30 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.11-205.SLx
- fixed dependency of the -kpasswd subpackage (spotted by Pat Riehecky)
- fixed on_network test to work on EL7 in server rc file too (reported by
  Otto-Michael Braun)
- fixed unsatisfied dependencies on shared libs from -authlib-devel by turning
  AutoReq off for that package (reported by Ben Meekhof)

* Fri Mar  6 2015 Stephan Wiesand <stephan wiesand desy de> 1.6.11-204.SLx
- update to release 1.6.11
- patch 1084 should no longer be needed (should...)
- patch 1085 is included in 1.6.11
- added "Provides: openafs-sl-client = %%{version}" as requested by Pat

* Mon Oct 20 2014 Stephan Wiesand <stephan wiesand desy de> 1.6.10-153.SLx
- update to release 1.6.10
- patch 1084 to revert gerrit 11358
- patch 1085 with aklog/krb524 fix from gerrit 11538
- package the new volscan executable + manpage, in -server
- do not package the xfs_size_check manpage
- removed the old lwp versions of butc, fileserver, volserver
- support for SL7
-  support "--with modsign" to sign the kernel module
-  ship systemd unit files on this platform, rather than init scripts
-  the old init scripts are called in "prepare" mode from the unit files
-  in this mode, they do the usual checks/autoconfig, ...
-  and then they write the environment files used in the unit files
- added BOSSERVER_OPTIONS variable to sysconfig (and server startup files)
- added ENABLE_DYNROOT_SPARSE to sysconfig (and client init script)
-  defaults to on on SL7, off on SL5/6
- patches 1080..83 are already in
- use the right path to depmod, and generally the right sbin

* Fri Apr 11 2014 Stephan Wiesand <stephan wiesand desy de> 1.6.5.1-149.SLx
- modify kmods to clean up links when updating to build against other kernel

* Thu Apr  3 2014 Stephan Wiesand <stephan wiesand desy de> 1.6.5.1-148.SLx
- patches 1081/2/3 with security content from openafs-1.6.7

* Fri Dec 13 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.5.1-147.SLx
- patch1080 with http://gerrit.openafs.org/10578 to fix RHBZ #1038315 on EL 6.5
- fix build on EL 5.10

* Mon Nov 25 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.5.1-146.SLx
- 1.6.5.1 bugfix release
- modify buildroot to use mktemp, allowing simultaneous builds (Pat)
- fix the AFS mountpoint in the cacheinfo file generated in the SPEC

* Wed Jul 24 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-145.SLx
- 1.6.5 security release addressing openafs-sa-2013-0003 and -0004
- see SECURITY.txt for important info on how to actually secure your site
- just updating to this build is *not* sufficient

* Tue Feb 26 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.144.SLx
- do some more work in modules script
- print debug output from kmod scripts if variable "verbose" is set

* Tue Feb 26 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.143.SLx
- several fixes in modules script; does less unnecessary work

* Mon Feb 25 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.142.SLx
- fixed location of modules script

* Sun Feb 24 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.141.SLx
- (untested, unfinished)
- use our own script for dealing with "weak updates", don't patch weak-modules
- use different paths, don't interfere with weak-modules
- new subpackage for the script: module-tools (license), require from kmods
- script is run from scripts and triggers in the kmods
- no longer provide kabi-mods
- added a purgecache action to the client init script (Pat Riehecky)

* Fri Feb 22 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.140.SLx
- the corrected actual, still "inofficial" 1.6.2 release

* Wed Feb 13 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.139.SLx
- the actual, still "inofficial" 1.6.2 release

* Fri Feb  1 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.138.1.pre4.SLx
- the actual pre4, downloaded from grand.central.org, + bos.patch
- adapted client init script to changed ifconfig output on F18 (->EL7)

* Wed Jan 30 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.137.1.pre4.SLx
- update to current head of 1.6.x (a15c406) + gerrit 9895, 8750 + bos patch
- updated CellServDB to latest from grand.central.org (Jan 28, 2013)

* Fri Jan 25 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.136.1.pre4.SLx
- pseudo pre4 - has gerrit 8912, 8937, 8940, 8939, 8945, + bos.patch
- this could be 1.6.2 final
- require /sbin/modprobe, not modutils (SL7/FC18)
* Sun Jan 13 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.135.1.pre3.SLx
- made it build and install on SL7 (and recognize F18 as that)
* Sat Jan 12 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.134.1.pre3.SLx
- added bos.patch
* Thu Jan 10 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.134.pre3.SLx
- this is the actual pre3 uploaded to grand.central.org
- and downloaded from there to another system

* Thu Jan 10 2013 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.133.pre3.SLx
- current head of 1_6_x (fa0c841d) + changes in the pipeline:
- 8866..7, 8869, 8872, 8889..90, 8896..97
- + "make pre3" not yet on gerrit

* Mon Dec 24 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.132.pre2.SLx
- this is the actual pre2 as uploaded to grand.central.org

* Fri Dec 21 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.131.pre2.SLx
- current head of 1_6_x (5cfb720) + changes in the pipeline:
- 8775..6, 8791, 8795..6, 8798, 8804..5, 8799..800, 8808..11
- + "make pre2" not yet on gerrit
- renamed kmod packages from openafs_... to openafs-...
- removed unused patches
- client init script changes to make updates from 1.4 smoother:
- on start, check for the libafs module as well, bail out if loaded
- on stop, check for a loaded libafs module, remove it if loaded

* Thu Dec 20 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.129.pre2.SLx
- pre1 + changes in the pipeline:
- 8775/6, 8785, 8779/80/81, 8786..91, 8795, 8796

* Mon Dec 17 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.128.pre2.SLx
- pre1 + EL5 build fixes (f87d49c/8021, 74c1881/8019, 5daa08e/8006)

* Sat Dec 15 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.127.pre2.SLx
- pre1 + changes foreseen for pre2 (8753, 8757, 8758, 8761)

* Thu Dec 13 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.126.pre1.SLx
- build kmod packages for each minor SL release kernel series
- patch weak-modules so it won't link our modules across minor release kernels
- use the doc macro to package documentation files
- added several files from the doc tarball to documentation files
- mark manpages as documentation files

* Tue Dec 11 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.124.pre1.SLx
- these are the tarballs uploaded to grand.central.org, still w/o tag
- add a sanity check for the module to load in the client init script

* Mon Dec 10 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.123.pre1.SLx
- first, still "inofficial" pre1

* Mon Dec 10 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.122.pre0.SLx
- build and package rxperf and th_rxperf

* Mon Dec 10 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.120.pre0.SLx
- latest pre1 candidate: current head (fb95823) + gerrit 8421, 8423 (rxperf stuff)

* Fri Dec  7 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.119.pre0.SLx
- latest pre1 candidate: current head (75af57b) + gerrit 8609, 8563, 8564, 8715

* Thu Dec  6 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.118.pre0.SLx
- includes the latest patch sets for gerrit 8548, 8604, 8605, 8696, 8608
- also includes cherry-picked 8617 from master, supposed to fix cache-bypass

* Thu Dec  6 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.117.pre0.SLx
- this one is just the current HEAD of openafs-stable_1_6_x (e1baf1af4)

* Thu Dec  6 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.116.pre0.SLx
- next 1.6.2 prerelease lookalike
- needs patch1078 to fix gerrit 8608/1 which is currently broken

* Sun Dec  2 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.2-0.114.pre0.SLx
- 1st attempt to build a 1.6.2 prerelease lookalike
- needs patch1077 beacuse erroneously version one of gerrit 8549 was applied

* Sun Apr  1 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.1-112.SLx
- update to 1.6.1 stable release, no patches

* Mon Mar  5 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.1-110.pre4.SLx
- update to prerelease 4

* Mon Feb 27 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.1-109.pre3.SLx
- update to prerelease 3 (-100..-108 were builds with debug patches)

* Thu Jan 26 2012 Stephan Wiesand <stephan wiesand desy de> 1.6.1-99.pre2.SLx
- update to prerelease 2
- no changelog, no release notes

* Sat Dec 17 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.1-98.pre1.SLx
- update to prerelease 1 for 1.6.1 release
- there are no release notes yet
- package new library libafscp.a in -devel
- the old patch 302 (afsdump_scan) is finally upstream

* Tue Aug 16 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-97.SLx
- update to final 1.6 release
- updated CellServDB to latest from grand.central.org (Aug 14, 2011)

* Mon Aug  8 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-96.pre7.SLx
- update to next prerelease, last patch is already in

* Thu Jun 23 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-95.pre6.SLx
- patch1076: attempt an RX fix (backport of http://gerrit.openafs.org/4837)

* Mon Jun  6 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-94.pre6.SLx
- update to next prerelease (pre5 had a serious bug and was not released)

* Fri Apr  1 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-93.pre4.SLx
- update to next prerelease

* Wed Mar 23 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-92.pre3.SLx
- update to next prerelease
- init scripts: fixed condrestart

* Wed Feb 16 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-91.pre2.SLx
- update to next prerelease
- package /afs as ghost, and create it in post again - and fix the label

* Wed Jan 19 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-90.pre1.SLx
- let openafs-client own the /afs mountpoint to avoid selinux troubles
- change initdir macro to /etc/rc.d/init.d (like upstream), and use it everywhere

* Wed Jan  5 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0-89.pre1.SLx
- fix version/release for prerelease to allow updating to final later

* Sun Jan  2 2011 Stephan Wiesand <stephan wiesand desy de> 1.6.0pre1-88.SLx
- update to first 1.6 prerelease

* Wed Dec 22 2010 Troy Dawson <dawson@fnal.gov> 1.5.78-87.SLx
- added i386 case version for sysname incase arch shows i386 despite a target=i686

* Mon Dec 20 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.78-86.SLx
- don't strip any binaries, let rpm do the job
- new in openafs-debug: cacheout, afscp, fsx
- new in openafs-client: afsio
- moved into main package: restorevol
- moved into openafs-server: ka-forwarder + manpage
- server package should own /usr/afs/etc
- moved into openafs-authlibs: libkopenafs.so.1[.1]
- moved into openafs-authlibs-devel: libkopenafs.{a,so}, kopenafs.h, libafs{authent,rpc}.a 
- fixed chcon in server's post script for SL6
- introduced the ability to build a kabi-tracking kmod (define build_kmod 1)
- introduced a switch to disable building the fuse client
- and unless that switch is used, buildrequire fuse-devel and package afsd.fuse
- other minor changes to make rpmlint less unhappy
- renamed openafs-debug to openafs-plumbing-tools
- moved fssync-debug and manpages into -plumbing-tools
- enabled debugsyms by default again, no effect on kernel module

* Tue Dec 14 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.78-84.SLx
- removed support for SL3/4, greatly simplifying the spec
- removed support for ia32e, ia64, athlon, ...
- removed all old patches and obsolete sources (like openafs-krb5.tar.gz)
- relaxed requirements between userland and kernel-module package
- updated Changelog & Relnotes, and made sure we do so in the future
- don't package the afs_compile_et manpage in the main packages as well
- don't add -fPIC to CFLAGS (be compatible with openafs.org spec)
- configure: no --enable-debug[-kernel] by default (be compatible with openafs.org spec)
- configure: added --disable-strip-binaries (be compatible with openafs.org spec)
- configure: added --with-linux-kernel-packaging (be compatible with openafs.org spec)
- this also renames the module to openafs.ko, so change in rc script
- configure: added --disable-kernel-module to non-module builds
- and moved the build requirement on kernel-devel to the module package
- the server package shouldn't require the kernel module
- debugspec can now be defined on the command line, and defaults to 0
- moved much of the kernel/kvers/****dir voodoo into openafs-sl-defs.sh
- which also replaces openas-lslrelease-helper.sh (and no longer stes SL5 on SL6)
- updated CellServDB to latest from grand.central.org (Dec 13, 2010)

* Fri Nov 12 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.78-83.SLx
- update to latest feature release
- enable dugging symbols by default
- there is no more /usr/include/potpourri.h
- module is called ...mp.ko again?

* Fri Oct 22 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.77-82.SLx
- update to latest feature release

* Thu Aug 19 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.76-81.SLx
- update to latest feature release
- patch1075 should no longer be required
- libkopenafs is now 1.1
- DAFS is built by default - added files to openafs-server
- added the new krb.excl(5) manpage to openafs-server

* Fri Apr 30 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.74-80.z2.SLx
- make this work with kernel releases prefixed with ".z[0-9]"

* Fri Apr 30 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.74-80.z1.SLx
- more SL6 changes:
- use afsvers macro instead of PACKAGE_VERSION which is no longer available
- patch1075 to fix kernel panic on module load
- and: buildrequire make...

* Wed Apr 28 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.74-79.SLx
- 1.5.74 release
- F10 -> SL6
- changed how to determine the domain (hostname -d/-f may not work)
- restorevol moved from sbin to bin

* Sun Jan 24 2010 Stephan Wiesand <stephan wiesand desy de> 1.5.69-78.z0.SLx
- first stab at 1.5

* Sun Jan 24 2010 Stephan Wiesand <stephan wiesand desy de> 1.4.12-77.pre1.z2.SLx
- patch1074 test fix, backed out 1073 for now

* Sat Jan 23 2010 Stephan Wiesand <stephan wiesand desy de> 1.4.12-77.pre1.z1.SLx
- patch1073 test fix

* Sun Jan 17 2010 Stephan Wiesand <stephan wiesand desy de> 1.4.12-77.pre1.SLx
- prerelease 1 for next upstream release
- patches 1065..1069 are already in
- added patches since prerelease from stable-1_4_x git branch
- updated CellServDB from grand.central.org (dementia.org entry changed)
- changed CellservDB entry for phy.bris.ac.uk (mail from Winnie Lasseco)
- package afs_compile_et + manpage (in -devel)

* Tue Nov 17 2009 Stephan Wiesand <stephan wiesand desy de> 1.4.11-76.1.SLx
- handle current lustre kernels (packaged a bit more like EL5)

* Sun Sep 20 2009 Stephan Wiesand <stephan wiesand desy de> 1.4.11-76.SLx
- added more post-1.4.11 fixes from stable-1_4_x git branch:
  1068: fix-linux24-builds-20090718
  1069: kernel-init-vrequest-structure-20090914

* Fri Jul 31 2009 Stephan Wiesand <stephan wiesand desy de> 1.4.11-75.SLx
- upstream release 1.4.11
- updated CellServDB from grand.central.org
- install release notes and changelog into /usr/share/doc/openafs-<version>
- explicitly build src/auth/setkey (for -debug package)
- do not install the new compile_et manpage, it clashes with e2fsprogs-devel
- do not install the new rmtsysd manpage, this doesn't exist for linux yet
- copyauth is no longer built; delete the manpage as well
- package new manpages for restorevol, vsys
- added post-1.4.11 fixes from stable-1_4_x git branch:
  1066: export-ktc-curpag-everywhere-20090713
  1067: fix-getvolume-for-nonroot-dynroot-fids-20090722

* Tue Apr 07 2009 Stephan Wiesand <stephan wiesand desy de> 1.4.10-74.SLx
- upstream release 1.4.10
- removed patches 1062..65
- updated CellServDB from grand.central.org; remove wallace from RAL entry

* Wed Dec 24 2008 Stephan Wiesand <stephan wiesand desy de> 1.4.8-73.SLx
- make this fit for F10

* Fri Nov 21 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.8-71.SLx
- upstream release 1.4.8
- post release patches:
  1062: viced-helper-thread-count-20081111 (1-liner to stay within 128 threads)
  1063..65: fileserver man page updates

* Sun Oct 26 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.8-0.70.pre3.SLx
- prerelease 3
- package a link for k5log.1.gz, and package both in openafs-krb5 not openafs

* Wed Oct 08 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.8-0.69.pre2.SLx
- simply prerelease 2

* Fri Oct 03 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.8-0.69.pre1.SLx
- patches 1058..1061 are in pre1
- package new manpages for krb.conf and vldb_convert (in -server)
- upstream now installs the K5 klog as klog.krb5; package, + a symlink to k5log
- should no longer need 1057

* Sun Jun 01 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.7-68.SLx
- replace 1056 by 1057: linux-hlist-unhashed-opencoding-20080520
- more post-1.4.7 patches (either trivial, or serious and simple):
  1058: butc-xbsa-lwp-protoize-damage-20080501
  1059: uuid-corrected-duplicate-check-20080501
  1060: viced-large-more-threads-20080506
  1061: vos-sync-flag-voltype-properly-20080521

* Thu May 15 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.7-67.SLx
- 1.4.7 release
- should not require patch 1056 - but still does :-(

* Fri Apr 11 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.7-0.65.pre3.SLx
- 1056: kernel 2.4 has no hlist_unhashed/insert_inode_hash

* Tue Apr 08 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.7-0.63.pre3.SLx
- next prerelease
- patches 1052..1054 are in pre3

* Tue Apr 08 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.7-0.62.pre2.SLx
- actually apply 1052..1054, stupid

* Mon Apr 07 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.7-0.61.pre2.SLx
- first stab at 1.4.7 prerelease
- had to change twiddle patch (301 -> 303) (one of two typos is now fixed)
- 1051 is already in now
- parallel make is hopelessly broken now; remove retry kludges and don't try
- remove useless symlink manpages
- package the new read_tape manpage
- temp. patches from cvs (should be in pre3):
  1052: linux-flush-unlock-20080402
  1053: linux-flush-compare-20080402
  1054: vlserver-checksignal-returns-voidstar-20080401

* Fri Mar 07 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.6-60.SLx
- when building for lustre kernels, fetch Module.symvers

* Fri Feb 29 2008 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.6-59.SLx
- fix build requirement for lustre case

* Sun Dec 23 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.6-58.SLx
- new upstream release; fixes fileserver bugs (OPENAFS-SA-2007-003, DOS)
- this obsoletes patches 1052,54,55;
- also removed linux-nsec-timestamp-zero (1053) for the time being
- renamed klog.krb5 to k5log
- => this is a build of pristine openafs-1.4.6, except for the extra k5log
- largefile-fileserver is the default since 1.4.5 -> adapt configure options
- added "--with debugsyms" build option

* Thu Nov 15 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.5-56.SLx
- first patches from cvs
  1051: krb5-klog-20071101
  1052: cbd-use-callback-size-for-callbacks-20071105
  1053: linux-nsec-timestamp-zero-20071106
  1054: viced-missing-lock-20071109
  1055: viced-accurately-track-file-callbacks-20071112
- krb5 capable klog packaged as klog.krb5 in openafs-krb5

* Sat Nov 03 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.5-55.SLx
- upstream release 1.4.5
- backout patch 1050, it's not working right => unmodified release

* Tue Oct 23 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.5-0.54.pre4.SLx
- prerelease 4
- fix missing percent sign in  is_lustre macro

* Sat Oct 20 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.5-0.53.pre3.SLx
- prerelease 3 of next upstream version, obsoletes patches 1018..1049
- new patch 1050: oldfs-2gb (see RT #73720, but this one also works on amd64)
- new man pages for CellAlias and pt_util
- there is no more kseal executable
- ka-forwarder now comes with upstream, and with a man page
- => we no longer need afs-krb5 at all; this also obsoletes patches 103, 104, 204
- removed unused SuidCells
- use man-pages from release, meanwhile they are better than those from #19268
- make sure man pages are packaged once only
- support for building against lustre-kernel-source on SL4/5

* Tue Sep 18 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-52.SLx
- more patches from CVS:
  1044: viced-assert-less-20070719
  1045: viced-multi-probe-addr-20070808
  1046: find-dcache-just-hold-the-lock-slightly-longer-20070820
  1047: linux-modparam-269-updates-20070821
  1048: linux-module-error-handling-20070821-modified
  1049: viced-remove-asserts-20070821

* Mon Jul 23 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-51.SLx
- SL5: actually add the improved init script...
- more patches from CVS:
  1037: bucoord-dump-levels-20070517.patch
  1038: budb-ol_verify-20070706.patch
  1039: clone-dont-hold-vol-lock-20070516.patch
  1040: des-p-temp-volatile-20070703.patch
  1041: memcache-alloc-failures-20070623.patch
  1042: pagsh-krb5-20070710.patch
  1043: tvolser-locking-updates-20070322.patch

* Wed Jul 11 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-50.SLx
- SL5: improved afs-server init script; also set it to unconfined_exec_t
  in postinstall if selinux active
- updated CellServDB to current version from grand.central.org
- more patches from CVS:
  1033: volser-delete-clone-not-source-20070702
  1034: avoid-empty-uuid-20070618
  1035: forceallnewconns-prototype-20070627
  1036: volser-earlier-logging-20070627

* Tue Jun 26 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-49.SLx
- SL3: added corrected patch1032 from CVS to find 64bit syscall table on amd64
  (openafs-1.4.4-amd64-linux-24-syscall-probe-symbol-change-20070623-fixed)

* Sat Jun 23 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-47.SLx
- SL5: fix /etc/init.d/afs-server (missing fi in stop code)
- more patches from CVS:
- 1029: linux-kmem-destroy-fix-20070609
- 1030: vsprocs-avoid-bogus-error-20070606
- 1031: sl5-vfs-flush-3arg-20070612 (modified patch w/o ifdefs since that
  would require running regen.sh - which doesn't work on SL5)

* Mon May 28 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-46.SLx
- added recent patches from CVS:
- 1022: namei-dont-randomly-full-salvage-20070514
- 1023: vos-namelen-for-dump-restore-is-stupid-20070509
- 1024: supergroup-cleanup-20070516
- 1025: ptserver-fix-bitmap-20070516
- 1026: glibc24-jmp-buf-mangling-20070516 (SL5 only)
- 1027: rx-call-abort-release-refcount-20070425
- 1028: dont-fclose-null-20070514

* Wed May 02 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-44.SLx
- SL4/5 init script: fix cache partition detection on SL4/5
- SL4: replace patch1020 by slightly fixed version now in CVS
- add accompanying patch1021 (vmalloc-no-glock-20070418)

* Sat Mar 24 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-43.SLx
- SL4: added patch1020 by Chris Wing to turn off broken symlink caching, see
  https://lists.openafs.org/pipermail/openafs-devel/2007-March/015069.html
- add buildhost and version-release to AFS version string

* Thu Mar 22 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.4-42.SLx
- upstream release with new default of -nosuid for local cell, see OPENAFS-SA-2007-001
  * this may break things for sites relying on setuid files in AFS *
- added a word of warning to the SuidCells config file
- updated CellServDB to version from grand.central.org as of 2007-03-21
- added linux-task-pointer-safety-20070320 from CVS (see RT #55973)

* Thu Mar 15 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.3-0.rc3.41.SLx
- added support for xenU kernel from xensource
- fixed release detection on plain RHEL5

* Sun Mar 11 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.3-0.rc3.39.SLx
- added patch to make sure afs_pag_destroy() holds the glock, from 
  https://lists.openafs.org/pipermail/openafs-devel/2007-March/014985.html
- for SL5, changed comments on afsd options in the sysconfig file
- for SL5, changed default afsd options to " " (as recommended by developers)

* Wed Mar 07 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.3-0.rc3.38.SLx
- upstream rc3, could remove all recent patches
- support new xenU kernel variant on SL4
- automated macro for rc sources
- put back kernel module dependencies (except if built --without kreqs)

* Thu Mar 01 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.3-0.rc2.37.SLx
- added forecenewconns patch (from CVS)

* Sun Feb 25 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.3-0.rc2.36.SLx
- release candidate 2 of next upstream version
- still needs patches for the tasklist_lock issue
- added patch against leaks in the kernel module (from CVS)
- fixed retry of parallel build of only_libafs_tree 

* Sat Feb 24 2007 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-35.SLx
- put SLx macros into a helper script, recognize 4.9x as SL5
- put debuginfo override into a helper script, required by RPM on SL3/4
- fix debuginfo release
- omit kernel dependency from kernel-module unless built --with kreqs
  (work around yum limitation to help the kernel module plugin)

* Sat Dec 30 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-33.SLx
- override debuginfo package name for kernel module package
- to make this work, never build the module and userland in same run

* Wed Dec 20 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-32.SLx
- added three patches from CVS:
  Patch1011: openafs-1.4.2-linux-osi-cred-pool-byebye-20061218.patch
    will hopefully rid us of the panics due to "cannot malloc 4xxx bytes"
    observed on SL3 systems (2.4.21-47.0.1.ELsmp), even if unloaded
  Patch1012: openafs-1.4.2-linux26-disable-backing-readahead-20061109.patch
    is just there to make the noext one succeed, and should not do any harm
  Patch1013: openafs-1.4.2-linux-statfs-dentry-20061109.patch
    should provide a reasonable df output (not 0kB or 166YB) on recent
    2.6 kernels (SL5)

* Sat Nov 18 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-31.SLx
- el5 beta2: tasklist_lock is back but now GPL-only... do not use...

* Wed Nov 15 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-30.SLx
- add patch on SL3/amd64 to get the syscall hooks (should be in 1.4.3)

* Sun Nov 12 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-29.SLx
- should build on {SL3 SL4 SL5} x {i686 ia64 x86_64} x {any variant}
- renamed base package to openafs.SLx to get a common src.rpm; binary packages
  retain their usual names, with SL3 etc. appended to release; added build
  instructions to base package description
- krb5: build aklog and asetkey from source coming with the openafs tarball
  now; only ka-forwarder is still built from krb5-afs
- run parallel makes (and try again if the first attempt fails)
- make use of new (build) requirements on kernel[-devel] on SL4/5
- updated CellServDB to latest from grand.central.org (w/o openafs.org entry!)
- allow changing configure options from the command line
- record configure option in description of server package
- init script: check more thoroughly for a defined cell; try to guess it if not
- init script: subtract 32MB from cache partition size if it is ext3 when
  calculating the usable cache size, then use 70% (not 80)
- init script: use 100MB (not just 8) if cache is not on dedicated filesystem
- on SL5: separate init scripts for client and server
  - client: /etc/init.d/afs (as before), owned by openafs-client
  - server: /etc/init.d/afs-server (new), owned by openafs-server

* Thu Sep 21 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.fc4.18.SL5
- replace last patch by openafs-1.4.2fc4-rcu_read_lock.patch
- 32bit syscalls are in upstream now

* Mon Sep 18 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.fc3.17.SL5
- add openafs-1.4.2fc3-no-tasklist_lock.patch for build on RHEL5beta1 x86_64

* Sun Sep 17 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.fc3.16.SL5
- add openafs-1.4.2fc3-x64-32bitsyscalls.patch for build on RHEL5beta1 x86_64

* Sat Sep 09 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.fc3.15.SL5
- upstream final candidate 3
- besides a real fix for amd64, some quite substantial changes in salvager
  and volserver

* Sat Sep 02 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.fc2.15.SL5
- drop the remaining two patches that were not in 1.4.1

* Sat Aug 26 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.rc1.14.SL5
- find kernel headers in /usr/src/kernels
- add rxubikdeclare patch (not sure it is important)
- find kernel headers on FC6

* Thu Aug 24 2006 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.rc1.12.SL5
- drop patches no longer needed
- add patch 1005 for last tiny configure problem, run regen, add buildreq
  on autoconf, automake

* Sat Aug 12 2006  Stephan Wiesand <stephan.wiesand@desy.de> 1.4.2-0.beta3.11.SL5
- build on FC6T2 (ugly, ugly hacks)
- update CellServDB
- the last patch is now in upstream sources
- tag "copyright" changed to "license"
- aklog.1 is no longer in src/aklog

* Fri May 19 2006  Stephan Wiesand <stephan.wiesand@desy.de> 1.4.0-11.SL
- added openafs-1.4.1-rxkad-ticketsize.patch, see mail to openafs-info
  by H. Reuter 2006-05-17 (and the reply by R. Toebbicke)

* Mon Apr 24 2006  Stephan Wiesand <stephan.wiesand@desy.de> 1.4.0-10.SL
- new upstream release with critical bugs fixed in the fileserver
- removed patch 1002 (rra-soname-bug18767.patch), it's in upstream now
- new patch 1003 openafs-1.4.1-moduleparam.patch to get modules built on 2.6.9
  (shamelessly stolen from Derek Atkins' "official" SRPM)  
- pthreaded butc is now the default; package butc.lwp in addition, instead of
  a second butc.pthread
- adapted to upstream changes w.r.t. man pages (there are quite a few more
  now), again borrowing from Derek Atkins' spec, but still preferring the
  enhanced ones from #19268, and packaging many more of them
- spec changes to allow module build for hugemem kernels (Fabien Wernli)
- the same for the new largesmp variant
- added build requirements on gcc, flex, bison, ncurses-devel (Chris Huebsch)
- make sure /usr/kerberos/bin is leading in PATH when configuring krb5 stuff

* Thu Nov 03 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.0-8.SL
- final release of 1.4.0

* Tue Oct 04 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.4.0-0rc6.8.SL
- latest release candidate, possibly the last one before 1.4.0
- added man pages (like "official" spec, but add those from RT #19268 
  and prefer them over the default ones where duplicate)
- added openafs-LICENSE.Sun (from "official" package)
- removed unused source6 openafs-modname helper
- add x-bit to kernel module to get it stripped
- really do not turn off __check_files
- remove all unpackaged files
- added xstat_*_test to debug package
- added -authlibs and -authlibs-devel packages (like "official" package,
  but keep static libs in -devel to make updates painless)
- added patch for those to correct sonames (RT #18767)
- added copyauth, kseal, vsys to main package
- added ka-forwarder to -krb5 package
- added bos_util, voldump to -server package
- added des_prototypes.h to -devel package
- updated CellServDB to latest version from grand.central.org (June 1)
  and added hepix.org cell

* Thu Aug 11 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.82-5.SL
- removed LSB init info from start script (breaks recent chkconfig)

* Tue May 03 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.82-3.SL
- added a patch (1001) from Jason McCormick <jasonmc@cert.org> to fix
  cache coherence issues with this release

* Mon May 02 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.82-2.SL
- added missing ia64 changes by Jarek from 1.3.80-2.SL (kernel requirement,
  module built is .mp.ko, not .ko)
- turned off leftover debugspec

* Sat Apr 30 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.82-1.SL
- new upstream release fixing linux 2.6 issues including the first write
  access hanging on x86/UP
- hopefully guessed right about the fix for ia64 module build (by Jarek
  for 1.3.80-2.SL, but could not find the srpm)
- made the init script a separate source file
- in init script, do not run the on_network check if ENABLE_DYNROOT=1
- package the LWP builds of fileserver & volserver (which are built but
  not installed by default) in addition to the default pthreaded ones,
  with suffix ".lwp"
- package the pthread build of butc in addition to the default LWP one,
  with suffix ".pthread"
- disable patch101 (obsoleted by upstream hack)
- removed the build hack from 1.3.80-1.SL, fixed upstream

* Tue Mar 22 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.80-1.SL
- new upstream version supposed to fix many problems on linux 2.6
- notice the default afsd behaviour finally has changed to -nosettime;
  add -settime to your afsd options to get back the old behaviour
- added an ugly hack to get the kernel modules built
- updated CellServDB to version from grand.central.org as of today

* Tue Mar 01 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.79-4.SL
- made default cache location and size macros, removed cacheinfo source5,
  generate cacheinfo in install instead
- fixed default cache size to 100MB again, resurrected the message
  in -client's post, changed default location to /var/cache/openafs
- removed unused source21 (kernel-version.sh)
- changed last afs-krb5 build patch (patch configure, not configure.in,
  and do not wipe out 64bit patch to configure by rerunning autoconf)

* Sun Feb 27 2005 Stephan Wiesand <stephan.wiesand@desy.de> 1.3.79-3.SL
- this version is SL4/1.3 only
- get afs-krb5 going
- removed tons of old cruft & patches no longer used
- adapt module build to kernel[-smp]-devel: we now require this to be
  installed, and will only build the module package for a single kernel
  defined on the command line, or the running one in none is defined
  (this gets rid of all that redhat-buildsys voodoo which seems broken
   on SL4 anyway)
- added livesys & kdump executables to main package
- added optional openafs-debug package with additional tools
- made module name in package & init script libafs instead of openafs,
  since that's what the module registers as anyway (modprobe -r openafs
  would fail)
- added a patch (101) to fix the CACHESIZE=AUTOMATIC behaviour when the cache
  is mounted on some device with a long name

* Sat Feb 26 2005  Jaroslaw Polok <jaroslaw.polok@cern.ch>
- initial attempt at build for SL 4. (2.6 kernel)

* Fri Feb 18 2005  Jaroslaw Polok <jaroslaw.polok@cern.ch>
- added build of ia32e kernel module

* Mon Jan 31 2005  Troy Dawson <dawson@fnal.gov> 15.12.SL
- All changes came from Stephan Wiesand.  Many thanks for his pointers
- afsd options chaned in spec file
- /etc/sysconfig/afs set to be %%config(noreplace)
- requires wget
- removed openafs-compat %%pre scripts
- Added CellAlias file, with commented out example

* Wed Jan 19 2005  Troy Dawson <dawson@fnal.gov> 15.11.SL
- Put LC_ALL=C into the startup server test. This helps with 
  internationalization. Submitted by Jaroslaw Polok

* Mon Jan 17 2005 Enrico M.V. Fasanelli <enrico@le.infn.it> 15.10.SL
- applied patch from Chris Wing for 64bit aklog & Co.

* Thu Aug 12 2004  Troy Dawson <dawson@fnal.gov> 15.7.SL
- Put -fakestat in as a default option

* Tue Aug 10 2004  Troy Dawson <dawson@fnal.gov> 15.6.SL
- Updated CellServDB
- Put -dynroot in as a default option

* Sat Jun 19 2004  Troy Dawson <dawson@fnal.gov> 15.4.SL
- Made more changes to startup script. Does sanity checks of ThisCell

* Fri Jun 18 2004  Troy Dawson <dawson@fnal.gov> 15.3.SL
- Made change to /etc/init.d/afs startup script

* Sun May 30 2004 Jaroslaw.Polok@cern.ch
- rebuilt for Scientific Linux without site-specific setup
- kerberos 5 enabled in build
* Fri Apr 16 2004  Jaroslaw.Polok@cern.ch
- changed packaging of modules again: to followup Fedora Core
  (draft) rules and allow yum/apt/up2date to handle these

* Tue Apr 06 2004  Jaroslaw.Polok@cern.ch
- changed packaging of modules

* Sun Feb 22 2004  Jaroslaw.Polok@cern.ch
- Rebuilt for CERN E. Linux (ix86/ia64/x86_64)

* Thu Sep  4 2003  David Howells <dhowells@redhat.com>> 1.2.10-4
- don't use rpm from within spec file as this can cause problems

* Wed Sep  3 2003  David Howells <dhowells@redhat.com> 1.2.10-4
- added ia64 to the ExclusiveArch list

* Fri Aug 29 2003  <David Howells <dhowells@redhat.com>> 1.2.10-3
- get rid of a %%else that causes problems with rpm-4.0.4

* Fri Aug 22 2003  David Howells <dhowells@redhat.com> 1.2.10-3
- added rpmbuild cmdline defines to control which bits to build

* Wed Aug 20 2003  Nalin Dahyabhai <nalin@redhat.com>
- obey CFLAGS set at configure-time on i386/x86_64 linux
- openafs-krb5: look in $krb5_prefix/lib64 for Kerberos libraries if they are
  not found in $krb5_prefix/lib
- build the modules for PAM on x86_64
- when checking for res_search, try to link with it instead of checking for it
  in libraries, in case it's a macro or redefined by a macro
- use %%{ix86} instead of %%{all_x86} where appropriate
- install AFS libraries into %%{_libdir} instead of %%{_prefix}/lib

* Fri Aug 15 2003  <David Howells <dhowells@redhat.com>> 1.2.10-3
- permit the kernel-to-build-against to be selected by cmdline argument to
  rpmbuild if preferred

* Thu Aug 14 2003  Nalin Dahyabhai <nalin@redhat.com>
- fix compilation of openafs-krb5 bits against krb5 1.3

* Mon Aug 11 2003  <David Howells <dhowells@redhat.com>> 1.2.10-2
- got rid of all rpmlint errors
- delete certain tags (Packager/Vendor/Distribution)

* Fri Aug  8 2003  <David Howells <dhowells@redhat.com>> 1.2.10-1
- Adapted OpenAFS version 1.2.10 to compile in beehive


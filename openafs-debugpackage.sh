#!/bin/sh

cat <<EOF
%define debug_package \\
%ifnarch noarch\\
%global __debug_package 1\\
%package -n %debugpkgname\\
Release: %{pkgrelx}\\
Summary: Debug information for %(echo %debugpkgname|sed 's/-debuginfo//')\\
Group: Development/Debug\\
%description -n %debugpkgname\\
Debug information for %(echo %{debugpkgname}|sed 's/-debuginfo//').\\
This will hopefully be useful when analyzing kernel crash dumps.\\
%files -n %debugpkgname -f debugfiles.list\\
%defattr(-,root,root)\\
%endif\\
%{nil}
EOF

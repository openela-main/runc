%global with_check 0

%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0

%if 0%{?rhel} > 7 && ! 0%{?fedora}
%define gobuild(o:) \
go build -buildmode pie -compiler gc -tags="rpm_crashtraceback libtrust_openssl ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -linkmode=external -compressdwarf=false -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags'" -a -v %{?**};
%else
%if ! 0%{?gobuild:1}
%define gobuild(o:) GO111MODULE=off go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -linkmode=external -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '-Wl,-z,relro -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld '" -a -v %{?**};
%endif
%endif

%global provider github
%global provider_tld com
%global project opencontainers
%global repo runc
# https://github.com/opencontainers/runc
%global import_path %{provider}.%{provider_tld}/%{project}/%{repo}
%global git0 https://%{import_path}

Epoch: 1
Name: %{repo}
Version: 1.1.9
Release: 1%{?dist}
Summary: CLI for running Open Containers
# https://fedoraproject.org/wiki/PackagingDrafts/Go#Go_Language_Architectures
#ExclusiveArch: %%{go_arches}
# still use arch exclude as the macro above still refers %%{ix86} in RHEL8.4:
# https://bugzilla.redhat.com/show_bug.cgi?id=1905383
ExcludeArch: %{ix86}
License: ASL 2.0
URL: %{git0}
Source0: %{git0}/archive/v%{version}.tar.gz
Provides: oci-runtime
BuildRequires: golang >= 1.17.7
BuildRequires: git
BuildRequires: /usr/bin/go-md2man
BuildRequires: libseccomp-devel >= 2.5
Requires: libseccomp >= 2.5
Requires: criu

%description
The runc command can be used to start containers which are packaged
in accordance with the Open Container Initiative's specifications,
and to manage containers running under runc.

%prep
%autosetup -Sgit
sed -i '/\#\!\/bin\/bash/d' contrib/completions/bash/%{name}

%build
mkdir -p GOPATH
pushd GOPATH
    mkdir -p src/%{provider}.%{provider_tld}/%{project}
    ln -s $(dirs +1 -l) src/%{import_path}
popd

pushd GOPATH/src/%{import_path}
export GO111MODULE=off
export GOPATH=%{gopath}:$(pwd)/GOPATH
export CGO_CFLAGS="%{optflags} -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64"
export BUILDTAGS="selinux seccomp"
export LDFLAGS="-X main.gitCommit= -X main.version=%{version}"
%gobuild -o %{name} %{import_path}

pushd man
./md2man-all.sh
popd

%install
make install install-man install-bash DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir} BINDIR=%{_bindir}

%check

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc MAINTAINERS_GUIDE.md PRINCIPLES.md README.md CONTRIBUTING.md
%{_bindir}/%{name}
%{_mandir}/man8/%{name}*
%{_datadir}/bash-completion/completions/%{name}

%changelog
* Fri Aug 11 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.9-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.9
- Related: #2176055

* Fri Jul 21 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.8-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.8
- Related: #2176055

* Fri Jun 16 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.7-2
- rebuild for following CVEs:
CVE-2022-41724
- Resolves: #2179972

* Wed May 03 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.7-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.7
- Related: #2176055

* Wed Apr 12 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.6-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.6
- Related: #2176055

* Fri Mar 31 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.5-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.5
- Related: #2176055

* Thu Mar 09 2023 Jindrich Novy <jnovy@redhat.com> - 1:1.1.4-2
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.4
- Related: #2176055

* Fri Aug 26 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.1.4-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.4
- Related: #2061390

* Thu Aug 25 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.1.3-3
- fix "Error: runc: exec failed: unable to start container process:
  open /dev/pts/0: operation not permitted: OCI permission denied"
- Related: #2061390

* Wed Jun 15 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.1.3-2
- add patch in attempt to fix gating tests - thanks to Kir Kolyshkin
- Related: #2061390

* Thu Jun 09 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.1.3-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.3
- Related: #2061390

* Fri Jun 03 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.1.2-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.2
- Related: #2061390

* Thu May 12 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.0.3-6
- Fix every podman run invocation generates two "Couldn't stat device
  /dev/char/10:200: No such file or directory" lines in the journal
- Related: #2061390

* Wed May 11 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.0.3-5
- BuildRequires: /usr/bin/go-md2man
- Related: #2061390

* Fri Apr 08 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.0.3-4
- Related: #2061390

* Tue Mar 08 2022 Jindrich Novy <jnovy@redhat.com> - 1:1.0.3-3
- require at least libseccomp >= 2.5
- Resolves: #2053990

* Wed Feb 16 2022 Jindrich Novy <jnovy@redhat.com> - 1.0.3-2
- rollback to 1.0.3 due to gating test issues
- Related: #2001445

* Tue Jan 18 2022 Jindrich Novy <jnovy@redhat.com> - 1.1.0-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.0
- Related: #2001445

* Mon Dec 06 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.3-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.3
- Related: #2001445

* Wed Aug 25 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.2-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.2
- Related: #1934415

* Fri Aug 06 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-5
- do not use versioned provide
- Related: #1934415

* Thu Jul 29 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-4
- fix "unknown version" displayed by runc -v
- Related: #1934415

* Mon Jul 26 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-3
- be sure to compile runc binaries the right way
- Related: #1934415

* Mon Jul 26 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-2
- use Makefile
- Related: #1934415

* Wed Jul 21 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.1
- Related: #1934415

* Thu May 20 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-76.rc95
- updated to rc95 to fix CVE-2021-30465
- Related: #1934415

* Tue May 18 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-75.rc94
- set GO111MODULE=off to fix build
- Related: #1934415

* Fri May 14 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-74.rc94
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.0-rc94
- Related: #1934415

* Tue May 11 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-73.rc93
- fix CVE-2021-30465
- Related: #1934415

* Tue Mar 30 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-72.rc93
- upload rc93 tarball
- Related: #1934415

* Tue Mar 30 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-71.rc93
- update to rc93
- Related: #1934415

* Fri Jan 29 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-70.rc92
- add missing Provides: oci-runtime = 1
- Related: #1883490

* Tue Dec 08 2020 Jindrich Novy <jnovy@redhat.com> - 1.0.0-69.rc92
- still use ExcludeArch as go_arches macro is broken for 8.4
- Related: #1883490

* Tue Aug 11 2020 Jindrich Novy <jnovy@redhat.com> - 1.0.0-68.rc92
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.0-rc92
- propagate proper CFLAGS to CGO_CFLAGS to assure code hardening and optimization
- Related: #1821193

* Thu Jul 02 2020 Jindrich Novy <jnovy@redhat.com> - 1.0.0-67.rc91
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.0-rc91
- Related: #1821193

* Tue May 12 2020 Jindrich Novy <jnovy@redhat.com> - 1.0.0-66.rc10
- synchronize containter-tools 8.3.0 with 8.2.1
- Related: #1821193

* Wed Feb 12 2020 Jindrich Novy <jnovy@redhat.com> - 1.0.0-65.rc10
- address CVE-2019-19921 by updating to rc10
- Resolves: #1801887

* Wed Dec 11 2019 Jindrich Novy <jnovy@redhat.com> - 1.0.0-64.rc9
- use no_openssl in BUILDTAGS (no vendored crypto in runc)
- Related: RHELPLAN-25139

* Mon Dec 09 2019 Jindrich Novy <jnovy@redhat.com> - 1.0.0-63.rc9
- be sure to use golang >= 1.12.12-4
- Related: RHELPLAN-25139

* Thu Nov 28 2019 Jindrich Novy <jnovy@redhat.com> - 1.0.0-62.rc9
- rebuild because of CVE-2019-9512 and CVE-2019-9514
- Resolves: #1766331, #1766303

* Thu Nov 21 2019 Jindrich Novy <jnovy@redhat.com> - 1.0.0-61.rc9
- update to runc 1.0.0-rc9 release
- amend golang deps
- fixes CVE-2019-16884
- Resolves: #1759651

* Mon Jun 17 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-60.rc8
- Resolves: #1721247 - enable fips mode

* Mon Jun 17 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-59.rc8
- Resolves: #1720654 - rebase to v1.0.0-rc8

* Thu Apr 11 2019 Eduardo Santiago <santiago@redhat.com> - 1.0.0-57.rc5.dev.git2abd837
- Resolves: #1693424 - podman rootless: cannot specify gid= mount options

* Wed Feb 27 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-56.rc5.dev.git2abd837
- change-default-root patch not needed as there's no docker on rhel8

* Tue Feb 12 2019 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-55.rc5.dev.git2abd837
- Resolves: CVE-2019-5736

* Tue Dec 18 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.0.0-54.rc5.dev.git2abd837
- re-enable debuginfo

* Mon Dec 17 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.0.0-53.rc5.dev.git2abd837
- go toolset not in scl anymore

* Wed Sep 26 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.0.0-52.rc5.dev.git2abd837
- rebase

* Fri Aug 31 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-51.dev.gitfdd8055
- Fix handling of tmpcopyup

* Fri Aug 24 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.0.0-49.rc5.dev.gitb4e2ecb
- %%gobuild uses no_openssl
- remove unused devel and unit-test subpackages

* Tue Aug 07 2018 Lokesh Mandvekar <lsm5@redhat.com> - 2:1.0.0-48.rc5.dev.gitad0f525
- build with %%gobuild
- exlude i686 temporarily because of go-toolset issues

* Mon Jul 30 2018 Florian Weimer <fweimer@redhat.com> - 1.0.0-47.dev.gitb4e2ecb
- Rebuild with fixed binutils

* Fri Jul 27 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-46.dev.gitb4e2ecb
- Add patch https://github.com/opencontainers/runc/pull/1807 to allow
- runc and podman to work with sd_notify

* Wed Jul 18 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.0.0-40.rc5.dev.gitad0f525
- Remove sysclt handling, not needed in RHEL8
- Make sure package built with seccomp flags
- Remove rectty
- Add completions

* Fri Jun 15 2018 Dan Walsh <dwalsh@redhat.com> - 2:1.0.0-36.rc5.dev.gitad0f525
- Better handling of user namespace

* Tue May 1 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-31.rc5.git0cbfd83
- Fix issues between SELinux and UserNamespace

* Tue Apr 17 2018 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.0.0-27.rc5.dev.git4bb1fe4
- rebuilt, placed missing changelog entry back

* Tue Feb 27 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-26.rc5.git4bb1fe4
- release v1.0.0~rc5

* Wed Jan 24 2018 Dan Walsh <dwalsh@redhat.name> - 1.0.0-26.rc4.git9f9c962
- Bump to the latest from upstream

* Mon Dec 18 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-25.rc4.gite6516b3
- built commit e6516b3

* Fri Dec 15 2017 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.0.0-24.rc4.dev.gitc6e4a1e.1
- rebase to c6e4a1ebeb1a72b529c6f1b6ee2b1ae5b868b14f
- https://github.com/opencontainers/runc/pull/1651

* Tue Dec 12 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-23.rc4.git1d3ab6d
- Resolves: #1524654

* Sun Dec 10 2017 Dan Walsh <dwalsh@redhat.name> - 1.0.0-22.rc4.git1d3ab6d
- Many Stability fixes
- Many fixes for rootless containers
- Many fixes for static builds

* Thu Nov 09 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-21.rc4.dev.gitaea4f21
- enable debuginfo and include -buildmode=pie for go build

* Tue Nov 07 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-20.rc4.dev.gitaea4f21
- use Makefile

* Tue Nov 07 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-19.rc4.dev.gitaea4f21
- disable debuginfo temporarily

* Fri Nov 03 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-18.rc4.dev.gitaea4f21
- enable debuginfo

* Wed Oct 25 2017 Dan Walsh <dwalsh@redhat.name> - 1.0.0-17.rc4.gitaea4f21
- Add container-selinux prerequires to make sure runc is labeled correctly

* Thu Oct 19 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-16.rc4.dev.gitaea4f21
- correct the release tag "rc4dev" -> "rc4.dev" cause I'm OCD

* Mon Oct 16 2017 Dan Walsh <dwalsh@redhat.com> - 1.0.0-15.rc4dev.gitaea4f21
- Use the same checkout as Fedora for lates CRI-O

* Fri Sep 22 2017 Frantisek Kluknavsky <fkluknav@redhat.com> - 1.0.0-14.rc4dev.git84a082b
- rebase to 84a082bfef6f932de921437815355186db37aeb1

* Tue Jun 13 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-13.rc3.gitd40db12
- Resolves: #1479489
- built commit d40db12

* Tue Jun 13 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-12.1.gitf8ce01d
- disable s390x temporarily because of indefinite wait times on brew

* Tue Jun 13 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-11.1.gitf8ce01d
- correct previous bogus date :\

* Mon Jun 12 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-10.1.gitf8ce01d
- Resolves: #1441737 - run sysctl_apply for sysctl knob

* Tue May 09 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-9.1.gitf8ce01d
- Resolves: #1447078 - change default root path
- add commit e800860 from runc @projectatomic/change-root-path

* Fri May 05 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-8.1.gitf8ce01d
- Resolves: #1441737 - enable kernel sysctl knob /proc/sys/fs/may_detach_mounts

* Thu Apr 13 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-7.1.gitf8ce01d
- Resolves: #1429675
- built @opencontainers/master commit f8ce01d

* Thu Mar 16 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-4.1.gitee992e5
- built @projectatomic/master commit ee992e5

* Fri Feb 24 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-3.rc2
- Resolves: #1426674
- built projectatomic/runc_rhel_7 commit 5d93f81

* Mon Feb 06 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-2.rc2
- Resolves: #1419702 - rebase to latest upstream master
- built commit b263a43

* Wed Jan 11 2017 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-1.rc2
- Resolves: #1412239 - *CVE-2016-9962* - set init processes as non-dumpable,
runc patch from Michael Crosby <crosbymichael@gmail.com>

* Wed Sep 07 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.1-6
- Resolves: #1373980 - rebuild for 7.3.0

* Sat Jun 25 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.1-5
- build with golang >= 1.6.2

* Tue May 31 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.1-4
- release tags were inconsistent in the previous build

* Tue May 31 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.1-1
- Resolves: #1341267 - rebase runc to v0.1.1

* Tue May 03 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.0-3
- add selinux build tag
- add BR: libseccomp-devel

* Tue May 03 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.0-2
- Resolves: #1328970 - add seccomp buildtag

* Tue Apr 19 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.1.0-1
- Resolves: rhbz#1328616 - rebase to v0.1.0

* Tue Mar 08 2016 Lokesh Mandvekar <lsm5@redhat.com> - 0.0.8-1.git4155b68
- Resolves: rhbz#1277245 - bump to 0.0.8
- Resolves: rhbz#1302363 - criu is a runtime dep
- Resolves: rhbz#1302348 - libseccomp-golang is bundled in Godeps
- manpages included

* Wed Nov 25 2015 jchaloup <jchaloup@redhat.com> - 1:0.0.5-0.1.git97bc9a7
- Update to 0.0.5, introduce Epoch for Fedora due to 0.2 version instead of 0.0.2

* Fri Aug 21 2015 Jan Chaloupka <jchaloup@redhat.com> - 0.2-0.2.git90e6d37
- First package for Fedora
  resolves: #1255179

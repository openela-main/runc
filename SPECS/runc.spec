%global with_check 0

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

Epoch: 4
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
* Fri Aug 11 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.9-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.9
- Related: #2176063

* Fri Jul 21 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.8-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.8
- Related: #2176063

* Wed Jun 14 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.7-2
- rebuild for following CVEs:
CVE-2021-43784 CVE-2022-41724 CVE-2023-28642
- Resolves: #2033659
- Resolves: #2179973
- Resolves: #2183103

* Tue May 02 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.7-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.7
- Related: #2176063

* Wed Apr 12 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.6-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.6
- Related: #2176063

* Fri Mar 31 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.5-2
- runc 1.1.5 resolves CVE-2023-25809 and CVE-2023-27561
- Resolves: #2176110
- Resolves: #2183098

* Wed Mar 29 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.5-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.5
- Related: #2176063

* Tue Feb 07 2023 Jindrich Novy <jnovy@redhat.com> - 4:1.1.4-2
- rebuild
- Resolves: #2102995

* Fri Aug 26 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.1.4-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.4
- Related: #2061316

* Wed Jul 27 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.1.3-2
- add patch in attempt to fix gating tests - thanks to Kir Kolyshkin
- Related: #2061316

* Thu Jun 09 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.1.3-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.3
- Related: #2061316

* Thu Jun 02 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.1.2-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.2
- Related: #2061316

* Fri May 13 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.0.3-5
- Re-enable debuginfo
- Related: #2061316

* Wed May 11 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.0.3-4
- BuildRequires: /usr/bin/go-md2man
- Related: #2061316

* Wed Feb 16 2022 Jindrich Novy <jnovy@redhat.com> - 4:1.0.3-3
- rollback runc due to failing gating tests
- Related: #2000051

* Wed Jan 26 2022 Jindrich Novy <jnovy@redhat.com> - 3:1.1.0-2
- Epoch: 3 as the oldest runc build in RHEL9 has Epoch: 2
- Related: #2000051

* Tue Jan 18 2022 Jindrich Novy <jnovy@redhat.com> - 1.1.0-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.1.0
- Related: #2000051

* Mon Dec 06 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.3-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.3
- Related: #2000051

* Fri Oct 01 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.2-3
- perform only sanity/installability tests for now
- Related: #2000051

* Wed Sep 29 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.2-2
- add gating.yaml
- Related: #2000051

* Fri Sep 03 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.2-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.2
- Related: #2000051

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 1.0.1-6
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Aug 06 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-5
- do not use versioned provide
- Resolves: #1974950

* Thu Jul 29 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-4
- fix "unknown version" displayed by runc -v
- Related: #1970747

* Mon Jul 26 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-3
- be sure to compile runc binaries the right way
- Related: #1970747

* Mon Jul 26 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-2
- use Makefile
- Related: #1970747

* Mon Jul 19 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.1-1
- update to https://github.com/opencontainers/runc/releases/tag/v1.0.1
- Related: #1970747

* Wed Jun 23 2021 Lokesh Mandvekar <lsm5@redhat.com> - 1.0.0-338.rc95
- Resolves: #1974950 - versionless oci-runtime

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 1.0.0-337.rc95
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Mon Jun 14 2021 Jindrich Novy <jnovy@redhat.com> - 1.0.0-336.rc95
- add GO111MODULE=off
- Related: #1970747

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 2:1.0.0-332.dev.gitbd013b6
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Feb 19 2021 Jindrich Novy <jnovy@redhat.com> - 2:1.0.0-331.dev.gitbd013b6
- use %%{go_arches}

* Thu Dec  3 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-330.dev.gitbd013b6
- autobuilt bd013b6

* Wed Dec  2 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-329.dev.git56a1f1f
- autobuilt 56a1f1f

* Wed Dec  2 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-328.dev.git3517877
- autobuilt 3517877

* Wed Dec  2 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-327.dev.git2a50985
- autobuilt 2a50985

* Mon Nov 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-326.dev.git2b92c25
- autobuilt 2b92c25

* Mon Nov 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-325.dev.git7cfb3dc
- autobuilt 7cfb3dc

* Tue Nov 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-324.dev.git06b737b
- autobuilt 06b737b

* Mon Nov 23 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-323.dev.gitd15ffff
- autobuilt d15ffff

* Mon Nov 23 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-322.dev.git0b11e29
- autobuilt 0b11e29

* Fri Nov 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-321.dev.gitb69070a
- autobuilt b69070a

* Wed Nov 18 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-320.dev.git689513c
- autobuilt 689513c

* Wed Nov 11 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-319.dev.git636f23d
- autobuilt 636f23d

* Tue Nov 10 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-318.dev.git30233a7
- autobuilt 30233a7

* Sat Nov  7 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-317.dev.git27227a9
- autobuilt 27227a9

* Fri Nov  6 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-316.dev.gite8498d3
- autobuilt e8498d3

* Thu Nov  5 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-315.dev.gitcf6c074
- autobuilt cf6c074

* Fri Oct 23 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-314.dev.git07e35a7
- autobuilt 07e35a7

* Wed Oct 21 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-313.dev.git411e413
- autobuilt 411e413

* Tue Oct 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-312.dev.git7ba005b
- autobuilt 7ba005b

* Fri Oct 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-311.dev.gitd8bfd6c
- autobuilt d8bfd6c

* Fri Oct  9 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-310.dev.git44f221e
- autobuilt 44f221e

* Thu Oct  8 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-309.dev.git10825f7
- autobuilt 10825f7

* Wed Oct  7 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-308.dev.gitc11e997
- autobuilt c11e997

* Tue Oct  6 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-307.dev.gitbb539a9
- autobuilt bb539a9

* Mon Oct  5 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-306.dev.gitc23c05e
- autobuilt c23c05e

* Sat Oct  3 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-305.dev.gitf671f6b
- autobuilt f671f6b

* Fri Oct  2 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-304.dev.git750036e
- autobuilt 750036e

* Thu Oct  1 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-303.dev.gita220b9c
- autobuilt a220b9c

* Wed Sep 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-302.dev.gitecfad5a
- autobuilt ecfad5a

* Tue Sep 29 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-301.dev.git49d4507
- autobuilt 49d4507

* Mon Sep 28 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-300.dev.git43d2b10
- autobuilt 43d2b10

* Sat Sep 26 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-299.dev.git6e5320f
- autobuilt 6e5320f

* Fri Sep 25 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-298.dev.git33faa5d
- autobuilt 33faa5d

* Tue Sep 22 02:11:55 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-297.dev.git190fcf2
- autobuilt 190fcf2

* Thu Sep 17 10:12:11 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-296.dev.gitd636ad6
- autobuilt d636ad6

* Tue Sep 15 16:12:54 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-295.dev.git892477c
- autobuilt 892477c

* Fri Sep 11 03:13:03 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-294.dev.git2cf8d24
- autobuilt 2cf8d24

* Thu Sep 10 20:12:51 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-293.dev.gitbbd4ffe
- autobuilt bbd4ffe

* Thu Sep 10 13:12:15 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-292.dev.gitab740e9
- autobuilt ab740e9

* Wed Sep  9 16:12:18 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-291.dev.git165ecd2
- autobuilt 165ecd2

* Thu Sep  3 14:12:46 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-290.dev.gitcbb0a79
- autobuilt cbb0a79

* Tue Aug 25 02:11:36 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-289.dev.git09ddc63
- autobuilt 09ddc63

* Fri Aug 21 20:10:31 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-288.dev.gite5f2eae
- autobuilt e5f2eae

* Thu Aug 20 19:10:38 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-287.dev.gitf844a2f
- autobuilt f844a2f

* Thu Aug 20 15:10:19 UTC 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-286.dev.gite949339
- autobuilt e949339

* Wed Aug 19 07:11:09 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-285.dev.git2265daa
- autobuilt 2265daa

* Tue Aug 18 05:11:22 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-284.dev.gita5847db
- autobuilt a5847db

* Tue Aug 18 01:11:15 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-283.dev.git7930f0c
- autobuilt 7930f0c

* Mon Aug 17 19:10:53 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-282.dev.git49a7346
- autobuilt 49a7346

* Thu Aug 13 04:11:15 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-281.dev.git54c53b1
- autobuilt 54c53b1

* Wed Aug 12 16:10:02 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-280.dev.gita2d1f85
- autobuilt a2d1f85

* Mon Aug 10 15:11:15 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-279.dev.gitdedadbf
- autobuilt dedadbf

* Thu Aug 06 05:10:09 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-278.dev.gita340fa9
- autobuilt a340fa9

* Tue Aug 04 05:09:55 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-277.dev.gitf668854
- autobuilt f668854

* Mon Aug 03 08:12:14 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-276.dev.git78d02e8
- autobuilt 78d02e8

* Sat Aug 01 01:09:45 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-275.dev.git3de3112
- autobuilt 3de3112

* Fri Jul 31 03:09:51 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-274.dev.gitd6f5641
- autobuilt d6f5641

* Fri Jul 31 00:09:50 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-273.dev.git46243fc
- autobuilt 46243fc

* Thu Jul 30 19:10:40 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-272.dev.git97b02cf
- autobuilt 97b02cf

* Wed Jul 29 03:09:14 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-271.dev.git67169a9
- autobuilt 67169a9

* Thu Jul 23 20:09:40 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-270.dev.gitd65df61
- autobuilt d65df61

* Wed Jul 22 19:10:06 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-269.dev.git86d9399
- autobuilt 86d9399

* Mon Jul 20 03:09:22 GMT 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-268.dev.gitf8749ba
- autobuilt f8749ba

* Thu Jul 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-267.dev.gitf9850af
- autobuilt f9850af

* Mon Jul 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-266.dev.gitb7d8f3b
- autobuilt b7d8f3b

* Mon Jul 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-265.dev.git47fbafb
- autobuilt 47fbafb

* Thu Jul 09 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-264.dev.gitcf1273a
- autobuilt cf1273a

* Thu Jul 09 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-263.dev.git545ebdd
- autobuilt 545ebdd

* Thu Jul 09 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-262.dev.gitfbf047b
- autobuilt fbf047b

* Wed Jul 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-261.dev.gitce54a9d
- autobuilt ce54a9d

* Wed Jul 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-260.dev.git9806eb5
- autobuilt 9806eb5

* Wed Jul 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-259.dev.git5517d1d
- autobuilt 5517d1d

* Tue Jul 07 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-258.dev.git819fcc6
- autobuilt 819fcc6

* Mon Jul 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-257.dev.git30dc54a
- autobuilt 30dc54a

* Mon Jul 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-256.dev.git3f81131
- autobuilt 3f81131

* Mon Jul 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-255.dev.git46a304b
- autobuilt 46a304b

* Fri Jul 03 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-254.dev.git3cb1909
- autobuilt 3cb1909

* Thu Jul 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-253.dev.git6f5edda
- autobuilt 6f5edda

* Wed Jun 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-252.dev.git1b94395
- autobuilt 1b94395

* Mon Jun 22 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-251.dev.git834c457
- autobuilt 834c457

* Sat Jun 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-250.dev.git0fa097f
- autobuilt 0fa097f

* Fri Jun 19 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-249.dev.gitdff7685
- autobuilt dff7685

* Fri Jun 19 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-248.dev.git9748b48
- autobuilt 9748b48

* Thu Jun 18 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-247.dev.git819c40b
- autobuilt 819c40b

* Wed Jun 17 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-246.dev.git406298f
- autobuilt 406298f

* Wed Jun 17 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-245.dev.git12a7c8f
- autobuilt 12a7c8f

* Tue Jun 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-244.dev.git82d2fa4
- autobuilt 82d2fa4

* Tue Jun 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-243.dev.git55c77cb
- autobuilt 55c77cb

* Tue Jun 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-242.dev.git5b247e7
- autobuilt 5b247e7

* Thu Jun 11 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-241.dev.gitfdc4837
- autobuilt fdc4837

* Thu Jun 11 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-240.dev.gited9d93e
- autobuilt ed9d93e

* Wed Jun 10 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-239.dev.gitb216304
- autobuilt b216304

* Fri Jun 05 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-238.dev.git1b97c04
- autobuilt 1b97c04

* Thu Jun 04 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-237.dev.git2a04669
- autobuilt 2a04669

* Tue Jun 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-236.dev.git0853956
- autobuilt 0853956

* Tue Jun 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-235.dev.git1302020
- autobuilt 1302020

* Sun May 31 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-234.dev.gitdbe5aca
- autobuilt dbe5aca

* Sun May 31 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-233.dev.git0f7ffbe
- autobuilt 0f7ffbe

* Sun May 31 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-232.dev.gita30f255
- autobuilt a30f255

* Sat May 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-231.dev.gite664e73
- autobuilt e664e73

* Sat May 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-230.dev.git2679754
- autobuilt 2679754

* Sat May 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-229.dev.git774a9e7
- autobuilt 774a9e7

* Fri May 29 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-228.dev.git64dbdb8
- autobuilt 64dbdb8

* Wed May 27 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-227.dev.git4f0bdaf
- autobuilt 4f0bdaf

* Wed May 27 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-226.dev.gita891fee
- autobuilt a891fee

* Tue May 26 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-225.dev.git1f737ee
- autobuilt 1f737ee

* Mon May 25 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-224.dev.git7673bee
- autobuilt 7673bee

* Thu May 21 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-223.dev.git3c8da9d
- autobuilt 3c8da9d

* Thu May 21 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-222.dev.git21cb236
- autobuilt 21cb236

* Wed May 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-221.dev.git8cd84e3
- autobuilt 8cd84e3

* Wed May 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-220.dev.git716079f
- autobuilt 716079f

* Wed May 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-219.dev.gitcd4b71c
- autobuilt cd4b71c

* Wed May 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-218.dev.git9a808dd
- autobuilt 9a808dd

* Tue May 19 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-217.dev.gitb207d57
- autobuilt b207d57

* Tue May 19 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-216.dev.gitf369199
- autobuilt f369199

* Mon May 18 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-215.dev.git53a4649
- autobuilt 53a4649

* Thu May 14 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-214.dev.git3f1e886
- autobuilt 3f1e886

* Wed May 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-213.dev.git85d4264
- autobuilt 85d4264

* Wed May 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-212.dev.git4b71877
- autobuilt 4b71877

* Wed May 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-211.dev.gitdf3d7f6
- autobuilt df3d7f6

* Wed May 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-210.dev.git58bf083
- autobuilt 58bf083

* Tue May 12 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-209.dev.git2b9a36e
- autobuilt 2b9a36e

* Tue May 12 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-208.dev.git867c9f5
- autobuilt 867c9f5

* Fri May 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-207.dev.git2c8d668
- autobuilt 2c8d668

* Fri May 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-206.dev.git6621af8
- autobuilt 6621af8

* Fri May 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-205.dev.git2b31437
- autobuilt 2b31437

* Fri May 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-204.dev.git47a7343
- autobuilt 47a7343

* Wed May 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-203.dev.git64416d3
- autobuilt 64416d3

* Tue May 05 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-202.dev.gita57358e
- autobuilt a57358e

* Mon May 04 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-201.dev.git96310f0
- autobuilt 96310f0

* Mon May 04 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-200.dev.gita0ddd02
- autobuilt a0ddd02

* Mon May 04 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-199.dev.git12ba2a7
- autobuilt 12ba2a7

* Sun May 03 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-198.dev.git609ba79
- autobuilt 609ba79

* Sun May 03 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-197.dev.gitf6439a8
- autobuilt f6439a8

* Wed Apr 29 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-196.dev.gitdd8d48e
- autobuilt dd8d48e

* Wed Apr 29 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-195.dev.git051d670
- autobuilt 051d670

* Wed Apr 29 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-194.dev.gitc18485a
- autobuilt c18485a

* Tue Apr 28 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-193.dev.git0a4dcc0
- autobuilt 0a4dcc0

* Tue Apr 28 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-192.dev.git80e2d1f
- autobuilt 80e2d1f

* Mon Apr 27 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-191.dev.git53fb4a5
- autobuilt 53fb4a5

* Sat Apr 25 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-190.dev.gitb19f9ce
- autobuilt b19f9ce

* Sat Apr 25 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-189.dev.git0fd8d46
- autobuilt 0fd8d46

* Fri Apr 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-188.dev.git634e51b
- autobuilt 634e51b

* Fri Apr 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-187.dev.git49ca1fd
- autobuilt 49ca1fd

* Fri Apr 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-186.dev.git78ff279
- autobuilt 78ff279

* Fri Apr 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-185.dev.git4402442
- autobuilt 4402442

* Thu Apr 23 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-184.dev.gitdbe44cb
- autobuilt dbe44cb

* Wed Apr 22 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-183.dev.gitcdce577
- autobuilt cdce577

* Tue Apr 21 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-182.dev.git46be7b6
- autobuilt 46be7b6

* Mon Apr 20 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-181.dev.git5b38ef7
- autobuilt 5b38ef7

* Thu Apr 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-180.dev.gite4981c9
- autobuilt e4981c9

* Thu Apr 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-179.dev.git9f6a2d4
- autobuilt 9f6a2d4

* Wed Apr 15 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-178.dev.git191def7
- autobuilt 191def7

* Tue Apr 14 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-177.dev.git56aca5a
- autobuilt 56aca5a

* Tue Apr 14 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-176.dev.git5c6216b
- autobuilt 5c6216b

* Mon Apr 13 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-175.dev.git13431e0
- autobuilt 13431e0

* Thu Apr 09 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-174.dev.gitccbb336
- autobuilt ccbb336

* Thu Apr 09 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-173.dev.gitd65ba5f
- autobuilt d65ba5f

* Wed Apr 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-172.dev.git9a93b73
- autobuilt 9a93b73

* Wed Apr 08 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-171.dev.git5c15da9
- autobuilt 5c15da9

* Tue Apr 07 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-170.dev.gitd3fdacb
- autobuilt d3fdacb

* Mon Apr 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-169.dev.gitd5e91b1
- autobuilt d5e91b1

* Mon Apr 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-168.dev.git0c7a9c0
- autobuilt 0c7a9c0

* Mon Apr 06 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-167.dev.git6cda0ea
- autobuilt 6cda0ea

* Fri Apr 03 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-166.dev.gite4363b0
- autobuilt e4363b0

* Thu Apr 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-165.dev.git0c6659a
- autobuilt 0c6659a

* Thu Apr 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-164.dev.gitf8e1388
- autobuilt f8e1388

* Thu Apr 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-163.dev.gite3e26ca
- autobuilt e3e26ca

* Tue Mar 31 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-162.dev.git9ec5b03
- autobuilt 9ec5b03

* Mon Mar 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-161.dev.git4a9e174
- autobuilt 4a9e174

* Mon Mar 30 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-160.dev.git8df45c8
- autobuilt 8df45c8

* Fri Mar 27 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-159.dev.gitf1eea90
- autobuilt f1eea90

* Fri Mar 27 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-158.dev.gitd4a6a1d
- autobuilt d4a6a1d

* Thu Mar 26 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-157.dev.gitcebef0e
- autobuilt cebef0e

* Thu Mar 26 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-156.dev.git96596cb
- autobuilt 96596cb

* Tue Mar 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-155.dev.gitbe51398
- autobuilt be51398

* Tue Mar 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-154.dev.gitcc183ca
- autobuilt cc183ca

* Tue Mar 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-153.dev.git4e6d8a0
- autobuilt 4e6d8a0

* Tue Mar 24 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-152.dev.git3087d43
- autobuilt 3087d43

* Mon Mar 23 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-151.dev.git07bd280
- autobuilt 07bd280

* Mon Mar 23 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-150.dev.git1797622
- autobuilt 1797622

* Tue Mar 17 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-149.dev.git939cd0b
- autobuilt 939cd0b

* Mon Mar 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-148.dev.git525b9f3
- autobuilt 525b9f3

* Mon Mar 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-147.dev.git981dbef
- autobuilt 981dbef

* Sat Mar 14 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-146.dev.git8615da6
- autobuilt 8615da6

* Mon Mar 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-145.dev.git3b7e32f
- autobuilt 3b7e32f

* Tue Feb 04 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-144.dev.gite6555cc
- autobuilt e6555cc

* Fri Jan 31 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-143.dev.gitff107ee
- autobuilt ff107ee

* Tue Jan 28 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-142.dev.git2b5730a
- autobuilt 2b5730a

* Wed Jan 22 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-141.dev.git2fc03cc
- autobuilt 2fc03cc

* Thu Jan 16 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-140.dev.gitf6fb7a0
- autobuilt f6fb7a0

* Tue Jan 14 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-139.dev.git709377c
- autobuilt 709377c

* Tue Jan 14 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-138.dev.git5cc0dea
- autobuilt 5cc0dea

* Thu Jan 02 2020 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-137.dev.git2b52db7
- autobuilt 2b52db7

* Tue Dec 31 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-136.dev.gita88592a
- autobuilt a88592a

* Tue Dec 17 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-135.dev.git7496a96
- autobuilt 7496a96

* Fri Dec 06 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-134.dev.git201b063
- autobuilt 201b063

* Fri Dec 06 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-133.dev.gite1b5af0
- autobuilt e1b5af0

* Fri Dec 06 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-132.dev.git5e63695
- autobuilt 5e63695

* Thu Dec 05 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-131.dev.git8bb10af
- autobuilt 8bb10af

* Mon Dec 02 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-130.dev.gitc35c2c9
- autobuilt c35c2c9

* Sat Nov 16 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-129.dev.git2186cfa
- autobuilt 2186cfa

* Tue Nov 05 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-128.dev.git46def4c
- autobuilt 46def4c

* Thu Oct 31 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-127.dev.gitb133fea
- autobuilt b133fea

* Thu Oct 31 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-126.dev.gite57a774
- autobuilt e57a774

* Tue Oct 29 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-125.dev.gitd239ca8
- autobuilt d239ca8

* Tue Oct 29 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-124.dev.git03cf145
- autobuilt 03cf145

* Thu Oct 24 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-123.dev.gitc4d8e16
- autobuilt c4d8e16

* Wed Oct 23 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-122.dev.git792af40
- autobuilt 792af40

* Wed Oct 23 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-121.dev.git8790f24
- autobuilt 8790f24

* Wed Oct 16 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-120.dev.git4e37017
- autobuilt 4e37017

* Sat Oct 05 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-119.dev.gitc1485a1
- autobuilt c1485a1

* Tue Oct 01 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-118.dev.git1b8a1ee
- autobuilt 1b8a1ee

* Mon Sep 30 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-117.dev.gitcad42f6
- autobuilt cad42f6

* Thu Sep 26 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-116.dev.git84373aa
- autobuilt 84373aa

* Thu Sep 26 2019 RH Container Bot <rhcontainerbot@fedoraproject.org> - 2:1.0.0-115.dev.git3e425f8
- autobuilt 3e425f8

* Wed Sep 18 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-114.dev.git7507c64
- autobuilt 7507c64

* Thu Sep 12 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-113.dev.gitbf27c2f
- autobuilt bf27c2f

* Wed Sep 11 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-112.dev.git6c05552
- autobuilt 6c05552

* Tue Sep 10 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-111.dev.git267490e
- autobuilt 267490e

* Tue Sep 10 2019 Jindrich Novy <jnovy@redhat.com> - 2:1.0.0-110.dev.gite7a87dd
- Add versioned oci-runtime provide.

* Mon Sep 09 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-109.dev.gite7a87dd
- autobuilt e7a87dd

* Mon Sep 9 2019 Daniel Walsh <dwalsh@fedoraproject.org> - 2:1.0.0-108.dev.gita6606a7
- Add provides oci-runtime

* Fri Sep 06 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-107.dev.gita6606a7
- autobuilt a6606a7

* Fri Sep 06 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-106.dev.git0fd4342
- autobuilt 0fd4342

* Thu Sep 05 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-105.dev.git92ac8e3
- autobuilt 92ac8e3

* Wed Sep 04 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-104.dev.git92d851e
- autobuilt 92d851e

* Wed Aug 28 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-103.dev.git51f2a86
- autobuilt 51f2a86

* Tue Aug 27 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-102.dev.gitdd07560
- autobuilt dd07560

* Mon Aug 26 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-101.dev.gitc61c737
- autobuilt c61c737

* Mon Aug 26 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-100.dev.git68d73f0
- autobuilt 68d73f0

* Sun Aug 25 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-99.dev.git3525edd
- autobuilt 3525edd

* Mon Aug 05 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-98.dev.git2e94378
- autobuilt 2e94378

* Mon Jul 29 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-97.dev.git80d35c7
- autobuilt 80d35c7

* Sat Jul 27 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-96.dev.git9ae7901
- autobuilt 9ae7901

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:1.0.0-95.dev.git6cccc17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jul 18 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-94.dev.git6cccc17
- autobuilt 6cccc17

* Wed May 15 2019 Daniel Walsh <dwalsh@fedoraproject.org> - 2:1.0.0-93.dev.gitb9b6cc6e
- Fix issue with runc interacting with /dev/stderr

* Wed Apr 24 2019 Daniel Walsh <dwalsh@fedoraproject.org> - 2:1.0.0-92.dev.gitc1b8c57a
- Fix issue with runc failing on SELinux disabled machines

* Fri Apr 19 2019 Daniel Walsh <dwalsh@fedoraproject.org> - 2:1.0.0-91.dev.gitda202113
- Revert Build with nokmem

* Wed Apr 17 2019 Daniel Walsh <dwalsh@fedoraproject.org> - 2:1.0.0-90.dev.gitda202113
- Build with nokmem

* Thu Apr 04 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-89.dev.git029124d
- autobuilt 029124d

* Wed Apr 03 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-88.dev.git6a3f474
- autobuilt 6a3f474

* Thu Mar 28 2019 Daniel Walsh <dwalsh@fedoraproject.org> - 2:1.0.0-87.dev.gitda202113
- release candidate 7

* Sat Mar 23 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-86.dev.git11fc498
- autobuilt 11fc498

* Thu Mar 21 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-85.dev.gitdd22a84
- autobuilt dd22a84

* Sun Mar 17 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-84.dev.gitf56b4cb
- autobuilt f56b4cb

* Sat Mar 16 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-83.dev.git7341c22
- autobuilt 7341c22

* Mon Mar 11 2019 Dan Walsh (Bot) <dwalsh@fedoraproject.org> - 2:1.0.0-82.dev.git2b18fe1
- Change Requires container-selinux to recommends container-selinux

* Fri Mar 08 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-81.dev.git2b18fe1
- autobuilt 2b18fe1

* Wed Mar 06 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-80.dev.git923a8f8
- autobuilt 923a8f8

* Tue Mar 05 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-79.dev.gitf739110
- autobuilt f739110

* Tue Feb 26 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-78.dev.gitf79e211
- autobuilt f79e211

* Sun Feb 24 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-77.dev.git5b5130a
- autobuilt 5b5130a

* Fri Feb 22 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-76.dev.git8084f76
- autobuilt 8084f76

* Sat Feb 16 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-75.dev.git751f18d
- autobuilt 751f18d

* Thu Feb 14 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-74.dev.gitf414f49
- autobuilt f414f49

* Wed Feb 13 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-73.dev.git0a012df
- autobuilt 0a012df

* Tue Feb 12 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-72.dev.git6635b4f
- autobuilt 6635b4f

* Sat Feb 09 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-71.dev.gitdd023c4
- autobuilt dd023c4

* Sat Feb 02 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-70.dev.gite4fa8a4
- autobuilt e4fa8a4

* Sat Jan 26 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-69.dev.git8011af4
- autobuilt 8011af4

* Wed Jan 16 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-68.dev.gitc1e454b
- autobuilt c1e454b

* Tue Jan 15 2019 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-67.dev.git12f6a99
- autobuilt 12f6a99

* Fri Dec 21 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-66.dev.gitbbb17ef
- autobuilt bbb17ef

* Tue Dec 11 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-65.dev.gitf5b9991
- autobuilt f5b9991

* Sun Dec 09 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-64.dev.git859f745
- autobuilt 859f745

* Wed Dec 05 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-63.dev.git25f3f89
- autobuilt 25f3f89

* Tue Dec 04 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-62.dev.git96ec217
- autobuilt 96ec217

* Tue Nov 27 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-61.dev.git4932620
- autobuilt 4932620

* Sun Nov 25 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-60.dev.git9397a6f
- autobuilt 9397a6f

* Sat Nov 24 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-59.dev.gitccb5efd3
- rc6 build

* Wed Nov 07 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-58.dev.git079817c
- autobuilt 079817c

* Thu Nov 01 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-57.dev.git9e5aa74
- built commit 9e5aa74

* Tue Oct 16 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-56.dev.git78ef28e
- built commit 78ef28e
 
* Tue Sep 25 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-55.dev.gitfdd8055
- built commit 578fe65e4fb86b95cc67b304d99d799f976dc40c

* Mon Sep 24 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-54.dev.git00dc700
- built commit 00dc700
- rebase 1807.patch
- enable debuginfo for all versions

* Fri Sep 07 2018 baude <bbaude@redhat.com> - 2:1.0.0-53.dev.git70ca035
- Add BuildRequires git

* Thu Sep 06 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-52.dev.git70ca035
- built commit 70ca035

* Fri Aug 31 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-51.dev.gitfdd8055
- Fix handling of tmpcopyup

* Wed Aug 15 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-50.dev.git20aff4f
- Revert minor cleanup patch

* Tue Aug 7 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-49.dev.gitb4056a4
- Pass GOMAXPROCS to init processes

* Tue Jul 31 2018 Florian Weimer <fweimer@redhat.com> - 2:1.0.0-48.dev.gitbeadf0e
- Rebuild with fixed binutils

* Sun Jul 29 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-47.dev.gitbeadf0e
- autobuilt beadf0e

* Fri Jul 27 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-46.dev.gitb4e2ecb
- Add patch https://github.com/opencontainers/runc/pull/1807 to allow
- runc and podman to work with sd_notify

* Thu Jul 26 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-45.dev.gitb4e2ecb
- autobuilt b4e2ecb

* Wed Jul 25 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-44.dev.gitbc14672
- autobuilt bc14672

* Fri Jul 20 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-43.dev.git21ac086
- Resolves: #1606281 - temp disable debuginfo for rawhide

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2:1.0.0-42.dev.git21ac086
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 11 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-41.dev.git21ac086
- autobuilt 21ac086

* Fri Jul 06 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-40.git45e08f6
- autobuilt 45e08f6

* Tue Jun 26 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-39.git2c632d1
- autobuilt 2c632d1

* Mon Jun 25 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-38.git3ccfa2f
- autobuilt 3ccfa2f

* Sun Jun 24 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-37.git0154d05
- autobuilt 0154d05

* Sat Jun 16 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-36.gitad0f525
- autobuilt ad0f525

* Tue Jun 05 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-35.gitdd56ece
- autobuilt dd56ece

* Sun Jun 03 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-34.git2e91544
- autobuilt 2e91544

* Thu May 31 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-33.gitecd55a4
- autobuilt ecd55a4

* Fri May 25 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-32.gitdd67ab1
- autobuilt dd67ab1

* Fri Apr 27 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-31.git0cbfd83
- autobuilt commit 0cbfd83

* Tue Apr 24 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-30.git871ba2e
- autobuilt commit 871ba2e

* Fri Apr 20 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-29.git1f11dc5
- autobuilt commit 1f11dc5

* Thu Apr 19 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-28.git63e6708
- autobuilt commit 63e6708

* Tue Apr 17 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-27.gitd56f6cc
- autobuilt commit d56f6cc

* Tue Apr 17 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-26.gitd56f6cc
- autobuilt commit d56f6cc

* Mon Apr 16 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-25.gitd56f6cc
- autobuilt commit d56f6cc

* Mon Apr 16 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-24.gitd56f6cc
- autobuilt commit d56f6cc

* Mon Apr 16 2018 Lokesh Mandvekar (Bot) <lsm5+bot@fedoraproject.org> - 2:1.0.0-23.gitf753f30
- autobuilt commit f753f30

* Fri Apr 13 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-22.gitf753f30
- Resolves: #1567229
- built commit f753f30

* Mon Apr 09 2018 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-21.gitcc4307a
- autobuilt commit cc4307a

* Mon Mar 12 2018 Peter Robinson <pbrobinson@fedoraproject.org> 2:1.0.0-20.rc5.git4bb1fe4
- Rebuild for aarch64 install issue

* Tue Feb 27 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-19.rc5.git4bb1fe4
- release v1.0.0~rc5

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2:1.0.0-17.rc4.git9f9c962.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 24 2018 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-17.rc4.git9f9c962
- Bump to the latest from upstream

* Tue Dec 26 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-16.rc4.gite6516b3
- install bash completion to correct location
- remove shebang from bash completion gh#1679
- correct rpmlint issues

* Mon Dec 18 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-15.rc4.gite6516b3
- built commit e6516b3

* Fri Dec 15 2017 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-14.rc4.gitdb093f6
- Lots of fixes for libcontainer
- support unbindable,runbindable for rootfs propagation

* Sun Dec 10 2017 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-13.rc4.git1d3ab6d
- Many Stability fixes
- Many fixes for rootless containers
- Many fixes for static builds

* Wed Oct 25 2017 Dan Walsh <dwalsh@redhat.name> - 2:1.0.0-12.rc4.gitaea4f21
- Add container-selinux prerequires to make sure runc is labeled correctly

* Tue Sep 12 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-11.rc4.gitaea4f21
- disable devel package and %%check - makes life easier for module building

* Tue Sep 5 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.0.0-10.rc4.gitaea4f21
- bump Epoch to 2 since bump to v1.0.1 was in error
- bump to v1.0.0-rc4
- built commit aea4f21

* Tue Sep 5 2017 Dan Walsh <dwalsh@redhat.name> - 1.0.1-4.rc.gitaea4f21
- Rebuilt from master, with requierements needed for CRI-O

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.0.1-3.gitc5ec254
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.0.1-2.gitc5ec254
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 20 2017 Dan Walsh <dwalsh@redhat.name> - 1.0.1-1.gitc5ec25487
- v1.0.0-rc5 release of runc

* Tue Jun 27 2017 Till Maas <opensource@till.name> - 1.0.0-9.git6394544
- Just make the criu dependency optional (https://bugzilla.redhat.com/show_bug.cgi?id=1460148)

* Tue Jun 27 2017 Till Maas <opensource@till.name> - 1.0.0-8.git6394544.1
- Do not build for ix86: there is no criu on ix86

* Fri Jun 02 2017 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.0.0-7.git6394544.1
- rebuilt

* Fri Mar 24 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.0.0-6.git75f8da7
- bump to v1.0.0-rc3
- built opencontainers/v1.0.0-rc3 commit 75f8da7

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.0.0-5.rc2.gitc91b5be.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.0.0-5.rc2
- depend on criu for checkpoint/restore

* Wed Jan 18 2017 Dennis Gilmore <dennis@ausil.us> - 1:1.0.0-4.rc2
- enable aarch64

* Wed Jan 11 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.0.0-3.rc2
- Resolves: #1412238 - *CVE-2016-9962* - set init processes as non-dumpable,
runc patch from Michael Crosby <crosbymichael@gmail.com>

* Fri Jan 06 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.0.0-2.rc2.git47ea5c7
- patch to enable seccomp
- Pass $BUILDTAGS to the compiler in cases where we don't have to define
gobuild for ourselves.
- From: Nalin Dahyabhai <nalin@redhat.com>

* Wed Dec 21 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.0.0-1.rc2.git47ea5c7
- bump to 1.0.0 rc2
- built commit 47ea5c7
- build with bundled sources for now (some new dependencies need to be packaged)

* Wed Aug 24 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.0.0-1.rc1.git04f275d
- Resolves: #1342707 - bump to v1.0.0-rc1
- built commit 04f275d
- cosmetic changes to make rpmlint happy

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.1.1-4.git57b9972
- https://fedoraproject.org/wiki/Changes/golang1.7

* Thu May 26 2016 jchaloup <jchaloup@redhat.com> - 1:0.1.1-3.git57b9972
- Add bash completion
  resolves: #1340119

* Thu May 19 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:0.1.1-2.gitbaf6536
- add selinux to BUILDTAGS in addition to the default seccomp tag

* Tue Apr 26 2016 jchaloup <jchaloup@redhat.com> - 1:0.1.1-0.1.gitbaf6536
- Update to v0.1.1
  resolves: #1330378

* Tue Apr 12 2016 jchaloup <jchaloup@redhat.com> - 1:0.0.9-0.3.git94dc520
- Ship man pages too
  resolves: #1326115

* Wed Apr 06 2016 jchaloup <jchaloup@redhat.com> - 1:0.0.9-0.2.git94dc520
- Extend supported architectures to golang_arches
  Disable failing test
  related: #1290943

* Wed Mar 16 2016 jchaloup <jchaloup@redhat.com> - 1:0.0.9-0.1.git94dc520
- Update to 0.0.9
  resolves: #1290943

* Wed Mar 02 2016 jchaloup <jchaloup@redhat.com> - 1:0.0.8-0.1.git1a124e9
- Update to 0.0.8

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.0.5-0.4.git97bc9a7
- https://fedoraproject.org/wiki/Changes/golang1.6

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.0.5-0.3.git97bc9a7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Dec 02 2015 jchaloup <jchaloup@redhat.com> - 1:0.0.5-0.2.git97bc9a7
- unit-test-devel subpackage requires devel with correct epoch

* Wed Nov 25 2015 jchaloup <jchaloup@redhat.com> - 1:0.0.5-0.1.git97bc9a7
- Update to 0.0.5, introduce Epoch for Fedora due to 0.2 version instead of 0.0.2
  resolves: #1286114

* Fri Aug 21 2015 Jan Chaloupka <jchaloup@redhat.com> - 0.2-0.2.git90e6d37
- First package for Fedora
  resolves: #1255179

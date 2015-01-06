# based on PLD Linux spec git://git.pld-linux.org/packages/python3.git

%bcond_with	tests	# skip tests
# 366 tests OK.
# 3 tests failed:
#     test_distutils test_socket test_strptime
# 15 tests skipped:
#     test_devpoll test_idle test_kqueue test_msilib test_ossaudiodev
#     test_pep277 test_startfile test_tcl test_tk test_ttk_guionly
#     test_ttk_textonly test_unicode_file test_winreg test_winsound
#     test_zipfile64

%define		py_ver		3.4
%define		py_abi		%{py_ver}m

%define		py_prefix	%{_prefix}
%define 	py_libdir	%{py_prefix}/%{_lib}/python%{py_ver}
%define		py_incdir	%{_includedir}/python%{py_abi}
%define		py_sitedir	%{py_libdir}/site-packages
%define		py_dyndir	%{py_libdir}/lib-dynload

Summary:	Very high level scripting language with X interface
Name:		python3
Version:	%{py_ver}.2
Release:	1
Epoch:		1
License:	PSF
Group:		Applications
Source0:	http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz
# Source0-md5:	36fc7327c02c6f12fa24fc9ba78039e3
Patch0:		%{name}-pythonpath.patch
Patch1:		%{name}-opt.patch
Patch2:		%{name}-cflags.patch
Patch3:		%{name}-lib64.patch
Patch4:		%{name}-lib64-regex.patch
Patch5:		%{name}-lib64-fix-for-test_install.patch
Patch6:		%{name}-makefile-location.patch
# from gentoo
Patch7:		%{name}-regenerate-platspec.patch
Patch8:		%{name}-distutils-cxx.patch
Patch9:		%{name}-h2py-encoding.patch
URL:		http://www.python.org/
BuildRequires:	autoconf
BuildRequires:	bzip2-devel
BuildRequires:	db-devel
BuildRequires:	expat-devel
BuildRequires:	file
BuildRequires:	gdbm-devel
BuildRequires:	gmp-devel
BuildRequires:	libffi-devel
BuildRequires:	libstdc++-devel
BuildRequires:	ncurses-ext-devel
BuildRequires:	openssl-devel
BuildRequires:	readline-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	sed
BuildRequires:	sqlite3-devel
BuildRequires:	xz-devel
BuildRequires:	zlib-devel
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Python is an interpreted, interactive, object-oriented programming
language. It incorporates modules, exceptions, dynamic typing, very
high level dynamic data types, and classes. Python combines remarkable
power with very clear syntax. It has interfaces to many system calls
and libraries, as well as to various window systems, and is extensible
in C or C++. It is also usable as an extension language for
applications that need a programmable interface.

%package libs
Summary:	Python library
Group:		Libraries/Python
# broken detection in rpm/pythondeps.sh
Provides:	python(abi) = %{py_ver}
Provides:	python(bytecode) = %{py_ver}

%description libs
Python shared library and very essental modules for Python binary.

%package modules
Summary:	Python modules
Group:		Libraries/Python
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}

%description modules
Python officially distributed modules.

%package pydoc3
Summary:	Python interactive module documentation access support
Group:		Applications
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}

%description pydoc3
Python interactive module documentation access support.

%package idle3
Summary:	IDE for Python language
Group:		Applications
Requires:	%{name}-tkinter = %{epoch}:%{version}-%{release}

%description idle3
IDE for Python language.

%package devel
Summary:	Libraries and header files for building python code
Group:		Development/Languages/Python
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}

%description devel
The Python interpreter is relatively easy to extend with dynamically
loaded extensions and to embed in other programs. This package
contains the header files and libraries which are needed to do both of
these tasks.

%package devel-tools
Summary:	Python development tools
Group:		Development/Languages/Python
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}

%description devel-tools
Python development tools such as profilers and debugger.

%package tkinter
Summary:	Standard Python interface to the Tk GUI toolkit
Group:		Libraries/Python
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}
Requires:	tix
Requires:	tk

%description tkinter
Standard Python interface to the Tk GUI toolkit.

%prep
%setup -qn Python-%{version}

%{__rm} -r Modules/{expat,zlib,_ctypes/{darwin,libffi*}}

find . -name '*.py' | xargs -r grep -El '^#! */usr/bin/env python3?' | \
    xargs %{__sed} -i -e '1s,^#! */usr/bin/env python3\?,#!/usr/bin/python3,'

%patch0 -p1
%patch1 -p1
%patch2 -p1
%if %{_lib} == "lib64"
%patch3 -p1
%patch4 -p1
%patch5 -p1
%endif
%patch6 -p1
#
%patch7 -p0
%patch8 -p0
%patch9 -p0

%build
%{__aclocal}
%{__autoconf}
%configure \
	ac_cv_posix_semaphores_enabled=yes	\
	ac_cv_broken_sem_getvalue=no		\
	--enable-ipv6				\
	--enable-shared				\
	--with-computed-gotos			\
	--with-cxx-main="%{__cxx}"		\
	--with-dbmliborder=gdbm:bdb		\
	--with-system-expat			\
	--with-system-ffi			\
	--with-threads				\
	--without-ensurepip			\
	BLDSHARED='$(CC) $(CFLAGS) -shared'	\
	LDFLAGS="%{rpmcflags} %{rpmldflags}"	\
	LDSHARED='$(CC) $(CFLAGS) -shared'	\
	LINKCC='$(PURIFY) $(CXX)'

%{__make} 2>&1 | awk '
BEGIN { fail = 0; logmsg = ""; }
{
		if ($0 ~ /\*\*\* WARNING:/) {
				fail = 1;
				logmsg = logmsg $0;
		}
		print $0;
}
END { if (fail) { print "\nPROBLEMS FOUND:"; print logmsg; exit(1); } }'

%install
rm -rf $RPM_BUILD_ROOT
install -d \
	$RPM_BUILD_ROOT%{py_sitedir}/__pycache__	\
	$RPM_BUILD_ROOT%{py_sitescriptdir}/__pycache__

# workaround short-circuit problems
rm -f *.pc

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# make libpython3.so simply symlink to real lib
ln -sf libpython%{py_abi}.so $RPM_BUILD_ROOT%{_libdir}/libpython3.so

ln -s python-%{py_ver}.pc $RPM_BUILD_ROOT%{_pkgconfigdir}/python3.pc
ln -s python-%{py_ver}.pc $RPM_BUILD_ROOT%{_pkgconfigdir}/python-%{py_abi}.pc

# xgettext specific for Python code
#
# we will have two commands: pygettext.py (an alias) and pygettext;
# this way there are no import (which is impossible now) conflicts and
# pygettext.py is provided for compatibility
install -p Tools/i18n/pygettext.py $RPM_BUILD_ROOT%{_bindir}/pygettext%{py_ver}

# reindent python code
install -p Tools/scripts/reindent.py $RPM_BUILD_ROOT%{_bindir}/pyreindent%{py_ver}

# just to cut the noise, as they are not packaged (now)
# first tests (probably could be packaged)
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/ctypes/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/distutils/tests
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/lib2to3/tests
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/sqlite3/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/tkinter/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/unittest/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/idlelib/idle_test

# other files
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/plat-*/regen
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/ctypes/macholib/fetch_macholib*
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/site-packages/README
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/distutils/command/wininst*.exe
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/idlelib/*.bat
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/idlelib/*.pyw

# currently provided by python-2to3, consider switching to this one
%{__rm} $RPM_BUILD_ROOT%{_bindir}/2to3

# that seems to be only an empty extension template,
# which seems to be built only {with tests}
%{__rm} -f $RPM_BUILD_ROOT%{py_dyndir}/xxlimited.*.so

# already in %%doc
%{__rm} $RPM_BUILD_ROOT%{py_scriptdir}/LICENSE.txt

%if %{with tests}
%check
export LC_ALL=C
export TERM=screen
LD_LIBRARY_PATH=$(pwd) ./python -m test.regrtest -uall -x test_posixpath test_uuid test_site test_urllib2_localnet test_gdb
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/python%{py_ver}
%attr(755,root,root) %{_bindir}/python%{py_abi}
%attr(755,root,root) %{_bindir}/python3
%attr(755,root,root) %{_bindir}/pyvenv
%attr(755,root,root) %{_bindir}/pyvenv-%{py_ver}
%{_mandir}/man1/python*.1*

%files libs
%defattr(644,root,root,755)
%doc LICENSE
%attr(755,root,root) %{_libdir}/libpython%{py_abi}.so.*.*

%dir %{py_incdir}
%{py_incdir}/pyconfig.h

%dir %{py_libdir}
%dir %{py_dyndir}
%dir %{py_sitedir}
%dir %{py_sitedir}/__pycache__
%dir %{py_scriptdir}
%dir %{py_scriptdir}/__pycache__
%dir %{py_sitescriptdir}
%dir %{py_sitescriptdir}/__pycache__

# shared modules required by python library
%attr(755,root,root) %{py_dyndir}/_struct.cpython-*.so

# modules required by python library
%{py_scriptdir}/_collections_abc.py
%{py_scriptdir}/_sitebuiltins.py
%{py_scriptdir}/_sysconfigdata.py
%{py_scriptdir}/_weakrefset.py
%{py_scriptdir}/abc.py
%{py_scriptdir}/bisect.py
%{py_scriptdir}/codecs.py
%{py_scriptdir}/copyreg.py
%{py_scriptdir}/functools.py
%{py_scriptdir}/genericpath.py
%{py_scriptdir}/heapq.py
%{py_scriptdir}/io.py
%{py_scriptdir}/keyword.py
%{py_scriptdir}/linecache.py
%{py_scriptdir}/locale.py
%{py_scriptdir}/os.py
%{py_scriptdir}/posixpath.py
%{py_scriptdir}/re.py
%{py_scriptdir}/reprlib.py
%{py_scriptdir}/site.py
%{py_scriptdir}/sre_*.py
%{py_scriptdir}/stat.py
%{py_scriptdir}/sysconfig.py
%{py_scriptdir}/token.py
%{py_scriptdir}/tokenize.py
%{py_scriptdir}/traceback.py
%{py_scriptdir}/weakref.py
# needed by the dynamic sys.lib patch
%{py_scriptdir}/__pycache__/_collections_abc.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_sitebuiltins.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_sysconfigdata.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_weakrefset.cpython-*.py[co]
%{py_scriptdir}/__pycache__/abc.cpython-*.py[co]
%{py_scriptdir}/__pycache__/bisect.cpython-*.py[co]
%{py_scriptdir}/__pycache__/codecs.cpython-*.py[co]
%{py_scriptdir}/__pycache__/copyreg.cpython-*.py[co]
%{py_scriptdir}/__pycache__/functools.cpython-*.py[co]
%{py_scriptdir}/__pycache__/genericpath.cpython-*.py[co]
%{py_scriptdir}/__pycache__/heapq.cpython-*.py[co]
%{py_scriptdir}/__pycache__/io.cpython-*.py[co]
%{py_scriptdir}/__pycache__/keyword.cpython-*.py[co]
%{py_scriptdir}/__pycache__/linecache.cpython-*.py[co]
%{py_scriptdir}/__pycache__/locale.cpython-*.py[co]
%{py_scriptdir}/__pycache__/os.cpython-*.py[co]
%{py_scriptdir}/__pycache__/posixpath.cpython-*.py[co]
%{py_scriptdir}/__pycache__/re.cpython-*.py[co]
%{py_scriptdir}/__pycache__/reprlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/site.cpython-*.py[co]
%{py_scriptdir}/__pycache__/sre_*.cpython-*.py[co]
%{py_scriptdir}/__pycache__/stat.cpython-*.py[co]
%{py_scriptdir}/__pycache__/sysconfig.cpython-*.py[co]
%{py_scriptdir}/__pycache__/token.cpython-*.py[co]
%{py_scriptdir}/__pycache__/tokenize.cpython-*.py[co]
%{py_scriptdir}/__pycache__/traceback.cpython-*.py[co]
%{py_scriptdir}/__pycache__/types.cpython-*.py[co]
%{py_scriptdir}/__pycache__/weakref.cpython-*.py[co]
%{py_scriptdir}/types.py

%{py_scriptdir}/collections

# encodings required by python library
%dir %{py_scriptdir}/encodings
%{py_scriptdir}/encodings/__pycache__
%{py_scriptdir}/encodings/*.py

%dir %{py_libdir}/config-%{py_abi}
%{py_libdir}/config-%{py_abi}/Makefile
%{py_libdir}/config-%{py_abi}/Setup
%{py_libdir}/config-%{py_abi}/Setup.config
%{py_libdir}/config-%{py_abi}/Setup.local

%files modules
%defattr(644,root,root,755)
%{py_scriptdir}/__future__.py
%{py_scriptdir}/__phello__.foo.py
%{py_scriptdir}/_bootlocale.py
%{py_scriptdir}/_compat_pickle.py
%{py_scriptdir}/_dummy_thread.py
%{py_scriptdir}/_markupbase.py
%{py_scriptdir}/_osx_support.py
%{py_scriptdir}/_pyio.py
%{py_scriptdir}/_strptime.py
%{py_scriptdir}/_threading_local.py
%{py_scriptdir}/aifc.py
%{py_scriptdir}/antigravity.py
%{py_scriptdir}/argparse.py
%{py_scriptdir}/ast.py
%{py_scriptdir}/asynchat.py
%{py_scriptdir}/asyncore.py
%{py_scriptdir}/base64.py
%{py_scriptdir}/bdb.py
%{py_scriptdir}/binhex.py
%{py_scriptdir}/bz2.py
%{py_scriptdir}/cProfile.py
%{py_scriptdir}/calendar.py
%{py_scriptdir}/cgi.py
%{py_scriptdir}/cgitb.py
%{py_scriptdir}/chunk.py
%{py_scriptdir}/cmd.py
%{py_scriptdir}/code.py
%{py_scriptdir}/codeop.py
%{py_scriptdir}/colorsys.py
%{py_scriptdir}/compileall.py
%{py_scriptdir}/configparser.py
%{py_scriptdir}/contextlib.py
%{py_scriptdir}/copy.py
%{py_scriptdir}/crypt.py
%{py_scriptdir}/csv.py
%{py_scriptdir}/datetime.py
%{py_scriptdir}/decimal.py
%{py_scriptdir}/difflib.py
%{py_scriptdir}/dis.py
%{py_scriptdir}/doctest.py
%{py_scriptdir}/dummy_threading.py
%{py_scriptdir}/enum.py
%{py_scriptdir}/filecmp.py
%{py_scriptdir}/fileinput.py
%{py_scriptdir}/fnmatch.py
%{py_scriptdir}/formatter.py
%{py_scriptdir}/fractions.py
%{py_scriptdir}/ftplib.py
%{py_scriptdir}/getopt.py
%{py_scriptdir}/getpass.py
%{py_scriptdir}/gettext.py
%{py_scriptdir}/glob.py
%{py_scriptdir}/gzip.py
%{py_scriptdir}/hashlib.py
%{py_scriptdir}/hmac.py
%{py_scriptdir}/imaplib.py
%{py_scriptdir}/imghdr.py
%{py_scriptdir}/imp.py
%{py_scriptdir}/inspect.py
%{py_scriptdir}/ipaddress.py
%{py_scriptdir}/lzma.py
%{py_scriptdir}/macpath.py
%{py_scriptdir}/macurl2path.py
%{py_scriptdir}/mailbox.py
%{py_scriptdir}/mailcap.py
%{py_scriptdir}/mimetypes.py
%{py_scriptdir}/modulefinder.py
%{py_scriptdir}/netrc.py
%{py_scriptdir}/nntplib.py
%{py_scriptdir}/ntpath.py
%{py_scriptdir}/nturl2path.py
%{py_scriptdir}/numbers.py
%{py_scriptdir}/opcode.py
%{py_scriptdir}/operator.py
%{py_scriptdir}/optparse.py
%{py_scriptdir}/pathlib.py
%{py_scriptdir}/pickle.py
%{py_scriptdir}/pickletools.py
%{py_scriptdir}/pipes.py
%{py_scriptdir}/pkgutil.py
%{py_scriptdir}/platform.py
%{py_scriptdir}/plistlib.py
%{py_scriptdir}/poplib.py
%{py_scriptdir}/pprint.py
%{py_scriptdir}/pty.py
%{py_scriptdir}/py_compile.py
%{py_scriptdir}/pyclbr.py
%{py_scriptdir}/queue.py
%{py_scriptdir}/quopri.py
%{py_scriptdir}/random.py
%{py_scriptdir}/rlcompleter.py
%{py_scriptdir}/runpy.py
%{py_scriptdir}/sched.py
%{py_scriptdir}/selectors.py
%{py_scriptdir}/shelve.py
%{py_scriptdir}/shlex.py
%{py_scriptdir}/shutil.py
%{py_scriptdir}/smtpd.py
%{py_scriptdir}/smtplib.py
%{py_scriptdir}/sndhdr.py
%{py_scriptdir}/socket.py
%{py_scriptdir}/socketserver.py
%{py_scriptdir}/ssl.py
%{py_scriptdir}/statistics.py
%{py_scriptdir}/string.py
%{py_scriptdir}/stringprep.py
%{py_scriptdir}/struct.py
%{py_scriptdir}/subprocess.py
%{py_scriptdir}/sunau.py
%{py_scriptdir}/symbol.py
%{py_scriptdir}/symtable.py
%{py_scriptdir}/tabnanny.py
%{py_scriptdir}/tarfile.py
%{py_scriptdir}/telnetlib.py
%{py_scriptdir}/tempfile.py
%{py_scriptdir}/textwrap.py
%{py_scriptdir}/this.py
%{py_scriptdir}/threading.py
%{py_scriptdir}/trace.py
%{py_scriptdir}/tracemalloc.py
%{py_scriptdir}/tty.py
%{py_scriptdir}/turtle.py
%{py_scriptdir}/uu.py
%{py_scriptdir}/uuid.py
%{py_scriptdir}/warnings.py
%{py_scriptdir}/wave.py
%{py_scriptdir}/webbrowser.py
%{py_scriptdir}/xdrlib.py
%{py_scriptdir}/zipfile.py

%{py_scriptdir}/__pycache__/__future__.cpython-*.py[co]
%{py_scriptdir}/__pycache__/__phello__.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_bootlocale.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_compat_pickle.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_dummy_thread.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_markupbase.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_osx_support.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_pyio.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_strptime.cpython-*.py[co]
%{py_scriptdir}/__pycache__/_threading_local.cpython-*.py[co]
%{py_scriptdir}/__pycache__/aifc.cpython-*.py[co]
%{py_scriptdir}/__pycache__/antigravity.cpython-*.py[co]
%{py_scriptdir}/__pycache__/argparse.cpython-*.py[co]
%{py_scriptdir}/__pycache__/ast.cpython-*.py[co]
%{py_scriptdir}/__pycache__/asynchat.cpython-*.py[co]
%{py_scriptdir}/__pycache__/asyncore.cpython-*.py[co]
%{py_scriptdir}/__pycache__/base64.cpython-*.py[co]
%{py_scriptdir}/__pycache__/bdb.cpython-*.py[co]
%{py_scriptdir}/__pycache__/binhex.cpython-*.py[co]
%{py_scriptdir}/__pycache__/bz2.cpython-*.py[co]
%{py_scriptdir}/__pycache__/cProfile.cpython-*.py[co]
%{py_scriptdir}/__pycache__/calendar.cpython-*.py[co]
%{py_scriptdir}/__pycache__/cgi.cpython-*.py[co]
%{py_scriptdir}/__pycache__/cgitb.cpython-*.py[co]
%{py_scriptdir}/__pycache__/chunk.cpython-*.py[co]
%{py_scriptdir}/__pycache__/cmd.cpython-*.py[co]
%{py_scriptdir}/__pycache__/code.cpython-*.py[co]
%{py_scriptdir}/__pycache__/codeop.cpython-*.py[co]
%{py_scriptdir}/__pycache__/colorsys.cpython-*.py[co]
%{py_scriptdir}/__pycache__/compileall.cpython-*.py[co]
%{py_scriptdir}/__pycache__/configparser.cpython-*.py[co]
%{py_scriptdir}/__pycache__/contextlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/copy.cpython-*.py[co]
%{py_scriptdir}/__pycache__/crypt.cpython-*.py[co]
%{py_scriptdir}/__pycache__/csv.cpython-*.py[co]
%{py_scriptdir}/__pycache__/datetime.cpython-*.py[co]
%{py_scriptdir}/__pycache__/decimal.cpython-*.py[co]
%{py_scriptdir}/__pycache__/difflib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/dis.cpython-*.py[co]
%{py_scriptdir}/__pycache__/doctest.cpython-*.py[co]
%{py_scriptdir}/__pycache__/dummy_threading.cpython-*.py[co]
%{py_scriptdir}/__pycache__/enum.cpython-*.py[co]
%{py_scriptdir}/__pycache__/filecmp.cpython-*.py[co]
%{py_scriptdir}/__pycache__/fileinput.cpython-*.py[co]
%{py_scriptdir}/__pycache__/fnmatch.cpython-*.py[co]
%{py_scriptdir}/__pycache__/formatter.cpython-*.py[co]
%{py_scriptdir}/__pycache__/fractions.cpython-*.py[co]
%{py_scriptdir}/__pycache__/ftplib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/getopt.cpython-*.py[co]
%{py_scriptdir}/__pycache__/getpass.cpython-*.py[co]
%{py_scriptdir}/__pycache__/gettext.cpython-*.py[co]
%{py_scriptdir}/__pycache__/glob.cpython-*.py[co]
%{py_scriptdir}/__pycache__/gzip.cpython-*.py[co]
%{py_scriptdir}/__pycache__/hashlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/hmac.cpython-*.py[co]
%{py_scriptdir}/__pycache__/imaplib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/imghdr.cpython-*.py[co]
%{py_scriptdir}/__pycache__/imp.cpython-*.py[co]
%{py_scriptdir}/__pycache__/inspect.cpython-*.py[co]
%{py_scriptdir}/__pycache__/ipaddress.cpython-*.py[co]
%{py_scriptdir}/__pycache__/lzma.cpython-*.py[co]
%{py_scriptdir}/__pycache__/macpath.cpython-*.py[co]
%{py_scriptdir}/__pycache__/macurl2path.cpython-*.py[co]
%{py_scriptdir}/__pycache__/mailbox.cpython-*.py[co]
%{py_scriptdir}/__pycache__/mailcap.cpython-*.py[co]
%{py_scriptdir}/__pycache__/mimetypes.cpython-*.py[co]
%{py_scriptdir}/__pycache__/modulefinder.cpython-*.py[co]
%{py_scriptdir}/__pycache__/netrc.cpython-*.py[co]
%{py_scriptdir}/__pycache__/nntplib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/ntpath.cpython-*.py[co]
%{py_scriptdir}/__pycache__/nturl2path.cpython-*.py[co]
%{py_scriptdir}/__pycache__/numbers.cpython-*.py[co]
%{py_scriptdir}/__pycache__/opcode.cpython-*.py[co]
%{py_scriptdir}/__pycache__/operator.cpython-*.py[co]
%{py_scriptdir}/__pycache__/optparse.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pathlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pickle.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pickletools.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pipes.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pkgutil.cpython-*.py[co]
%{py_scriptdir}/__pycache__/platform.cpython-*.py[co]
%{py_scriptdir}/__pycache__/plistlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/poplib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pprint.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pty.cpython-*.py[co]
%{py_scriptdir}/__pycache__/py_compile.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pyclbr.cpython-*.py[co]
%{py_scriptdir}/__pycache__/queue.cpython-*.py[co]
%{py_scriptdir}/__pycache__/quopri.cpython-*.py[co]
%{py_scriptdir}/__pycache__/random.cpython-*.py[co]
%{py_scriptdir}/__pycache__/rlcompleter.cpython-*.py[co]
%{py_scriptdir}/__pycache__/runpy.cpython-*.py[co]
%{py_scriptdir}/__pycache__/sched.cpython-*.py[co]
%{py_scriptdir}/__pycache__/selectors.cpython-*.py[co]
%{py_scriptdir}/__pycache__/shelve.cpython-*.py[co]
%{py_scriptdir}/__pycache__/shlex.cpython-*.py[co]
%{py_scriptdir}/__pycache__/shutil.cpython-*.py[co]
%{py_scriptdir}/__pycache__/smtpd.cpython-*.py[co]
%{py_scriptdir}/__pycache__/smtplib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/sndhdr.cpython-*.py[co]
%{py_scriptdir}/__pycache__/socket.cpython-*.py[co]
%{py_scriptdir}/__pycache__/socketserver.cpython-*.py[co]
%{py_scriptdir}/__pycache__/ssl.cpython-*.py[co]
%{py_scriptdir}/__pycache__/statistics.cpython-*.py[co]
%{py_scriptdir}/__pycache__/string.cpython-*.py[co]
%{py_scriptdir}/__pycache__/stringprep.cpython-*.py[co]
%{py_scriptdir}/__pycache__/struct.cpython-*.py[co]
%{py_scriptdir}/__pycache__/subprocess.cpython-*.py[co]
%{py_scriptdir}/__pycache__/sunau.cpython-*.py[co]
%{py_scriptdir}/__pycache__/symbol.cpython-*.py[co]
%{py_scriptdir}/__pycache__/symtable.cpython-*.py[co]
%{py_scriptdir}/__pycache__/tabnanny.cpython-*.py[co]
%{py_scriptdir}/__pycache__/tarfile.cpython-*.py[co]
%{py_scriptdir}/__pycache__/telnetlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/tempfile.cpython-*.py[co]
%{py_scriptdir}/__pycache__/textwrap.cpython-*.py[co]
%{py_scriptdir}/__pycache__/this.cpython-*.py[co]
%{py_scriptdir}/__pycache__/threading.cpython-*.py[co]
%{py_scriptdir}/__pycache__/trace.cpython-*.py[co]
%{py_scriptdir}/__pycache__/tracemalloc.cpython-*.py[co]
%{py_scriptdir}/__pycache__/tty.cpython-*.py[co]
%{py_scriptdir}/__pycache__/turtle.cpython-*.py[co]
%{py_scriptdir}/__pycache__/uu.cpython-*.py[co]
%{py_scriptdir}/__pycache__/uuid.cpython-*.py[co]
%{py_scriptdir}/__pycache__/warnings.cpython-*.py[co]
%{py_scriptdir}/__pycache__/wave.cpython-*.py[co]
%{py_scriptdir}/__pycache__/webbrowser.cpython-*.py[co]
%{py_scriptdir}/__pycache__/xdrlib.cpython-*.py[co]
%{py_scriptdir}/__pycache__/zipfile.cpython-*.py[co]

# list .so modules to be sure that all of them are built

%attr(755,root,root) %{py_dyndir}/_bisect.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_bz2.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_codecs_cn.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_codecs_hk.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_codecs_iso2022.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_codecs_jp.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_codecs_kr.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_codecs_tw.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_crypt.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_csv.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_ctypes*.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_curses.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_curses_panel.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_datetime.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_dbm.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_decimal.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_elementtree.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_gdbm.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_hashlib.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_heapq.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_json.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_lsprof.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_lzma.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_md5.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_multibytecodec.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_multiprocessing.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_opcode.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_pickle.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_posixsubprocess.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_random.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_sha1.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_sha256.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_sha512.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_socket.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_ssl.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_testbuffer.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_testcapi.cpython-*.so
%attr(755,root,root) %{py_dyndir}/_testimportmultiple.cpython-*.so

%attr(755,root,root) %{py_dyndir}/array.cpython-*.so
%attr(755,root,root) %{py_dyndir}/audioop.cpython-*.so
%attr(755,root,root) %{py_dyndir}/binascii.cpython-*.so
%attr(755,root,root) %{py_dyndir}/cmath.cpython-*.so
%attr(755,root,root) %{py_dyndir}/fcntl.cpython-*.so
%attr(755,root,root) %{py_dyndir}/grp.cpython-*.so
%attr(755,root,root) %{py_dyndir}/math.cpython-*.so
%attr(755,root,root) %{py_dyndir}/mmap.cpython-*.so
%attr(755,root,root) %{py_dyndir}/nis.cpython-*.so
%attr(755,root,root) %{py_dyndir}/ossaudiodev.cpython-*.so
%attr(755,root,root) %{py_dyndir}/parser.cpython-*.so
%attr(755,root,root) %{py_dyndir}/pyexpat.cpython-*.so
%attr(755,root,root) %{py_dyndir}/readline.cpython-*.so
%attr(755,root,root) %{py_dyndir}/resource.cpython-*.so
%attr(755,root,root) %{py_dyndir}/select.cpython-*.so
%attr(755,root,root) %{py_dyndir}/spwd.cpython-*.so
%attr(755,root,root) %{py_dyndir}/syslog.cpython-*.so
%attr(755,root,root) %{py_dyndir}/termios.cpython-*.so
%attr(755,root,root) %{py_dyndir}/time.cpython-*.so
%attr(755,root,root) %{py_dyndir}/unicodedata.cpython-*.so
%attr(755,root,root) %{py_dyndir}/zlib.cpython-*.so

%dir %{py_scriptdir}/asyncio
%{py_scriptdir}/asyncio/__pycache__
%{py_scriptdir}/asyncio/*.py

%{py_scriptdir}/concurrent

%dir %{py_scriptdir}/ctypes
%dir %{py_scriptdir}/ctypes/macholib
%{py_scriptdir}/ctypes/__pycache__
%{py_scriptdir}/ctypes/macholib/__pycache__

%{py_scriptdir}/ctypes/*.py
%{py_scriptdir}/ctypes/macholib/*.py
%doc %{py_scriptdir}/ctypes/macholib/README.ctypes

%dir %{py_scriptdir}/curses
%{py_scriptdir}/curses/__pycache__
%{py_scriptdir}/curses/*.py

%dir %{py_scriptdir}/dbm
%{py_scriptdir}/dbm/__pycache__
%{py_scriptdir}/dbm/*.py

%dir %{py_scriptdir}/distutils
%dir %{py_scriptdir}/distutils/command
%doc %{py_scriptdir}/distutils/README
%{py_scriptdir}/distutils/__pycache__
%{py_scriptdir}/distutils/command/__pycache__
%{py_scriptdir}/distutils/*.py
%{py_scriptdir}/distutils/command/*.py
%{py_scriptdir}/distutils/command/command_template

%dir %{py_scriptdir}/email
%dir %{py_scriptdir}/email/mime
%{py_scriptdir}/email/*.py
%{py_scriptdir}/email/__pycache__
%{py_scriptdir}/email/architecture.rst
%{py_scriptdir}/email/mime/*.py
%{py_scriptdir}/email/mime/__pycache__

%dir %{py_scriptdir}/ensurepip
%{py_scriptdir}/ensurepip/__pycache__
%{py_scriptdir}/ensurepip/*.py
%{py_scriptdir}/ensurepip/_bundled

%dir %{py_scriptdir}/html
%{py_scriptdir}/html/*.py
%{py_scriptdir}/html/__pycache__

%dir %{py_scriptdir}/http
%{py_scriptdir}/http/__pycache__
%{py_scriptdir}/http/*.py

%dir %{py_scriptdir}/idlelib

%dir %{py_scriptdir}/importlib
%{py_scriptdir}/importlib/__pycache__
%{py_scriptdir}/importlib/*.py

%dir %{py_scriptdir}/json
%{py_scriptdir}/json/__pycache__
%{py_scriptdir}/json/*.py

%dir %{py_scriptdir}/logging
%{py_scriptdir}/logging/__pycache__
%{py_scriptdir}/logging/*.py

%dir %{py_scriptdir}/multiprocessing
%{py_scriptdir}/multiprocessing/__pycache__
%{py_scriptdir}/multiprocessing/*.py
%dir %{py_scriptdir}/multiprocessing/dummy
%{py_scriptdir}/multiprocessing/dummy/__pycache__
%{py_scriptdir}/multiprocessing/dummy/*.py

%dir %{py_scriptdir}/plat-*
%{py_scriptdir}/plat-*/__pycache__
%{py_scriptdir}/plat-*/*.py

%{py_scriptdir}/turtledemo

%dir %{py_scriptdir}/unittest
%{py_scriptdir}/unittest/__pycache__
%{py_scriptdir}/unittest/*.py

%dir %{py_scriptdir}/urllib
%{py_scriptdir}/urllib/__pycache__
%{py_scriptdir}/urllib/*.py

%dir %{py_scriptdir}/venv
%dir %{py_scriptdir}/venv/scripts
%{py_scriptdir}/venv/*.py
%{py_scriptdir}/venv/__pycache__
%dir %{py_scriptdir}/venv/scripts/posix
%{py_scriptdir}/venv/scripts/posix/activate

%dir %{py_scriptdir}/wsgiref
%{py_scriptdir}/wsgiref/__pycache__
%{py_scriptdir}/wsgiref/*.py

%dir %{py_scriptdir}/xml
%dir %{py_scriptdir}/xml/dom
%dir %{py_scriptdir}/xml/etree
%dir %{py_scriptdir}/xml/parsers
%dir %{py_scriptdir}/xml/sax
%{py_scriptdir}/xml/__pycache__
%{py_scriptdir}/xml/dom/__pycache__
%{py_scriptdir}/xml/etree/__pycache__
%{py_scriptdir}/xml/parsers/__pycache__
%{py_scriptdir}/xml/sax/__pycache__
%{py_scriptdir}/xml/*.py
%{py_scriptdir}/xml/dom/*.py
%{py_scriptdir}/xml/etree/*.py
%{py_scriptdir}/xml/parsers/*.py
%{py_scriptdir}/xml/sax/*.py

%dir %{py_scriptdir}/xmlrpc
%{py_scriptdir}/xmlrpc/__pycache__
%{py_scriptdir}/xmlrpc/*.py

%attr(755,root,root) %{py_dyndir}/_sqlite3.cpython-*.so
%dir %{py_scriptdir}/sqlite3
%{py_scriptdir}/sqlite3/__pycache__
%{py_scriptdir}/sqlite3/*.py

%files pydoc3
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/pydoc3
%attr(755,root,root) %{_bindir}/pydoc%{py_ver}
%{py_scriptdir}/pydoc.py
%{py_scriptdir}/__pycache__/pydoc.cpython-*.py[co]
%dir %{py_scriptdir}/pydoc_data
%{py_scriptdir}/pydoc_data/__pycache__
%{py_scriptdir}/pydoc_data/*.py
%{py_scriptdir}/pydoc_data/*.css

%files idle3
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/idle3
%attr(755,root,root) %{_bindir}/idle%{py_ver}
%dir %{py_scriptdir}/idlelib/Icons
%{py_scriptdir}/idlelib/__pycache__
%{py_scriptdir}/idlelib/*.py
%doc %{py_scriptdir}/idlelib/*.txt
%doc %{py_scriptdir}/idlelib/ChangeLog
%{py_scriptdir}/idlelib/Icons/*
%{py_scriptdir}/idlelib/*.def

%files devel
%defattr(644,root,root,755)
%doc Misc/{ACKS,NEWS,README,README.valgrind,valgrind-python.supp}
%attr(755,root,root) %{_bindir}/python%{py_abi}-config
%attr(755,root,root) %{_bindir}/python%{py_ver}-config
%attr(755,root,root) %{_bindir}/python3-config
%attr(755,root,root) %{_libdir}/libpython%{py_abi}.so
%attr(755,root,root) %{_libdir}/libpython3.so
%{py_incdir}/*.h
%exclude %{py_incdir}/pyconfig.h
%attr(755,root,root) %{py_libdir}/config-%{py_abi}/makesetup
%attr(755,root,root) %{py_libdir}/config-%{py_abi}/install-sh
%{py_libdir}/config-%{py_abi}/config.c
%{py_libdir}/config-%{py_abi}/config.c.in
%{py_libdir}/config-%{py_abi}/python.o
%{py_libdir}/config-%{py_abi}/python-config.py
%{_pkgconfigdir}/python-%{py_ver}.pc
%{_pkgconfigdir}/python-%{py_abi}.pc
%{_pkgconfigdir}/python3.pc

%files devel-tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/pygettext%{py_ver}
%attr(755,root,root) %{_bindir}/pyreindent%{py_ver}
%{py_scriptdir}/pdb.py
%{py_scriptdir}/profile.py
%{py_scriptdir}/pstats.py
%{py_scriptdir}/timeit.py
%{py_scriptdir}/__pycache__/pdb.cpython-*.py[co]
%{py_scriptdir}/__pycache__/profile.cpython-*.py[co]
%{py_scriptdir}/__pycache__/pstats.cpython-*.py[co]
%{py_scriptdir}/__pycache__/timeit.cpython-*.py[co]

# 2to3
%dir %{py_scriptdir}/lib2to3
%dir %{py_scriptdir}/lib2to3/fixes
%dir %{py_scriptdir}/lib2to3/pgen2
%{_bindir}/2to3-%{py_ver}
%{py_scriptdir}/lib2to3/*.pickle
%{py_scriptdir}/lib2to3/*.py
%{py_scriptdir}/lib2to3/*.txt
%{py_scriptdir}/lib2to3/__pycache__
%{py_scriptdir}/lib2to3/fixes/*.py
%{py_scriptdir}/lib2to3/fixes/__pycache__
%{py_scriptdir}/lib2to3/pgen2/*.py
%{py_scriptdir}/lib2to3/pgen2/__pycache__

%files tkinter
%defattr(644,root,root,755)
%dir %{py_scriptdir}/tkinter
%{py_scriptdir}/tkinter/__pycache__
%{py_scriptdir}/tkinter/*.py
#%attr(755,root,root) %{py_dyndir}/_tkinter.cpython-*.so


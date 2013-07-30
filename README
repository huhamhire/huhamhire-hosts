Hosts Setup Utility
===================



Introduction
------------

Due to the Chinese government is using the GFW blocking the web access to some
world famous sites like Googel+, twitter, Facebook, and Wikipedia etc., we
made this hosts tool to help people to get through the Great Firewall.

Hosts Setup Utility provides basic tools to manage the hosts file on operating
systems with a desktop environment. Users could use these tool to modify the
hosts file in order to visit specified websites blocked by Chinese government.
Tools for users to backup/restore hosts files is also provided.

The home page of this project is <https://hosts.huhamhire.com/>.

You can also visit the project page on Google Code to get our latest news
<http://code.google.com/p/huhamhire-hosts/>.


License
-------

Licensed under the GNU General Public License, version 3. You should
have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.


Usage
-----

* Windows(x86/x64): run hostsutl.exe from the binary excutables package to get
        started.

        - "Run as Administrator" is needed for operations to change the hosts
          file on Windows Vista or newer.

* Mac OS X: run HostsUtl application from the binary excutables package to get
        started.

        - Because of the locale problem with py2app, the automatic language
          selection may not work correctly on Mac OS with binary excutables.
          You can just choose the language on your on choice.

* Linux/X11(Source code): run command "python hostsutl.py" to get started.

        - All platforms with python and the PyQT4 extension could use this
        - method to run the source code.
        - A desktop environment with QT and python is needed only for
          Linux/X11 users.
        - "sudo" is needed for operations to change the hosts file.

(Note if the programe is not running with privileges to modify the hosts file,
a warning message would be shown and you could only do operations like backup
hosts file and update the local data file.)


Requirements
------------

* Microsoft Windows 2000 or newer for Windows users.

* Mac OS X 10.6 or newer for Macintosh users.

* Linux/X11 desktop with QT for Linux/X11 users.

* Python 2.6/2.7 with PyQT4 extension for develop.

* py2exe or py2app would be required while making binary excutables for
        specified platforms.


Available Modules
-----------------

* hostsutl.py - contains main parts of Hosts Setup Utility.

* qthostsui.py - contains UI class for the main dialog of Hosts Setup Utility.

* qthosts_rc.py - contains images used by the main dialog.

* retrievedata.py - contains tools to read data from the local hosts data
        file.

* utilities.py - contains basic utilities used by Hosts Setup Utility.


Tools for Developers
--------------------

* _build.py - contains tools to make packages for different platforms.

        Usage: _build.py [type]
        Options:
            type    define the platform to make package for. Optional choices
                    could be: py2exe, py2app, py2tar, py2source
                        py2exe - Make binary excutables for Windows. The
                        py2app - Make binary excutables for Mac OS X. The
                            operations of this option depends on the py2app
                            distutils extension.
                        py2app - Make source code packages for X11 users.
                        py2source - Make source code packages for developers.

* _pylupdate4.py : contains tools to update the language files for UI.

* _pyuic4.py : contains tools update the UI code from UI design.


The Rest of the Distribution
----------------------------

* lang/ - This directory contains language files for Hosts Setup Utility.
        The *.qm files would be included in distribution packages.

* img/ - This directory contains images and Icons used by  Hosts Setup
        Utility.
        The files in this directory would on be included source code package
        for developers.

* mac_res/ - This directory contains resources to make excutables binaries for
        Mac OS X.
        The files in this directory would on be included source code package
        for developers.

* hostsutl.pro - Project file for QT.

* qthosts.qrc - Resource file for main dialog designed by QT.

* qthostsui.ui - UI project file for the main dialog.


Author/Maintainer
-----------------
huhamhire <me@huhamhire.com>

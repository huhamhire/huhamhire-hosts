###################
Hosts Setup Utility
###################

Introduction
============
Since the governments of some countries are using technical methods blocking
internet access to some websites and web service providers which includes some
world famous sites like Google, YouTube, twitter, Facebook, and Wikipedia
etc., we designed this tiny utility in order to help people getting through
the Internet blockade.

`Hosts Setup Utility` provides basic tools to manage the hosts file on current
operating systems. It also provides both support for Graphical Desktop
environment with Graphical User Interface (GUI) and CLI environment with
Text-based User Interface (TUI).

Users could use these tool to modify the hosts to visit specified websites or
services blocked by ISP/government. Functions which help users to
backup/restore hosts files are also provided.

`Hosts Setup Utility` is designed by `huhamhire-hosts team`. For further
information, please visit our `website <https://hosts.huhamhire.com>`_.


Developer Documentation
=======================
Developers could find our project documentation by visiting
`<https://hosts.huhamhire.com/document/>`_.

This documentation contains descriptions of modules and functions which are
used in the current version of `Hosts Setup Utility`. These documents also
provides some optional methods for developers to help improve this tool.


License
=======
Licensed under the GNU General Public License, version 3. You should have
received a copy of the GNU General Public License along with this program.
If not, see `<http://www.gnu.org/licenses/>`_.


System Requirements
===================
Here are the system requirements needed for using `Hosts Setup Utility`.


Graphical User Interface (GUI)
------------------------------
System requirements to run `Hosts Setup Utility` on Graphical Desktop are
listed here:

* Microsoft Windows 2000 or newer for Windows users.

* Mac OS X 10.6 or newer for Macintosh users.

* Linux/X11 desktop with Python 2 and PyQt4 for Linux/X11 users.

* Internet access is required for retrieving the latest hosts data file.

  - On some linux distributions, pre-built packages of PyQt4 can be
    found in software repositories. For example, you can install PyQt4 on
    a debian distribution simplly using:

    .. code-block:: bash

        apt-get install python-qt4


More requirements are needed for developers:

* Python 2.6/2.7 with PyQt4 extension for developers.

* py2exe or py2app would be required while making binary excutables for
  specified platforms.


Text-based User Interface (TUI)
-------------------------------
Any devices with `Python 2` and `Python Standard Library` INSTALLED could run
`Hosts Setup Utility` in TUI mode from a 80x24 terminal. In addition to this,
TUI mode could also be operated via SSH on remote devices/machines/servers.
All you need is a system with Python 2 installed.


Get Started
===========
Since `Hosts Setup Utility` supports both Graphical Desktop environment with
Graphical User Interface (GUI) and CLI/terminal environment with Text-based
User Interface (TUI), users could the way they would like to launch this tool.

However, GUI mode is highly recommended because several features like
backup/restore hosts file are still not supported in TUI mode currently.

* If the program is not running with privileges to modify the hosts
  file, a warning message would be shown and you could only do operations
  like backup hosts file and update the local data file. Plus, TUI mode
  could not get started in this condition.


Graphical User Interface (GUI) Mode
-----------------------------------
* Windows(x86/x64): Run hoststool.exe from the binary excutables package to
  get started.

      - "Run as Administrator" is needed for operations to change the
        hosts file on Windows Vista or newer.

* Mac OS X: Run HostsUtl application from the binary excutables package to get
  started.

      - Because of the locale problem with py2app, the automatic language
        selection may not work correctly on Mac OS with binary executable
        files. You can just choose the language on your on choice.

* Linux/X11(Source code): Run command "python hoststool.py" to get started.

      - All platforms with Python and the PyQt4 could use this method to run
        with the source code.
      - A desktop environment with PyQt4 and python is needed only for
        Linux/X11 users to start a GUI Session.


Text-based User Interface (TUI) Mode
-----------------------------------
* Windows Excutable(x86/x64):

  #. Start a command line(could be `cmd` or `Power Shell`).

     - "Run as Administrator" is needed for operations to change the
       hosts file on Windows Vista or newer.

  #. Change directory to the folder contains binary executable files. of
     `Hosts Setup Utility`.

  #. Run ``hoststool_tui.exe`` with an argument ``-t`` from the directory to
     get started.

* Python Source Code:

  `Python Source Code` is very easy to be started through any terminals on any
  operating systems.

  #. Change your directory to the source script.

  #. Run ``python hoststool.py -t`` in the terminal. Of course, wirte
     privileges to access the hosts file on current system is required. If
     not, a warning message box would show up and then terminate current
     session.


User Customized Hosts
=====================

Users are allowed to add customized hosts list as an independent module to
make a hosts file. All you need to do is create a simple text file named
``custom.hosts`` in the working directory, and put your own hosts entries
into this file. Then you would find a `Customized Hosts` option in the
function list.

  * Non-ASCII characters are not recommended to be put into the
    customized hosts file.


Author/Maintainer
=================
huhamhire `<me@huhamhire.com>`_

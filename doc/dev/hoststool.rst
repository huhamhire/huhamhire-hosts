Hosts Setup Utility
===================

This chapter contains discriptions for modules, scripts, and configurations
at the root working directory of `Hosts Setup Utility`.

UtilLauncher
------------
.. automodule:: hoststool
    :members:


Packaging Tool
--------------

A simple script is also provided for developer to make new package of
`Hosts Setup Utility` distributions. This tool could create distributions for
`Windows`, `OS X`, `Linux`, and any `Unix-like` systems.

* **_build.py**

Here is the usage for running this script::

    Usage: _build.py [type]
    Options:
        type    Indicating the mode for making packages. Optional choices
                could be: py2exe, py2app, py2tar, py2source
                    py2exe - Make binary excutables for Windows. The
                        operations of this option depends on the py2exe
                        distutils extension.
                    py2app - Make binary excutables for Mac OS X. The
                        operations of this option depends on the py2app
                        distutils extension.
                    py2app - Make source code packages for X11 users.
                    py2source - Make source code packages for developers.

.. note::
    * ``py2exe`` option requires a Windows platform with `py2exe` installed.
    * ``py2app`` option requires an OS X platform with `PyQt4` and `py2app`.


Configuration Files
-------------------

There is only one configuration file stored in the root working directory
currently, which is used to configure the mirrors servers for
`Hosts Setup Utility`.

* **network.conf**

Here is an example for setting up a server in the configuration file::

    [Github]
    label = GITHUB
    server = github.com
    update = http://huhamhire.github.com/huhamhire-hosts/update/


Hosts Data File
---------------

`hosts data file` is not included in any distributions. It is usually
downloaded from the mirror servers of this project.

* **hostslist.data**

In fact, the data file `hostslist.data` is just a zip package containing a
sqlite database file `hostslist.s3db`. The database file could be loaded by
any sqlite database managing tools.

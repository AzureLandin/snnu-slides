#!/usr/bin/env python3
"""Disk And Execution MONitor (Daemon)

Rebuilds the slides with ``make`` on a fixed interval (1 second) so the
output PDF stays in sync with the sources.  On POSIX systems the process
can be detached into the background with ``-f``; on Windows there is no
fork(), so it always runs in the foreground.

Usage:
    python build-daemon.py        # run in foreground
    python build-daemon.py -f     # POSIX: detach into background
    python build-daemon.py -k     # terminate a running daemon

References:
    1) Advanced Programming in the Unix Environment: W. Richard Stevens
    2) Unix Programming Frequently Asked Questions:
         http://www.erlenstar.demon.co.uk/unix/faq_toc.html
"""

import os
import sys
import time
import signal
import subprocess
from optparse import OptionParser
from configparser import ConfigParser

# Default daemon parameters.
UMASK = 0
WORKDIR = os.getcwd()
MAXFD = 1024
PIDFILE = "build-daemon.pid"
REDIRECT_TO = os.devnull


def create_daemon():
    """Detach from the controlling terminal and run in the background.

    Windows has no fork()/setsid(), so there we simply stay in the
    foreground and return 0 (the caller still records the pid file).
    """
    if os.name != "posix":
        return 0

    try:
        pid = os.fork()  # First child.
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if pid == 0:
        # Become the session leader of a new session and process group.
        os.setsid()
        try:
            pid = os.fork()  # Second child, so we can never regain a tty.
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))
        if pid == 0:
            # The second child: reset working directory and umask.
            os.chdir(WORKDIR)
            os.umask(UMASK)
        else:
            os._exit(0)  # Exit the first child.
    else:
        os._exit(0)  # Exit the parent of the first child.

    # Close all open file descriptors inherited from the parent.
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = MAXFD
    for fd in range(maxfd):
        try:
            os.close(fd)
        except OSError:
            pass  # fd wasn't open to begin with.

    # Redirect standard I/O to /dev/null.
    os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)
    os.dup2(0, 1)                    # standard output (1)
    os.dup2(0, 2)                    # standard error (2)
    return 0


def fork():
    """Daemonize and record process info in the pid file."""
    retcode = create_daemon()
    if os.name == "posix":
        procParams = """
[process info]
return_code = %s
process_id = %s
parent_process_id = %s
process_group_id = %s
session_id = %s
user_id = %s
effective_user_id = %s
real_group_id = %s
effective_group_id = %s
""" % (retcode, os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0),
       os.getuid(), os.geteuid(), os.getgid(), os.getegid())
    else:
        procParams = "[process info]\nprocess_id = %s\n" % os.getpid()
    with open(PIDFILE, "w") as f:
        f.write(procParams + "\n")
    return retcode


def load_pid_file():
    cfg = ConfigParser()
    cfg.read(PIDFILE)
    if not cfg.has_section("process info"):
        raise SystemExit("no pid file found: %s" % PIDFILE)
    pinfo = dict(cfg.items("process info"))
    for k, v in pinfo.items():
        try:
            pinfo[k] = int(v)
        except ValueError:
            pass
    return pinfo


def run_daemon():
    # shell=False avoids cmd.exe and its AutoRun noise on Windows.
    try:
        while True:
            subprocess.call(["make", "-s"])
            time.sleep(1)
    except KeyboardInterrupt:
        print("shutting down...")


def main():
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-f", "--fork", action="store_true", dest="fork",
                      default=False, help="launch daemon in background")
    parser.add_option("-k", "--kill", action="store_true", dest="kill",
                      default=False, help="terminate a running daemon")
    (options, args) = parser.parse_args()

    if options.kill:
        pids = load_pid_file()
        pid = pids["process_id"]
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            print("pid %s does not exist" % pid)
        os.unlink(PIDFILE)
        return

    if options.fork:
        retcode = fork()
        run_daemon()
        sys.exit(retcode)

    run_daemon()


if __name__ == "__main__":
    main()

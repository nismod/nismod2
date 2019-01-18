# Configuration file for jupyter-notebook.

## The IP address the notebook server will listen on.
c.NotebookApp.ip = '0.0.0.0'

## The directory to use for notebooks and kernels.
c.NotebookApp.notebook_dir = '.'

## Whether to open in a browser after starting. The specific browser used is
#  platform dependent and determined by the python standard library `webbrowser`
#  module, unless it is overridden using the --browser (NotebookApp.browser)
#  configuration option.
c.NotebookApp.open_browser = False

## Forces users to use a password for the Notebook server. This is useful in a
#  multi user environment, for instance when everybody in the LAN can access each
#  other's machine through ssh.
#
#  In such a case, server the notebook server on localhost is not secure since
#  any user can connect to the notebook server via ssh.
c.NotebookApp.password_required = False

## The port the notebook server will listen on.
c.NotebookApp.port = 8888

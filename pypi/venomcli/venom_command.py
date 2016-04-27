#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys
from argparse import ArgumentTypeError
import os
import glob
import shutil
import subprocess
import json
import re


class ColorWriter(object):
  PURPLE    = '\033[95m'
  BLUE      = '\033[94m'
  GREEN     = '\033[92m'
  YELLOW    = '\033[93m'
  RED       = '\033[91m'
  RESET     = '\033[0m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'
  
  @staticmethod
  def set(color):
    import sys
    sys.stdout.write(color)
  
  @classmethod
  def reset(cls):
    cls.set(cls.RESET)
  
  @classmethod
  def write(cls, text, color=RESET, end='\n'):
    cls.set(color)
    print(text, end=end)
    cls.set(cls.RESET)
  
  @classmethod
  def error(cls, text, end='\n'):
    cls.write(text, color=cls.RED, end=end)
  
  @classmethod
  def warn(cls, text, end='\n'):
    cls.write(text, color=cls.YELLOW, end=end)
  
  @classmethod
  def info(cls, text, end='\n'):
    cls.write(text, color=cls.BLUE, end=end)
  
  @classmethod
  def log(cls, text, end='\n'):
    text = re.sub(r'`([^`]*)`', '{}\\1{}{}'.format(cls.UNDERLINE, cls.RESET, cls.GREEN), text)
    cls.write(text, color=cls.GREEN, end=end)


def get_input(*args, **kwargs):
  try:
    input = raw_input
  except NameError:
    pass
  return input(*args, **kwargs)


def check_brew_install():
  command = ['brew', 'list', 'google-app-engine']
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, error = process.communicate()
  
  if error.startswith('Error'):
    ColorWriter.warn('''Google App Engine is not installed on your system
and is required for venom to run.

Install Google App Engine? (y/n): ''', end='')
    response = get_input()
    if response.lower() == 'y':
      os.system('brew install google-app-engine')
    else:
      ColorWriter.error('ERROR: Google App Engine not installed. Exiting')
      exit(1)


def copytree(src, dst, symlinks=False, ignore=None, template=None):
  template = template if template else {}
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
      if not os.path.exists(d) or not os.path.isdir(d):
        os.mkdir(d)
      copytree(s, d, symlinks, ignore)
    else:
      s_file = open(s, 'r')
      s_value = s_file.read()
      s_file.close()
      
      for key, value in template.items():
        s_value = s_value.replace('{{{{ {} }}}}'.format(key), value)
      
      d_file = open(d, 'w+')
      d_file.write(s_value)
      d_file.close()

      # shutil.copy2(s, d)


class VenomCLI(object):
  def __init__(self):
    parser = argparse.ArgumentParser(
      description='Venom command line tool',
      usage='''venom <command> [<args>]

The most commonly used venom commands are:
   create   Create a new pyvenom project
   start    Starts a venom server
   kill     Forcefully closes an open port
''')
    parser.add_argument('command', help='Subcommand to run')
    
    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    args = parser.parse_args(sys.argv[1:2])
    if not hasattr(self, args.command):
      ColorWriter.error('Unrecognized command')
      parser.print_help()
      exit(1)
    # use dispatch pattern to invoke method with same name
    getattr(self, args.command)()

  def create(self):
    parser = argparse.ArgumentParser(description='Create a new venom project')
    # prefixing the argument with -- means it's optional
    parser.add_argument('dir', help='The directory in which to create a new pyvenom project')
    parser.add_argument('-s', '--source', help='The source directory for creation boilerplate', default=None, action='store')
    parser.add_argument('-a', '--application', help='The Google App Engine application ID', default=None, action='store')
    # now that we're inside a subcommand, ignore the first
    # TWO argvs, ie the command (git) and the subcommand (commit)
    args = parser.parse_args(sys.argv[2:])
    # create a new project
    dir_path = os.path.abspath(args.dir)
    dir_exists = os.path.exists(dir_path)
    if dir_exists:
      if not os.path.isdir(dir_path):
        raise ArgumentTypeError('path is not a directory: \'{}\''.format(args.dir))
    else:
      os.makedirs(dir_path)
    
    if args.source:
      source_path = os.path.abspath(args.source)
    else:
      cli_dir = os.path.dirname(os.path.realpath(__file__))
      source_path = os.path.abspath(os.path.join(cli_dir, 'boilerplate'))
    
    copytree(source_path, dir_path, template={
      'application':
        args.application
        if args.application else
        os.path.basename(os.path.normpath(dir_path))
    })
    
    os.system('cd {} && venom run vendor:install'.format(dir_path))
    
    ColorWriter.log('''New venom project created at ./{}

  To run the server
    - Run `venom start test` or
    - Run `cd test` and then `venom start`
  
  To open the server in the Venom IDE
    - Run `venom ide test` or
    - Run `cd test` and then `venom ide`'''
    .format(os.path.basename(os.path.normpath(dir_path))))
  
  def start(self):
    parser = argparse.ArgumentParser(description='Run a venom server')
    parser.add_argument('dir', help='pyvenom server directory', default='.', action='store', nargs='?')
    parser.add_argument('-c', '--clean', help='Clear all databases before starting the server', action='store_true')
    parser.add_argument('--port', help='Server port', action='store')
    parser.add_argument('--host', help='Server host', action='store')
    parser.add_argument('--admin_port', help='Admin server port', action='store')
    parser.add_argument('--admin_host', help='Admin server host', action='store')
    args = parser.parse_args(sys.argv[2:])
    
    check_brew_install()
    
    dir_path = os.path.abspath(args.dir)
    
    command = 'dev_appserver.py "{}"'.format(dir_path)
    kwargs = []
    if args.clean:
      kwargs.append('--clear_datastore')
      kwargs.append('--clear_search_indexes')
      kwargs.append('--clear_prospective_search')
    
    if args.port: kwargs.append('--port {}'.format(args.port))
    if args.host: kwargs.append('--host {}'.format(args.host))
    if args.admin_port: kwargs.append('--admin_port {}'.format(args.admin_port))
    if args.admin_host: kwargs.append('--admin_host {}'.format(args.admin_host))
    
    os.system(command + ' ' + ' '.join(kwargs))
  
  def kill(self):
    parser = argparse.ArgumentParser(description='Forcefully closes a port')
    parser.add_argument('port', help='Port to forcefully close', action='store')
    args = parser.parse_args(sys.argv[2:])
    
    command = ['lsof', '-t', '-i:{}'.format(args.port)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if output:
      ColorWriter.warn('Confirm force close port {} (y/n): '.format(args.port), end='')
      response = get_input()
      if response.lower() == 'y':
        os.system('kill -9 {}'.format(output))
        ColorWriter.warn('Port {} forcefully closed'.format(args.port))
        exit(1)
      else:
        ColorWriter.warn('Snake bite canceled. Exiting')
        exit(1)
    
    ColorWriter.warn('Port {} is already closed. Exiting'.format(args.port))
    exit(1)
  
  def run(self):
    parser = argparse.ArgumentParser(description='Venom script runner')
    parser.add_argument('script_name', help='Script name from venom.json', action='store')
    args = parser.parse_args(sys.argv[2:])
    
    curr_dir = os.getcwd()
    json_file = os.path.join(curr_dir, 'venom.json')
    exists = os.path.exists(json_file)
    is_file = os.path.isfile(json_file)
    
    if not exists:
      ColorWriter.error('ERROR: Current project does not contain venom.json in the root. Exiting')
      exit(1)
    
    if not is_file:
      ColorWriter.error('ERROR: venom.json is not a file. Exiting')
      exit(1)
    
    try:
      venom_json = json.loads(open(json_file, 'r').read())
    except ValueError:
      ColorWriter.error('ERROR: venom.json file is not a valid JSON')
      exit(1)
    
    if not 'scripts' in venom_json:
      venom_json['scripts'] = {}
    
    script_name = args.script_name
    if not script_name in venom_json['scripts']:
      ColorWriter.error('ERROR: script name \'{}\' not found in venom.json scripts'.format(script_name))
      exit(1)
    
    script = venom_json['scripts'][script_name]
    os.system(script)


def main():
  VenomCLI()


if __name__ == '__main__':
  main()

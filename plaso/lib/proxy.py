#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The Plaso Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This file contains a proxy object that can be used to provide RPC access."""

import abc


def GetProxyPortNumberFromPID(process_id):
  """Simple mechanism to set the port number based on a PID value.

  Args:
    process_id: An integer, process ID (PID), value that should be used to find
                a port number.

  Returns:
    An integer indicating a possible port number for the process to listen on.
  """
  # TODO: Improve this method of selecting ports.
  # This is in now way a perfect algorightm for choosing port numbers (what if
  # it is already assigned?, etc)
  if process_id < 1024:
    return process_id + 1024

  if process_id > 65535:
    # Return the remainder of highest port number, sent back to the
    # function itself, since this number could be lower than 1024.
    return GetProxyPortNumberFromPID(process_id % 65535)

  return process_id


class ProxyServer(object):
  """An interface defining functions needed for a proxy object."""

  def __init__(self, port=0):
    """Initialize the proxy object.

    Args:
      port: An integer indicating the port number the proxy listens to.
            This is optional and defaults to port zero.
    """
    super(ProxyServer, self).__init__()
    self._port_number = port

  @property
  def listening_port(self):
    """Returns back the port the proxy listens to."""
    return self._port_number

  @abc.abstractmethod
  def Open(self):
    """Sets up the necessary objects in order for the proxy to be started."""

  @abc.abstractmethod
  def StartProxy(self):
    """Start the proxy.

    This usually involves setting up the proxy to bind to an address and
    listen to requests.
    """

  @abc.abstractmethod
  def SetListeningPort(self, new_port_number):
    """Change the port the proxy listens to."""

  @abc.abstractmethod
  def RegisterFunction(self, function_name, function):
    """Register a function for this proxy.

    Args:
      function_name: The name of the registered proxy function.
      function: The callback for the function providing the answer.
    """


class ProxyClient(object):
  """An interface defining functions needed to implement a proxy client."""

  def __init__(self, port=0):
    """Initialize the proxy client.

    Args:
      port: An integer indicating the port number the proxy connects to.
            This is optional and defaults to port zero.
    """
    super(ProxyClient, self).__init__()
    self._port_number = port

  @abc.abstractmethod
  def Open(self):
    """Sets up the necessary objects in order for the proxy to be started."""

  @abc.abstractmethod
  def GetData(self, call_back_name):
    """Return data extracted from a RPC callback.

    Args:
      call_back_name: The name of the call back function or attribute registered
                      in the RPC service.

    Returns:
      The data returned by the RPC server.
    """

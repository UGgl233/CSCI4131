#!/usr/bin/env python3

# See https://docs.python.org/3.2/library/socket.html
# for a description of python socket and its parameters
#
# Copyright 2018, Shaden Smith, Koorosh Vaziri,
# Niranjan Tulajapure, Ambuj Nayab, Akash Kulkarni, and Daniel J. Challou
# for use by students enrolled in Csci 4131 at the University of
# Minnesota-Twin Cities only. Do not reuse or redistribute further
# without the express written consent of the authors.
#
import socket

#add the following
import socket
import os
import stat
import sys
import urllib.parse
import datetime
import re

from datetime import datetime
from urllib.request import urlopen # To open csumn web page
from threading import Thread
from argparse import ArgumentParser


# Calendar.html !!!!


BUFSIZE = 4096
#add the following
CRLF = '\r\n'
METHOD_NOT_ALLOWED = 'HTTP/1.1 405  METHOD NOT ALLOWED{}Allow: GET, HEAD{}Connection: close{}{}'.format(CRLF, CRLF, CRLF, CRLF)
OK = 'HTTP/1.1 200 OK{}{}{}'.format(CRLF, CRLF, CRLF)
NOT_FOUND = 'HTTP/1.1 404 NOT FOUND{}Connection: close{}{}'.format(CRLF, CRLF, CRLF)
FORBIDDEN = 'HTTP/1.1 403 FORBIDDEN{}Connection: close{}{}'.format(CRLF, CRLF, CRLF)
MOVED_PERMANENTLY = 'HTTP/1.1 301 MOVED PERMANENTLY{}Location:  https://www.cs.umn.edu/{}Connection: close{}{}'.format(CRLF,CRLF,CRLF,CRLF)

def get_contents(fname):
    with open(fname, 'r') as f:
        return f.read()

# Take %3A token off
def unquote(time):
    x = re.split('%3A', time)
    return (x[0] + ":" + x[1])

def check_perms(resource):
    """Returns True if resource has read permissions set on 'others'"""
    stmode = os.stat(resource).st_mode
    return (getattr(stat, 'S_IROTH') & stmode) > 0


def client_talk(client_sock, client_addr):
    print('talking to {}'.format(client_addr))
    data = client_sock.recv(BUFSIZE)
    while data:
      print(data.decode('utf-8'))
      data = client_sock.recv(BUFSIZE)

    # clean up
    client_sock.shutdown(1)
    client_sock.close()
    print('connection closed.')

class HTTP_HeadServer:  #A re-worked version of EchoServer
  def __init__(self, host, port):
    print('listening on port {}'.format(port))
    self.host = host
    self.port = port

    self.setup_socket()

    self.accept()

    self.sock.shutdown()
    self.sock.close()

  def setup_socket(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.host, self.port))
    self.sock.listen(128)

  def accept(self):
    while True:
      (client, address) = self.sock.accept()
      #th = Thread(target=client_talk, args=(client, address))
      th = Thread(target=self.accept_request, args=(client, address))
      th.start()

  # here, we add a function belonging to the class to accept
  # and process a request
  def accept_request(self, client_sock, client_addr):
    print("accept request")
    data = client_sock.recv(BUFSIZE)
    req = data.decode('utf-8') #returns a string
    response=self.process_request(req)
    #once we get a response, we chop it into utf encoded bytes
    #and send it (like EchoClient)
    client_sock.send(bytes(response,'utf-8'))

    #clean up the connection to the client
    #but leave the server socket for recieving requests open
    client_sock.shutdown(1)
    client_sock.close()

  def process_request(self, request):
    print('######\nREQUEST:\n{}######'.format(request))

    linelist = request.strip().split(CRLF)
    reqline = linelist[0]
    rlwords = reqline.split()
    lastline = linelist[-1] # Get the last line of request

    if len(rlwords) == 0:
        return ''

    # All supported methods
    if rlwords[0] == 'HEAD':
        resource = rlwords[1][1:] # skip beginning /
        return self.head_request(resource)

    if rlwords[0] == 'GET':
        resource = rlwords[1][1:]
        return self.get_request(resource)

    if rlwords[0] == 'POST':
        return self.post_request(lastline)

    # Bonus
    if rlwords[0] == 'DELETE':
        resource = rlwords[1][1:]
        return self.delete_request(resource)

    if rlwords[0] == 'OPTIONS':
        resource = rlwords[1][1:]
        return self.option_request(resource)

    # Bonus
    if rlwords[0] == 'PUT':
        resource = rlwords[1][1:]
        return self.put_request(resource, lastline)

    else:
        return METHOD_NOT_ALLOWED

  # def put_request(self, resource, lastline):
  #     """PUT GET requests."""
  #     path = os.path.join('.', resource)
  #
  #     if not os.path.exists(resource):
  #         f = open(resource, 'w+')
  #         f.write(lastline)
  #         f.close()
  #
  #     else:


  def post_request(self, lastline):
      """POST GET requests."""
      attributes = lastline.split('&')
      placename = attributes[0].split('=')[1]
      placename = placename.replace('+', ' ')
      add1 = attributes[1].split('=')[1]
      add1 = add1.replace('+', ' ')
      add2 = attributes[2].split('=')[1]
      add2 = add2.replace('+', ' ')
      opentime = attributes[3].split('=')[1]
      opentime = unquote(opentime)
      closetime = attributes[4].split('=')[1]
      closetime = unquote(closetime)
      additionalinfo = attributes[5].split('=')[1]
      additionalinfo = additionalinfo.replace('+', ' ')
      urlinfo = urlinfo[6].split('=')[1]
      body = '<html><body>' + '<p>Following Form Data Submitted Successfully</p>'\
      + '<p>Place Name: ' + placename + '</p>'\
      + '<p>Address Line1: ' + add1 + '</p>'\
      + '<p>Address Line2: ' + add2 + '</p>'\
      + '<p>Open Time: ' + opentime + '</p>'\
      + '<p>Close Time: ' + closetime + '</p>'\
      + '<p>Additional Info: ' + additionalinfo + '</p>'\
      + '<p>URL: ' + urlinfo + '</p>'\
      + '</html></body>'

      return OK + body

  def option_request(self, resource):
      """Option GET requests."""
      path = os.path.join('.', resource)
      header = ''
      if resource == '':
          header += 'HTTP/1.1 200 OK{}'.format(CRLF)
          header += 'Allow: OPTIONS, GET, HEAD, POST, PUT, DELETE\n'
          header += 'Cache-Control: max-age=604800\n'
          header += 'Date: ' + str(datetime.now()) + '\n'
          header += 'Content-Length: 0\n'

      elif resource == 'calendar.html':
          header += 'HTTP/1.1 200 OK{}'.format(CRLF)
          header += 'Allow: OPTIONS, GET, HEAD\n'
          header += 'Cache-Control: max-age=604800\n'
          header += 'Date: ' + str(datetime.now()) + '\n'
          header += 'Content-Length: 0\n'

      elif resource == 'form.html':
          header += 'HTTP/1.1 200 OK{}'.format(CRLF)
          header += 'Allow: OPTIONS, GET, HEAD, POST\n'
          header += 'Cache-Control: max-age=604800\n'
          header += 'Date: ' + str(datetime.now()) + '\n'
          header += 'Content-Length: 0\n'

      return header

  def delete_request(self, resource):
      """Delete GET requests."""
      path = os.path.join('.', resource)
      if resource == 'csumn':
          header = MOVED_PERMANENTLY
          return header

      elif not os.path.exists(resource):
          header = NOT_FOUND
          body = get_contents('404.html')

      elif not check_perms(resource):
          header = FORBIDDEN
          body = get_contents('403.html')

      else:
          os.remove(resource)
          header += 'HTTP/1.1 200 OK{}'.format(CRLF)
          header += 'Date: ' + str(datetime.now()) + '\n'
          body = ''

      return (header + body)

  def get_request(self, resource):
      """Handles GET requests."""
      path = os.path.join('.', resource)
      if resource == 'csumn':
          header = MOVED_PERMANENTLY
          return header

      elif not os.path.exists(resource):
          header = NOT_FOUND
          body = get_contents('404.html')

      elif not check_perms(resource):
          header = FORBIDDEN
          body = get_contents('403.html')

      else:
          header = OK
          body = get_contents(resource)

      return (header + body)


  def head_request(self, resource):
    """Handles HEAD requests."""
    path = os.path.join('.', resource) #look in directory where server is running
    if resource == 'csumn':
      ret = MOVED_PERMANENTLY
    elif not os.path.exists(resource):
      ret = NOT_FOUND
    elif not check_perms(resource):
      ret = FORBIDDEN
    else:
      ret = OK
    return ret

#to do a get request, read resource contents and append to ret value.
#(you should check types of accept lines before doing so)

def parse_args():
  # parser = ArgumentParser()
  # parser.add_argument('--host', type=str, default='localhost',
  #                     help='specify a host to operate on (default: localhost)')
  # parser.add_argument('-p', '--port', type=int, default=9001,
  #                     help='specify a port to operate on (default: 9001)')
  # args = parser.parse_args()
  # return (args.host, args.port)

  if (len(sys.argv) == 1):
      return ('localhost', 9001)
  return ('localhost', int(sys.argv[1]))

if __name__ == '__main__':
  (host, port) = parse_args()
  HTTP_HeadServer(host, port) #Formerly EchoServer

#!/usr/bin/env python3

import boto3
import boto.ec2
import http.server
import socketserver
import signal
import time

#AWS_ACCESS_KEY = boto.config.get('Credentials', 'aws_access_key_id')
#AWS_ACCESS_SECRET_KEY = boto.config.get('Credentials', 'aws_secret_access_key')


dryRun = False; # put the script into dry run mode where the function allows it

ec2Client = boto3.client('ec2')
ec2Resource = boto3.resource('ec2')
conn = boto.ec2.connect_to_region("us-east-1")

#Create EBS volume
vol = conn.create_volume(1, "us-east-1d") #default standard = magnetic
print ('Volume Id: ', vol.id)
print (vol.__dict__)
conn.create_tags([vol.id], {"Name":"AlexandrKulbida"})
time.sleep(30) #to be replaced with waiter

#Security group
response = ec2Client.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    response = ec2Client.create_security_group(GroupName='SECURITY_GROUP',
                                         Description='Ports 80,20',
                                         VpcId=vpc_id)

    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))


    data = ec2Client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
       print(e)

# Create the instance
instanceDict = ec2Resource.create_instances(
    DryRun = dryRun,
    ImageId = "ami-0ff8a91507f77f867",
    KeyName = "keypair2nvirginia",
    InstanceType = "t1.micro",
#    BlockDeviceMappings=[{"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 1}}],
    SecurityGroupIds = [security_group_id],
    MinCount = 1,
    MaxCount = 1
)
# Wait for it to launch before assigning the elastic IP address
instanceDict[0].wait_until_running();


#attach EBS
#result = ec2Client.attach_volume(VolumeId=vol.id,InstanceId=ec2.Instance.id,Device='/dev/sdw')

#: ec2.Instance(id='i-0a97f1aa2abcf08e8')

reservations =   ec2Client.describe_instances(
    Filters=[{'Name': 'instance-state-name', 
              'Values': ['running']}])["Reservations"]

#instance1 = reservations.instanceDict[0]
#print(instance1)

#create EBS volume

#myCode = """#!/bin/bash
#sudo mkfs.ext4 /dev/xvdf
#sudo mkdir /vol
#echo "/dev/xvdf /vol auto noatime 0 0" | sudo tee -a /etc/fstab"""



#result = ec2Client.attach_volume(VolumeId=vol.id,InstanceId=,Device='/dev/sdw')




mytags = [{
    "Key" : "Owner", 
    "Value" : "AlexandrKulbida",
    "Key" : "Name",
    "Value" : "AlexandrKulbida"
       
    } 
    ]
for reservation in reservations :
    for each_instance in reservation["Instances"]:
        ec2Client.create_tags(
            Resources = [each_instance["InstanceId"] ],
            Tags= mytags
           )


#terminate_instances()


###############################
##          HTTP Server       #
###############################

#Sorry for bad modularity of the code :)

import http.server
import cgi
import base64
import json
from urllib.parse import urlparse, parse_qs
from socketserver import ThreadingMixIn
import threading 
#import daemon
import os

class CustomServerHandler(http.server.BaseHTTPRequestHandler):
 
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
 
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
 
    def do_GET(self):
        key = self.server.get_auth_key()
 
        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()
 
            response = {
                'success': False,
                'error': 'No auth header received'
            }
 
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
 
        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('<meta http-equiv="refresh" content=1; URL=http://127.0.0.1:8888" /><pre>'.encode('utf-8'))
            self.wfile.write(str(os.popen('echo "Last commit details:\n\n" && git show --stat && echo "\n\nFree memory:" && free && echo "\n\nCPU:"&& top -n 1 -b').read()).encode('utf-8')) 
            getvars = self._parse_GET()
 
            response = {
                'path': self.path,
                'get_vars': str(getvars)
            }
 
            base_path = urlparse(self.path).path
            if base_path == '/path1':
                # Do some work
                pass
 
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.do_AUTHHEAD()
 
            response = {
                'success': False,
                'error': 'Invalid credentials'
            }
 
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
 
    def do_POST(self):
        key = self.server.get_auth_key()
 
        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()
 
            response = {
                'success': False,
                'error': 'No auth header received'
            }
 
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
 
        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
 
            postvars = self._parse_POST()
            getvars = self._parse_GET()
 
            response = {
                'path': self.path,
                'get_vars': str(getvars),
                'get_vars': str(postvars)
            }
 
            base_path = urlparse(self.path).path
            if base_path == '/path1':
                # Do some work
                pass
 
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.do_AUTHHEAD()
 
            response = {
                'success': False,
                'error': 'Invalid credentials'
            }
 
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
 
        response = {
            'path': self.path,
            'get_vars': str(getvars),
            'get_vars': str(postvars)
        }
 
        self.wfile.write(bytes(json.dumps(response), 'utf-8'))
 
    def _parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(
                self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
 
        return postvars
 
    def _parse_GET(self):
        getvars = parse_qs(urlparse(self.path).query)
 
        return getvars
 
#class ThreadedHTTPServer(ThreadingMixIn, CustomHTTPServer):
#    """Handle requests in a separate thread."""
 
class CustomHTTPServer(http.server.HTTPServer):
    key = ''
 
    def __init__(self, address, handlerClass=CustomServerHandler):
        super().__init__(address, handlerClass)
 
    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')
 
    def get_auth_key(self):
        return self.key

if __name__ == '__main__':
    try:
        while True:
            server = CustomHTTPServer(('', 8888))
#       server = ThreadedHTTPServer(('', 8888))
            server.set_auth('demo', 'demo')
            print("starting server, press <Ctrl-C> once to stop server and terminate AWS resources")

        #response = ec2Client.delete_security_group(
        #GroupId=security_group_id
        #)

            server.serve_forever()
    except KeyboardInterrupt:

            ec2r = boto3.resource('ec2', region_name='us-east-1')
            all_running_instances = [i for i in ec2r.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])]
            for instance in all_running_instances:
                print("Running instance : %s" % instance.id)

            for instance in all_running_instances:
                instance.terminate()
                print("Instance : %s terminated" % instance.id)
                time.sleep(15)
                waiter = ec2Client.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=[instance.id])
                time.sleep(30)
                response = ec2Client.delete_security_group(
                GroupId=security_group_id
                )

            print("KeyboardInterrupt has been caught.")


#    except KeyboardInterrupt:
#        print('Interrupted')
#        try:
#            sys.exit(0)
#        except SystemExit:
#            os._exit(0)

#######################################3
#Terminate instances
#def delete_server(instanceId):
#    ec2Client.terminate_instances(instance_ids=[instanceId])


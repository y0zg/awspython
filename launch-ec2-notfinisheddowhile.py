import boto3
import http.server
import socketserver
import sys
import os
import time

def ec2():
    dryRun = True; # useful variable to put the script into dry run mode where the function allows it

    ec2Client = boto3.client('ec2')
    ec2Resource = boto3.resource('ec2')

    #Security group
    response = ec2Client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = ec2Client.create_security_group(GroupName='SECURITY_GROUP_NAME',
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
# ???    Name = "Test",
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

    reservations=ec2Client.describe_instances(
    Filters=[{'Name': 'instance-state-name', 
              'Values': ['running']}])["Reservations"]

#snapshot = ec2Client.create_snapshot(VolumeId='volume-id', Description='EBS')
#volume = ec2Client.create_volume(SnapshotId=snapshot.id, volume_size=1)
#ec2Client.Instance('instance-id').attach_volume(VolumeId=volume.id, Device='/dev/sdy')
#snapshot.delete()

    mytags=[{
        "Key" : "Owner", 
        "Value" : "AlexandrKulbida",
        "Key" : "Name",
        "Value" : "AlexandrKulbida"
       
        } 
        ]
    for reservation in reservations :
        for each_instance in reservation["Instances"]:
            ec2Client.create_tags(
#             Resources = [instanceDict],
            Resources = [each_instance["InstanceId"] ],
            Tags= mytags
           )

#ec2Client.add_tag('Name','instance-id')

#def make_resource_tag(resource , tags_dictionary):
#   response = resource.create_tags(
#        Tags = mytags)

#terminate_instances()
def delsg():
    response = ec2Client.delete_security_group(
        GroupId='sg-034681939ce58f6f3'
    )


################
#              #
#  HTTP socket #
#              #
################

def httpser():
    import http.server
    import cgi
    import base64
    import json
    
    from urllib.parse import urlparse, parse_qs
 
 
    class CustomServerHandler(http.server.BaseHTTPRequestHandler):
 
def do_HEAD(self):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
 
def do_AUTHHEAD(self):
    self.send_response(401)
    self.send_header(
    'WWW-Authenticate', 'Basic realm="Demo Realm"')
    self.send_header('Content-type', 'application/json')
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
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
 
                    getvars = self._parse_GET()
 
                    response = {
                    'path': self.path,
                    'get_vars': str(getvars)
                    }
                    base_path = urlparse(self.path).path
                    if base_path == '/path1':
                    # Do some work
                        pass
                    elif base_path == '/path2':
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
            self.send_header('Content-type', 'application/json')
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
            elif base_path == '/path2':
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
    server = CustomHTTPServer(('', 8888))
    server.set_auth('demo', 'demo')
    server.serve_forever()

def main():
    start_sotp=input("Enter start or stop for ec2 instance:")

    while True:
            if start_sotp not in ["start","stop"]:
                start_sotp=input("Enter start or stop")
                continue
            else:
                break
    if start_sotp=="start":
        #start_instance(ec2_con_re,in_id)
        ec2()
    else:
        delsg()
        #stop_instance(ec2_con_re,in_id)
        httpser()


#######################################3
#Terminate instances
#def delete_server(instanceId):
#    conn.terminate_instances(instance_ids=[instanceId])



#PORT = 8000


#Handler = http.server.SimpleHTTPRequestHandler

#with socketserver.TCPServer(("", PORT), Handler) as httpd:
#    print("serving at port", PORT)
#    httpd.serve_forever()
# Allocate an elastic IP
#eip = ec2Client.allocate_address(DryRun=dryRun, Domain='vpc')
# Associate the elastic IP address with the instance launched above
#ec2Client.associate_address(
#     DryRun = dryRun,
#     InstanceId = instanceDict[0].id,
#     AllocationId = eip["AllocationId"])

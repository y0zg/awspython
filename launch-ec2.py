import boto3
import http.server
import socketserver

dryRun = False; # useful variable to put the script into dry run mode where the function allows it

ec2Client = boto3.client('ec2')
ec2Resource = boto3.resource('ec2')

#Security group
response = ec2Client.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    response = ec2Client.create_security_group(GroupName='SECURITY_GROUP_NAME',
                                         Description='DESCRIPTION',
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
    SecurityGroupIds = ["sg-bbafdfcd"],
    MinCount = 1,
    MaxCount = 1
)
# Wait for it to launch before assigning the elastic IP address
instanceDict[0].wait_until_running();

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
# Allocate an elastic IP
#eip = ec2Client.allocate_address(DryRun=dryRun, Domain='vpc')
# Associate the elastic IP address with the instance launched above
#ec2Client.associate_address(
#     DryRun = dryRun,
#     InstanceId = instanceDict[0].id,
#     AllocationId = eip["AllocationId"])

#route53Client = boto3.client('route53')
#Now add the route 53 record set to the hosted zone for the domain
#route53Client.change_resource_record_sets(
#    HostedZoneId = 'YOUR_ZONE_ID',
#    ChangeBatch= {
#    'Comment': 'Add new instance to Route53',
#    'Changes': [
#    {
#        'Action': 'CREATE',
#        'ResourceRecordSet': {
#            'Name': 'YOUR_DNS_ENTRY',
#            'Type': 'A',
#            'TTL': 60,
#            'ResourceRecords': [
#            {
#                'Value': eip["PublicIp"]
#            },
#            ],
#        }
#    },
#    ]
#})
 

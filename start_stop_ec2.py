############################
#                          #
# start/stop ec2 instances:#
#                          #
############################
import boto3
import sys
import os
import time
def get_ec2_con_for_give_region(my_region):
    ec2_con_re=boto3.resource('ec2',region_name=my_region)
    return ec2_con_re
def list_instances_on_my_region(ec2_con_re):
    for each in ec2_con_re.instances.all():
        print (each.id)
def get_instant_state(ec2_con_re,in_id):
    for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id',"Values":[in_id]}]):
        pr_st=each.state['Name']
        return pr_st
def start_instance(ec2_con_re,in_id):
    pr_st=get_instant_state(ec2_con_re,in_id)
    if pr_st=="running":
        print("instance is already running")
    else:
        for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id',"Values":[in_id]}]):
            each.start()
            print("please wait it to start")
            each.wait_until_running()
            print("now it is running")

        return
def Thank_you():
    print("\n\nHello")
    return None

def stop_instance(ec2_con_re,in_id):
    pr_st=get_instant_state(ec2_con_re,in_id)
    if pr_st=="stopped":
        print("Instance already stopped")
    else:
        for each in ec2_con_re.instance.filter(Filters=[{'Name':'instance-id',"Values":[in_id]}]):
            each.stop()
            print("please wait it is going to stop")
            each.wait_until_stopped()
            print("now it is stopped")

def welcome():
    print("this scrip will help to start stop ec2 instances")
    print("\n\n")
    time.sleep(2)

def main():
    welcome()
    my_region=input("Enter your region name:")
    print ("please wait")
    ec2_con_re=get_ec2_con_for_give_region(my_region)
    print("please wait listining all instances in your region".format(my_region))
    list_instances_on_my_region(ec2_con_re)
    in_id=input("Choose instance id to start")
    start_sotp=input("Enter start or stop for ec2 instance:")
    while True:
            if start_sotp not in ["start","stop"]:
                start_sotp=input("Enter start or stop")
                continue
            else:
                break
    if start_sotp=="start":
        start_instance(ec2_con_re,in_id)
    else:
        stop_instance(ec2_con_re,in_id)
    Thank_you()


if __name__== '__main__':
    os.system('cls')
    main()













































































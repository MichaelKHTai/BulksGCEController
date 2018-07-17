from googleapiclient import discovery
import google.cloud
from google.oauth2 import service_account
from oauth2client.client import GoogleCredentials
import os
import json
import time
import subprocess
import argparse
import sys

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

config = json.load(open(os.path.join(__location__, 'config.json')))

cred_name = config['cred_name']
service_key = open(os.path.join(__location__, cred_name))
info = json.load(service_key)
credentials = credentials = service_account.Credentials.from_service_account_info(info)

project = config['project']
service = discovery.build('compute', 'v1', credentials=credentials)
user_name = config['user_name']
zone = config['zone']

instances_limit_count = int(config['instances_limit_count'])

class ceclient():
    
    working_group_label = ''

    def search_any(self, search_type, filter = None):
        items = []
        obj = None
        if search_type == "instances": 
            obj = service.instances()
        elif search_type == "disks":
            obj = service.disks()
        
        if obj:
            request = obj.list(project=project, zone=zone, filter=filter)
            while request is not None:
                response = request.execute()
                items += response['items']
                request = obj.list_next(previous_request=request, previous_response=response)
        return items

    def create_instances_from_snapshot(self, snapshot, limit_count = instances_limit_count):
        
        request = service.snapshots().get(project=project, snapshot=snapshot)
        response = request.execute()

        if response:
            source_snapshot = response['name']

            all_instances = self.search_any('instances', filter="labels.type=" + self.working_group_label)

            if len(all_instances) < limit_count:
                all_engine_id = [int(x['labels']['id']) for x in all_instances]
                engine_needed = limit_count - len(all_instances)
                new_disk_id_arr = [i for i in range(0, limit_count) if i not in all_engine_id]
                new_disk_id_arr = new_disk_id_arr[:engine_needed]
                
                for i in range(0, engine_needed):
                    new_disk_id = str(new_disk_id_arr[i])
                    body = {
                        'name': 'cloud-engine-' + self.working_group_label + '-' + new_disk_id,
                        'sourceSnapshot': 'global/snapshots/' + source_snapshot,
                        'labels': {
                            'type':self.working_group_label,
                            'id': new_disk_id
                        }
                    }

                    request = service.disks().insert(project=project, zone=zone, body=body)
                    response = request.execute()

                not_ready = True
                while not_ready:
                    print "Wait 10s for disk to ready."
                    time.sleep(10)
                    disk_list = self.search_any('disks', filter="labels.type=" + self.working_group_label)
                    not_ready = False
                    for disk in disk_list:
                        if disk['status'] != 'READY':
                            print "At least disk -- " + disk['name'] + " is still not ready."
                            not_ready = True
                            break
                            

                for i in range(0, engine_needed):
                    new_disk_id = str(new_disk_id_arr[i])
                    body = {
                            "name": 'cloud-engine-' + self.working_group_label + '-' + new_disk_id,
                            "machineType": "https://www.googleapis.com/compute/v1/projects/" + project + "/zones/" + zone + "/machineTypes/n1-standard-2",
                            "zone": "https://www.googleapis.com/compute/v1/projects/" + project + "/zones/" + zone,
                            "networkInterfaces": [{
                                "accessConfigs": [{
                                    "type": "ONE_TO_ONE_NAT",
                                    "name": "External NAT"
                                }],
                                "network": "global/networks/default"
                            }],
                            "disks": [{
                                "source": "https://www.googleapis.com/compute/v1/projects/" + project + "/zones/" + zone + "/disks/cloud-engine-" + self.working_group_label + "-" + new_disk_id,
                                "boot": True,
                                "autoDelete": True
                            }],
                            "labels":{
                                "type":self.working_group_label,
                                "id":new_disk_id
                            }
                    }
                    request = service.instances().insert(project=project, zone=zone, body=body)
                    response = request.execute()

    def delete_instance(self, name):
        request = service.instances().delete(project=project, zone=zone, instance=name)
        response = request.execute()
        print "Deleting instances: " + name
        return response
    def delete_instances(self, remove_all=False):
        filter = "(labels.type=" + self.working_group_label +") AND (labels.id!=0)"
        if remove_all:
            filter = "labels.type=" + self.working_group_label
        all_instances = self.search_any('instances', filter=filter)
        all_instances_name = [x['name'] for x in all_instances]

        if remove_all:
            print "Request Send, deleting all in instances group: " + self.working_group_label
        else:
            print "Request Send, deleting copies in instances group: " + self.working_group_label
        for instance in all_instances_name:
            self.delete_instance(instance)
        
        
    def disable_instance(self, name):
        request = service.instances().stop(project=project, zone=zone, instance=name)
        response = request.execute()
        print "Request Send, stopping instance: " + name
        return response
    def disable_instances(self):
        all_instances = self.search_any('instances', filter="labels.type=" + self.working_group_label)
        all_instances_name = [x['name'] for x in all_instances]
        for instance in all_instances_name:
            self.disable_instance(instance)


    def enable_instance(self, name):
        request = service.instances().start(project=project, zone=zone, instance=name)
        response = request.execute()
        print "Request Send, starting instance: " + name
        return response
    def enable_instances(self):
        all_instances = self.search_any('instances', filter="labels.type=" + self.working_group_label)
        all_instances_name = [x['name'] for x in all_instances]
        for instance in all_instances_name:
            self.enable_instance(instance)
        

    def upload_file(self, projectname):
        var = raw_input("Upload file with name: " + projectname + " will remove all file and directory with same name in the instance. Are you sure? (y/n)")
        if var.lower().strip() != "y":
            print "Abort uploading."
            return
        is_zip = False
        if projectname.split('.')[1] == "zip":
            is_zip = True
        fullpath_projectname = __location__ + "/" + projectname
        if os.path.isfile(fullpath_projectname):
            all_instances = self.search_any('instances', filter="labels.type=" + self.working_group_label)
            all_instances_name = [x['name'] for x in all_instances]
            
            
            i = 0
            for instance in all_instances_name:

                temp_command = 'gcloud_command_' + str(i) 
                i += 1
                temp_instance = user_name + "@" + instance
                temp_file_path = '/home/' + user_name + '/'

                command_arr = []
                command_arr.append('call gcloud compute ssh ' + temp_instance + ' --zone ' + zone + ' --command "cd ' + temp_file_path + '; rm -rf ' + temp_file_path + projectname.split('.')[0] + '; rm -f ' + temp_file_path + projectname.split('.')[0] + '*"\n')
                command_arr.append('call gcloud compute scp "' + fullpath_projectname + '" ' + instance + ':' + temp_file_path + '\n')
                if is_zip:
                    command_arr.append('call gcloud compute ssh ' + temp_instance + ' --zone ' + zone + ' ' + ' --command "cd ' + temp_file_path + '; unzip ' + temp_file_path + projectname + '"' + '\n')
                with open(os.path.join(__location__, 'bat/' + temp_command + '.bat'), 'w') as bat:
                    bat.writelines(command_arr)
                subprocess.Popen(os.path.join(__location__, 'bat/' + temp_command + '.bat'), shell=True)

    def run_program(self, projectname, starter, args = ''):
        all_instances = self.search_any('instances', filter="labels.type=" + self.working_group_label)
        all_instances_name = [x['name'] for x in all_instances]
        is_python = True
        if starter.split('.')[1] != 'py':
            is_python = False

        i = 0
        for instance in all_instances_name:
            
            temp_command = 'gcloud_command_' + str(i)
            i += 1
            temp_instance = user_name + "@" + instance
            temp_file_path = '/home/' + user_name + '/'

            ssh_call = 'call gcloud compute ssh ' + temp_instance + ' --zone ' + zone + ' --command "cd ' + temp_file_path + '; '
            command_arr = []
            #enable execution on .exe
            command_arr.append(ssh_call + 'chmod +x ' + temp_file_path + projectname + '/*.exe"' + '\n')
            command_arr.append(ssh_call + ('python ' if is_python else '') + temp_file_path + projectname + '/' + starter + ' ' + args + '"' + '\n')
            with open(os.path.join(__location__, 'bat/' + temp_command + '.bat'), 'w') as bat:
                bat.writelines(command_arr)
            subprocess.Popen(os.path.join(__location__, 'bat/' + temp_command + '.bat'), shell=True)

    def __init__(self, label):
        self.working_group_label = label

#create_instances_from_snapshot('haha')
#upload_file("FBPage_NoAPI.zip")
#disable_instances()
#enable_instances()
#delete_instances()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Google Compute Engine Bulk Instances Controller")
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('label', help='Specifiy the Instances with this label name')
    parser.add_argument('--create','-c', help='Create Instances with snapshot name create, number of instances need can be optional added in 2nd arg', nargs='+')
    group.add_argument('--on','-n', action="store_true", help='Turn on all Instances')
    group.add_argument('--off','-f', action="store_true", help='Turn off all Instances')
    parser.add_argument('--delete','-d', action="count", help='Delete Instances except instance with id-0, -ddd for all')
    parser.add_argument('--upload','-u', help='Upload the file with name upload')
    parser.add_argument('--run','-r', help='At least 2 args needed. 1. Project file contains the executable; 2. Executable name (.py/.exe); 3+. Args for executable', nargs='+')

    args = parser.parse_args()

    label = args.label
    worker = ceclient(label)
    if args.create:
        if args.create > 1:
            worker.create_instances_from_snapshot(args.create[0] , int(args.create[1]))
        else:
            worker.create_instances_from_snapshot(args.create[0])
    if args.on:
        worker.enable_instances()
    if args.off:
        worker.disable_instances()
    if args.delete:
        if args.delete > 2:
            worker.delete_instances(True)
        else:
            worker.delete_instances()
    if args.upload:
        worker.upload_file(args.upload)

    if args.run:
        if len(args.run) > 2:
            worker.run_program(args.run[0], args.run[1], ' '.join(args.run[2:]))
        elif len(args.run) > 1:
            worker.run_program(args.run[0], args.run[1])
        else:
            print 'At least 2 args needed. 1. Project file contains the executable; 2. Executable name (.py/.exe); 3+. Args for executable'


    sys.exit(0)
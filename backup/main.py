import functions_framework
from google.cloud import compute_v1
from google.cloud import compute
from flask import request
from markupsafe import escape
import sys
from typing import Any
import time
from datetime import datetime
import pytz
from threading import Thread
from google.api_core.retry import Retry

instance_client = compute_v1.InstancesClient()
disk_client = compute_v1.DisksClient()
global_operations_client = compute_v1.GlobalOperationsClient()
zonal_operations_client = compute_v1.ZoneOperationsClient()

@functions_framework.http
def backup_disks(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        print('Invalid request')
        return 'Invalid request', 400

    vm_name = request_json.get('vm_name')
    zone = request_json.get('zone')
    project_id = request_json.get('project_id')

    if not vm_name or not zone or not project_id:
        print('Missing parameters')
        return 'Missing parameters', 400

    print(f"Inputs: \n  vm_name: {vm_name} \n  zone: {zone} \n  project_id: {project_id}")

    try:
        # Fetch all disks attached to the specified VM
        instance = instance_client.get(project=project_id, zone=zone, instance=vm_name)
        disks = instance.disks
        current_date_time = print_current_time_in_israel()

        operations = []
        snapshot_names = []
        # Create snapshots for each disk
        for disk in disks:
            #responses.append(disk.device_name)
            snapshot_name = f"{vm_name}-{current_date_time}-{disk.source.split('/')[-1]}"
            snapshot = compute_v1.Snapshot()
            snapshot.name = snapshot_name
            snapshot.source_disk = disk.source

            disk_obj = disk_client.get(project=project_id, zone=zone, disk=disk.source.split('/')[-1])
            if disk_obj.region:
                print(f"disk name: {disk.source.split('/')[-1]}    disk region: {disk_obj.region}")
            if disk_obj.zone:
                print(f"disk name: {disk.source.split('/')[-1]}    disk zone: {disk_obj.zone}")
            #print(f"{disk.device_name} - {disk.source}")

            snapshot_client = compute_v1.SnapshotsClient()

            operation = snapshot_client.insert(project=project_id, snapshot_resource=snapshot)

            operations.append(operation)
            snapshot_names.append(snapshot_name)

        results = []
        threads = []
        for op in operations:
            thread = Thread(target=wait_for_global_operation, args=(op,project_id))
            thread.start()
            threads.append(thread)
            #thread.run()

        for thread in threads:
            thread.join()
        
        #Once all snapshots are created, continue to turn on the VM:
        start_op = start_instance(project_id, zone, vm_name)

        print("Snapshots have been taken and instance has been started.")
        return "done", 200

    except Exception as e:
        print(str(e))
        return str(e), 500

def wait_for_global_operation(operation: compute_v1.Operation, project_id):
    ops_client = global_operations_client
    op_name = operation.name
    times_tried = 0
    while True:
        if times_tried > 10:
            print("Timed out.")
            raise TimeoutError("Operation timed out.")
        result = ops_client.wait(project=project_id, operation=op_name)
        #if operation status is DONE
        if str(result.status) == "2104194":
            if result.error:
                raise Exception(f"Error in operation: {result.error}")
            else:
                print(f"Operation finished: {result}")
            return
        times_tried += 1
        time.sleep(10)  # Sleep before retrying to check the operation status

def wait_for_zonal_operation(operation: compute_v1.Operation, project_id, zone):
    ops_client = zonal_operations_client
    op_name = operation.name
    times_tried = 0
    while True:
        if times_tried > 5:
            print("Timed out.")
            raise TimeoutError("Operation timed out.")
            return False
        result = ops_client.wait(project=project_id, operation=op_name, zone=zone)
        #if operation status is DONE
        if str(result.status) == "2104194":
            if result.error:
                raise Exception(f"Error in operation: {result.error}")
                return False
            else:
                print(f"Operation finished: {result}")
                return True
        times_tried += 1
        time.sleep(10)  # Sleep before retrying to check the operation status

def print_current_time_in_israel():
    # Define the timezone for Israel
    israel_tz = pytz.timezone('Israel')

    # Get the current time in UTC
    utc_now = datetime.utcnow()

    # Convert the current UTC time to Israel time
    israel_now = utc_now.astimezone(israel_tz)

    # Print the date and time in a formatted string
    return(israel_now.strftime('%Y%m%d-%H%M%S'))

def start_instance(project_id, zone, instance_name):
    """
    Start a Google Compute Engine instance.

    Args:
        project_id (str): GCP project ID
        zone (str): Zone where the instance is located
        instance_name (str): Name of the instance to start
    """

    num_tries = 5
    i = 0
    while True:
        # Start the instance
        operation = instance_client.start(project=project_id, zone=zone, instance=instance_name)

        # Wait for the operation to complete
        if wait_for_zonal_operation(operation, project_id, zone):
            print(f"Instance '{instance_name}' has been started.")
            break
        i += 1
        if i > num_tries:
            print("Maximum retries reached for instance creation.")
            break
 
# Backup Disks Function

This Python script is designed to be deployed as a Google Cloud Function and facilitates the restoration of Google Compute Engine (GCE) virtual machine (VM) disks which are attached to a given VM, from snapshots captured in the "backup" function in the other section of this package. The process includes stopping the current VM, detaching its disks, creating new disks from snapshots, and then reassembling a new VM with the newly created disks and the original IP address. The old VM is deleted.

## Overview

The script defines an HTTP-triggered Cloud Function which performs the following steps:

- Receives the VM's name, zone, project ID, and a specific snapshot datetime from an HTTP request.
- Stops the specified VM.
- Detaches the VM's disks.
- Creates new disks from the specified snapshots.
- Creates a new VM with the new disks and reattaches the IP.
- Deletes the old VM.

## Setup Requirements

To deploy and run this script, you need:

- A Google Cloud Platform (GCP) account.
- A GCP project with billing enabled.
- Necessary IAM permissions for managing Compute Engine resources and deploying Cloud Functions.

## Deployment

### Enable the APIs: 
- Ensure that the Compute Engine API, Cloud Functions API, and Cloud Run Admin API are enabled in your GCP project.

### Prepare the environment:
- Ensure you have the necessary roles (Project Editor).

### Deploy the Function:
- Go to the Cloud Functions section in the GCP Console.
- Create a new 2nd gen function:
    - Name: e.g., restoreVMFunction.
    - Trigger: HTTP.
    - Source code: Upload the script or use the inline editor.
    - Runtime: Python 3.11 or higher.
    - Memory allocated: 512 MiB.
    - CPU allocated: 0.583.
    - Timeout: Set to 1800 seconds (30 minutes).
    - Environment variables: Configure as needed for your specific setup.
    - Entry point: main

## Using the Function

Once deployed, the function can be invoked by making an HTTP GET request to the URL provided by Cloud Functions. The request should include a JSON payload specifying the vm_name, zone, project_id, and snapshot_datetime (format YYYYMMDD-HHMMSS).

### Sample Payload JSON:

    {
    "vm_name": "example-vm",
    "zone": "us-central1-a",
    "project_id": "my-gcp-project",
    "snapshot_datetime": "20230101-120000"
    }

## Function Details

### Input Validation: 
The function checks if all required parameters (vm_name, zone, project_id, snapshot_datetime) are provided.
### Error Handling: 
Provides detailed error messages for missing parameters or failures during execution.
### Concurrency: 
Utilizes Python threading to manage multiple disk operations concurrently.
### Logging: 
Extensive logging is implemented for operational monitoring and debugging.

## Additional Functions

- stop_instance: Stops the specified VM.
- delete_instance: Deletes the VM once the new one is ready.
- detach_disk: Detaches a disk from the VM.
- create_disk_from_snapshot: Creates a new disk from a given snapshot.
- recreate_instance: Creates the new VM with newly created disks and reassigns the original external IP.
- attach_disk: Attaches a disk to the VM.
- wait_for_zonal_operation: Helper function to monitor the status of zonal operations.

## Notes

- Monitor the function's execution and logs through the Cloud Functions dashboard for operational tracking and troubleshooting.
- This script provides a robust solution for VM restoration in GCE environments, making it suitable for scenarios such as disaster recovery or environment cloning.
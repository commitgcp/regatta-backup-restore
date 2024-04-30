# Backup Disks Function

This Python script is designed to be deployed as a Google Cloud Function. It serves as an automation tool to manage snapshots of all disks attached to a specified Google Compute Engine (GCE) virtual machine (VM) and subsequently start the VM. This can be particularly useful for backup purposes in a cloud environment.

## Overview

The script defines a single Cloud Function which:

- Takes as input the name, zone, and project ID of a GCE VM (which is currently stopped).
- Validates the input.
- Retrieves information about all attached disks.
- Creates snapshots of these disks.
- Waits for the snapshot operations to complete.
- Starts the VM.

## Setup Requirements

To deploy and run this script, you need:

- A Google Cloud Platform (GCP) account.
- A GCP project with billing enabled.
- Appropriate IAM permissions to manage Compute Engine resources and deploy Cloud Functions.

## Deployment

### Enable the APIs: 
- Ensure that the Compute Engine API, Cloud Functions API, and Cloud Run Admin API are enabled in your GCP project.

### Prepare the environment:

- Ensure you have the necessary roles assigned to your account (Project Editor).

### Deploy the Function:
- Navigate to the Cloud Functions section in the GCP Console.
- Create a new 2nd gen function:
    - Name: Assign a name, e.g., backupDisksFunction.
    - Trigger: HTTP.
    - Source code: Inline editor or source from the repository.
    - Runtime: Python 3.11 or higher.
    - Memory allocated: 512 MiB.
    - CPU allocated: 0.583.
    - Timeout: Set to 600 seconds.
    - Environment variables: Include necessary configurations like project ID, if not included in the function's code.
    - Entry point: backup_disks

### Set environment variables: 
- If your function relies on environment-specific configurations, set these in the Cloud Function settings.

## Using the Function

Make sure that your VM is STOPPED (turned off) before running this function.
Once deployed, the function can be invoked by making an HTTP GET request to the URL provided by Cloud Functions. The request must include a JSON payload specifying the vm_name, zone, and project_id.
Sample Payload JSON:

    {
    "vm_name": "example-vm",
    "zone": "us-central1-a",
    "project_id": "my-gcp-project"
    }

## Function Details

### Input Validation: 
Checks if all required inputs (vm_name, zone, project_id) are present.
### Error Handling:
Provides detailed error messages if there are missing parameters or if any part of the operation fails.
### Concurrent Operations: 
Uses threading to manage multiple disk snapshot operations concurrently.
### Logging: 
Includes extensive logging for debugging and operational tracking.

## Additional Functions

### wait_for_global_operation and wait_for_zonal_operation: 
These helper functions are used to poll the status of Compute Engine operations, handling retries and timeouts.
### print_current_time_in_israel: 
A utility function to fetch the current date and time in the Israel timezone, used for naming snapshots.

## Notes

- The function expects the VM associated with the vm_name provided in the input to be stopped before the function is called.
- Monitor the function's execution and logs via the Cloud Functions dashboard to troubleshoot and ensure it operates as expected.
- This script offers a robust automation solution for snapshot management and VM operations in GCE, tailored for deployment as a GCP Cloud Function.
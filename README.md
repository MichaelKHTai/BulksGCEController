# BulksGCEController
Tool for controlling multiple Google Compute Engine instances though local machine.

## Getting Started

1. Create a Google Compute Engine instance
2. In create tabpage, click `Management, security, disks, networking, sole tenancy`
3. Click `Add label`, with Key as `type`, Value as your project name
4. Create a cloud instance Snapshot of the instances created
5. Generate a service-account has all permisson of controlling Compute Engine instance, put the JSON-key file with the controller.py

### Prerequisites

1. gloud is required, please install it though [Google SDK](https://cloud.google.com/sdk/docs/downloads-interactive)
2. Python 2.7+


### Installing

Download the cecontroller.py


### Usage

```
cmd> python cecontroller.py {project_name}
```

Options
```
'--create','-c', help='Create Instances with snapshot name create, number of instances need can be optional added in 2nd arg', nargs='+')
'--on','-n', action="store_true", help='Turn on all Instances')
'--off','-f', action="store_true", help='Turn off all Instances')
'--delete','-d', action="count", help='Delete Instances except instance with id-0, -ddd for all')
'--upload','-u', help='Upload the file with name upload')
'--run','-r', help='At least 2 args needed. 1. Project file contains the executable; 2. Executable name (.py/.exe); 3+. Args for executable', nargs='+')
```

Code Snippet Options
**cecontroller.ceclient(projectname)**
    Create the class for controlling compute engine instances
    --projectname: value of instance tag "type" (please be remember adding the type tag of source instance before creating copies)

**cecontroller.ceclient.enable_instances()**
    *Same as --on*
    Start all compute engine instances.

**cecontroller.ceclient.disable_instances()**
    *Same as --off*
    Close all compute engine instances.

**cecontroller.ceclient.create_instances_from_snapshot(snapshot, limit_count = config.instances_limit_count)**
    *Same as --create*
    Create all compute engine instances copy from source instance's snapshot. 
    **Notice!!** Remember to create a "type" tag for the source instances (not the snapshot).
    --snapshot(string): name of snapshot formed by target instance
    --limit_count(int): number of copied instances will be created

**cecontroller.ceclient.delete_instances(remove_all=False)**
    *Same as --delete*
    Delete all compute engine instances.
    --remove_all(bool): True if all instances including the copying source instance should be deleted

**cecontroller.ceclient.upload_file(workerfilename)**
    *Same as --upload*
    Upload target file to all compute engine instances.
    --workerfilename(string): the file name (.zip/.py/.exe) wanted to be uploaded, for example "FBPage_NoAPI.zip"

**cecontroller.ceclient.run_program(workerfilename, starter, args = '')**
    *Same as --run*
    Run target file in all compute engine instances.
    --workerfilename(string): the file name (.zip/.py/.exe) wanted to be uploaded, for example "FBPage_NoAPI.zip"
    --starter(string): there should be a start file (.py/.exe) for starting the program, it can be program itself.
    --args(string): space separated arguments of the starter, for example "ads 2 -c 1"

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Author

Michael KH Tai

## Date

10/03/2018
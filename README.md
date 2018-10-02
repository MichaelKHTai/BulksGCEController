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


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Author

Michael KH Tai

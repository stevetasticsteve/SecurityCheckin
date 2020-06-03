# Checkin app
A simple PyQt5 app for tracking regular team check ins.

Our organization has people living in remote areas for extended periods of time. Our policy is that once every 3 days 
they need to contact headquarters to check in with the security coordinator. If there is no check in after 3 days the 
security coordinator needs to launch a search and rescue. 
This simple PyQt5 desktop app creates an SQlite database and a user friendly GUI for keeping track of check ins from 
outstations. Clicking on the outstation check in button logs the check in and any stations that go 
longer than 3 days without being checked in appear in red.

The program could be used to keep track of any group of tasks that need to be attended to regularly.

## Getting started
A pyinstaller .exe is provided in the dist folder (whole folder needs to be copied)

Alternatively Python can run SecurityCheckins.pyw

### Prerequisites
- [Python3](https://www.python.org/downloads/)
- PyQt5

### Installing
1. Download and install [Python3](https://www.python.org/downloads/)
2. pip install PyQt5

## Contributing
Bug reports or comments can be emailed to stevetasticsteve@gmail.com

## Licence
 This project is licensed under [GPL 3.0 ].

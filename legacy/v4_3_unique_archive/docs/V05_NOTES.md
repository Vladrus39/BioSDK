# biogpu-core v0.5 notes

v0.5 makes the project more research-ready and hardware-aware.

Added:

- streaming/online change benchmark;
- MaxOne-like dry-run adapter contract;
- strict energy accounting hooks separating host, MEA, stimulator and life-support;
- result versioning/config hash helpers;
- richer static dashboard;
- new tests.

Important limitation: the MaxOne-like adapter is a dry-run software contract only. It does not connect to any vendor SDK or hardware and does not define real stimulation parameters.

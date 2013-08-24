# bigpyp

Handles the high-level configuration of a BigIP load balancer.
Will take these findings and incorporate into our Cloud automation.

High-level is defined as:

* On the network with proper interfaces, bonding, and vlans configured
* Licensed (if applicable)
* Firmware current (if applicable)
* Established cluster
* Outside/inside interfaces configured

## Usage

    $ cd bigpyp/bigpyp/
    $ PASS=<password> python load_balancer.py

## Testing

    $ tox

## License and Author

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

MR IGTL Bridge
==============
Python OpenIGTLink Bridge module for Real-Time Interactive MRI. The goal of this bridge module is to provide a vender-neutral real-time interactive MRI inteface for surgical navigation software, such as [3D Slicer](https://www.slicer.org/). To achieve this goal, the bridge has two network communication interfaces, including open client interface and proprietary scanner interface. 

This repository only provides a platform-independent interface to OpenIGTLink clients. Platform-dependent widget and listner must be provided to connect the bridge to an actual MRI scanner.


Squence Diagram
---------------


![alternative text](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.github.com/ProstateBRP/mrigtlbridge/main/doc/sequence.txt)


Installation
------------

This package can be installed using `pip`. To download the source:

~~~~
% git clone https://github.com/ProstateBRP/mrigtlbridge
% cd mrigtlbridge
~~~~

Then run the `pip` command. To install the system:

~~~~
% pip install . 
~~~~

Alternatively, you may choose to install in the user directory:

~~~~
% pip install . --user
~~~~


Usage
-----

This package comes with simulator software. To run the simulator,

~~~~
% mrigtlbridge
~~~~




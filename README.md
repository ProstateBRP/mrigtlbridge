MR IGTL Bridge
==============
Python OpenIGTLink Bridge module for Real-Time Interactive MRI. The goal of this bridge module is to provide a vendor-neutral real-time interactive MRI interface for surgical navigation software, such as [3D Slicer](https://www.slicer.org/). To achieve this goal, the bridge has two network communication interfaces, including open client interface and proprietary scanner interface. 

This repository only provides a platform-independent interface to OpenIGTLink clients. Platform-dependent widget and listener must be provided to connect the bridge to an actual MRI scanner.


Sequence Diagram
---------------

```mermaid
sequenceDiagram

title Initialization
participant Navigation

participant BridgeGUI
participant IGTLListener
participant MRListener

participant MRScanner

Navigation -> IGTLListener : IGTL(STRING, "CMD_<timestamp>", Text="START_UP")
activate Navigation
activate IGTLListener
IGTLListener -> MRListener : Command
activate MRListener
MRListener -> MRScanner : Command (Proprietary)
activate MRScanner #DarkGray
MRScanner -> MRListener : Status (Proprietary)
deactivate MRScanner
MRListener -> IGTLListener : Status
deactivate MRListener
IGTLListener -> Navigation : IGTL(STATUS, "MR", Code=01(OK), Message=CURRENT_STATUS)
deactivate IGTLListener
deactivate Navigation

note over Navigation, MRScanner : Transition to "Idle"

```


```mermaid
sequenceDiagram

title Idle
participant Navigation

participant BridgeGUI
participant IGTLListener
participant MRListener

alt If the user subscribes parameters
  Navigation -> IGTLListener : IGTL(STRING, "CMD_<timestamp>", Text="START_SCAN")
  activate Navigation
  activate IGTLListener
  IGTLListener -> MRListener : Command
  activate MRListener
  MRListener -> MRScanner : Command (Proprietary)
  activate MRScanner #DarkGray
  MRScanner -> MRListener : Status (Proprietary)
  deactivate MRScanner
  MRListener -> IGTLListener : Status
  deactivate MRListener
  IGTLListener -> Navigation : IGTL(STATUS, "MR", Code=01(OK), Message=CURRENT_STATUS)
  deactivate IGTLListener
  deactivate Navigation
  note over Navigation, MRScanner : Transition to "Scan"
end


```

```mermaid
sequenceDiagram

title Scan
participant Navigation
participant BridgeGUI
participant IGTLListener
participant MRListener

loop Imaging
  alt If user updates slice position 
    Navigation -> IGTLListener : IGTL(TRANSFORM, "PLANE_<id>")
    IGTLListener -> MRListener : Transform
    MRListener -> MRScanner : Transform (Proprietary)
    note over MRScanner: Updates the scan plane.
  end
  note over MRScanner: Acquires an image.
  MRScanner -> MRListener : Image (Proprietary)
  MRListener -> IGTLListener : Image
  IGTLListener -> Navigation : IGTL(IMAGE, "MR Image")
  alt If user stops the scan
    Navigation -> IGTLListener : IGTL(STRING, "CMD_<timestamp>", Text="STOP_SCAN")
    activate Navigation
    activate IGTLListener
    IGTLListener -> MRListener : Command
    activate MRListener
    MRListener -> MRScanner : Command (Proprietary)
    activate MRScanner #DarkGray
    MRScanner -> MRListener : Status (Proprietary)
    deactivate MRScanner
    MRListener -> IGTLListener : Status
    deactivate MRListener
    IGTLListener -> Navigation : IGTL(STATUS, "MR", Code=01(OK), Message=CURRENT_STATUS)
    deactivate IGTLListener
    deactivate Navigation
    note over Navigation, MRScanner : Transition to "Idle"
  end
  
end

```


Installation
------------


Before install the module, make sure to install the Python-wrapped OpenIGTLink library. The code and instruction are available at [the Swig-Python OpenIGTLink repository](https://github.com/tokjun/OpenIGTLink/tree/Swig-Python).

The rest of the package can be installed using `pip`. First, download the source from the git repository using the following command:

~~~~
% git clone https://github.com/ProstateBRP/mrigtlbridge
% cd mrigtlbridge
~~~~

Then run the `pip` command. To install into the system:

~~~~
% pip install . 
~~~~

Alternatively, you may choose to install in the user directory:

~~~~
% pip install . --user
~~~~


Tutorial on Simulator
---------------------


This package comes with simulator software, which can send a series of images to an OpenIGTLink server (e.g., 3D Slicer) stored locally.
The following steps assume that 3D Slicer is used as an OpenIGTLink server.

### Preparation

The images should be in the NRRD format, saved in a single folder, and listed in a list JSON file. The JSON file would look like:

~~~~
{
    "0" : {
        "M" : "SyntheticSequence_000_M.nrrd",
        "P" : "SyntheticSequence_000_P.nrrd"
    },
    "1" : {
        "M" : "SyntheticSequence_001_M.nrrd",
        "P" : "SyntheticSequence_001_P.nrrd"
    },
    "2" : {
        "M" : "SyntheticSequence_002_M.nrrd",
        "P" : "SyntheticSequence_002_P.nrrd"
    },
    "3" : {
        "M" : "SyntheticSequence_003_M.nrrd",
        "P" : "SyntheticSequence_003_P.nrrd"
    },
    "4" : {
        "M" : "SyntheticSequence_004_M.nrrd",
        "P" : "SyntheticSequence_004_P.nrrd"
    },
    "5" : {
        "M" : "SyntheticSequence_005_M.nrrd",
        "P" : "SyntheticSequence_005_P.nrrd"
    },
    "6" : {
        "M" : "SyntheticSequence_006_M.nrrd",
        "P" : "SyntheticSequence_006_P.nrrd"
    },
    "7" : {
        "M" : "SyntheticSequence_007_M.nrrd",
        "P" : "SyntheticSequence_007_P.nrrd"
    },
    "8" : {
        "M" : "SyntheticSequence_008_M.nrrd",
        "P" : "SyntheticSequence_008_P.nrrd"
    }
}
~~~~

From a terminal, start the simulator using the following command: 

~~~~
% mrigtlbridge_sim
~~~~

### Connecting 3D Slicer and the simulator

On 3D Slicer, open the OpenIGTLink IF module (under "IGT" section of the Modules menu), create a new connector node, and configure it as a server. Then click the "Active" checkbox to activate the server. 

On the simulator, enter the IP address of the computer that runs 3D Slicer in the entry box below "Connect to IGTL Server." If 3D Slicer and the simulator are running on the same machine, the address does not need to be changed ("127.0.0.1"). Click the "Connect to IGTL Server." button to connect the simulator to 3D Slicer. If successful, the Status of the connector becomes "ON."

### Loading the image list file

Click the '...' button in the "Image List" line to open a file selection dialog box. Choose the JSON file and click "OK". Then click the "Connect to MRSIM."" 

### Start image transfer. 

The simulator does not start image streaming until it receives a command from the server. The command is an OpenIGTLink STRING message containing "START_STRING". To send send the command from 3D Slicer:

1. Open the "Texts" module.
2. From the "Text node" selector, choose "Create New Text as..", and then enter "CMD" in the dialog box to create a text node.
3. Click the "Edit" button below the text box, and edit the content to "START_SEQUENCE".
4. Open the "OpenIGTLink IF" module, and go to the "I/O Configuration" section.
5. Expand the tree under the connector used for connecting the simulator, and click "IN".
6. From the pull-down menu at the bottom of the "I/O Configuration" section, choose "CMD", and click the "+" button next to it.
7. Click the "Send" button next to the "-" button at the bottom of the "I/O Configuration" to push the string message to the simulator.
8. The simulator should start streaming the images.
































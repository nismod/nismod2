# Decide Step

This is the DAFNI wrapper for the NISMOD decision step. The reason this step has been
extracted out is so that each of the other NISMOD models can only require the datasets
they directly use. If this step wasn't extracted out then every model would need a copy
of every dataset in order to be properly used in a SOS Workflow.

This is a very simple image, it just extracts all the datasets into their proper
locations then runs the decision step. In order to create a SOS Workflow this should be
the first step of the Workflow.

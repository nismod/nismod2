#!/usr/bin/env bash

# Search smif logs for timings blocks (found between lines with long strings of ***)
grep INFO smif.log | sed '/\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/,/\*\*\*/{//!b};d'

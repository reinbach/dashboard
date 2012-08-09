Dashboard
=========

A dashboard that accepts different data sets placing a very small requirement on the data structure.

Objective
---------

Able to send any data sets (with minimal requirements) to the service/app and it automatically handles the data set.
If this is the first time the app has received this data set from the particular source, it creates and new "bucket" for the data. Any subsequent data set that matches this initial data set is added to the "bucket".
If similar data set but different data source, then categorize the data set within the "bucket".

The display side of things, attempts to determine the best manner to display the data, allowing user override, and user can view the data dynamically.

Data Assumptions
----------------

1. Data has following format [[1,..n],]
1. If no label, then matching data sets have same n number and matching data type for each value
   1.1 If multiple data sets found, then assign to "dump"
1. First set is taken as header, initially
1. Columns are in the same order

Setup/Installation
------------------

Make sure you have an instance of MongoDB running locally

    python setup.py install
    python app.py
    python producer.py


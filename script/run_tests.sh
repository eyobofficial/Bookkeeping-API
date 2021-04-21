#!/bin/bash

# Run all tests
echo 'Run tests...'
python manage.py test --verbosity 2 --no-input

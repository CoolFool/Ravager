#!/bin/bash
cd ravager || exit 1
curl -f http://localhost:"${PORT}"/keep_alive || exit 1
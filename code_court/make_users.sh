#!/bin/bash

token=$(curl -sH "Content-Type: application/json" --data '{"username": "admin", "password": "pass"}' http://codecourt.org/api/login | jq -r ".access_token")

for i in {2..110}; do
    echo $i
    curl -H "Authorization: Bearer $token" -H "Content-Type: application/json" --data "{\"name\": \"Test\", \"username\": \"testuser$i\", \"password\": \"pass\", \"contest_name\": \"UNO\"}" http://codecourt.org/api/make-defendant-user
done

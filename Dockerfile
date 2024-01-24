FROM ubuntu:latest
LABEL authors="vladb"

ENTRYPOINT ["top", "-b"]
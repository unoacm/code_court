FROM alpine

ARG UNAME=user
ARG UID=1000

RUN apk add --no-cache python python3 lua gcc g++ openjdk8 gfortran ruby perl nodejs guile bash rust

RUN adduser -D $UNAME -u $UID -g $UID

RUN mkdir /scratch && chown -R user /scratch && chmod -R 777 /scratch

VOLUME ["/share"]

# remove setuid, setguid
RUN find / -perm +6000 -type f -exec chmod a-s {} \; || true \
        find / -xdev -type d -perm +0002 -exec chmod o-w {} + \
        find / -xdev -type f -perm +0002 -exec chmod o-w {} + \
        find / -xdev -regex '.*apk.*' -exec rm -fr {} +

USER user

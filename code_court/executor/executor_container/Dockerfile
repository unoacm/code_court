FROM alpine:3.5

RUN apk add --no-cache python python3 lua gcc g++ openjdk8 gfortran ruby perl nodejs bash && \
    adduser -S user


# remove setuid, setguid
RUN find / -perm +6000 -type f -exec chmod a-s {} \; || true \
        find / -xdev -type d -perm +0002 -exec chmod o-w {} + \
        find / -xdev -type f -perm +0002 -exec chmod o-w {} + \
        find / -xdev -regex '.*apk.*' -exec rm -fr {} + \

USER user

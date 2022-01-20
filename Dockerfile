FROM python:3.9-alpine

# Define variables
ENV USER=butUser
ENV PROJ_FOLDER=/home/${USER}/VUT_MPA-MOK-project

RUN apk add --no-cache build-base

# Create a new user and create folder for project
RUN adduser -Ds /bin/bash ${USER}
RUN mkdir ${PROJ_FOLDER}/

WORKDIR ${PROJ_FOLDER}/

# Install required packages to pip
COPY --chown=${USER} ./pysrc/requirements.txt ./
RUN pip install -r ./requirements.txt

USER ${USER}

# Add all project files
ADD --chown=${USER} ./index.html ./main.py ./
ADD --chown=${USER} pysrc ./pysrc/
ADD --chown=${USER} static ./static/

ENTRYPOINT ["python"]

CMD ["main.py"]
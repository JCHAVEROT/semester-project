#####################################
# RCP CaaS requirement (Setup)
#####################################

# Use an image with GPU support (CUDA 11.3.1)
FROM nvidia/cuda:11.3.1-runtime-ubuntu20.04

# Create user inside the container for EPFL mapping
ARG LDAP_USERNAME
ARG LDAP_UID
ARG LDAP_GROUPNAME
ARG LDAP_GID

RUN groupadd ${LDAP_GROUPNAME} --gid ${LDAP_GID} && \
    useradd -m -s /bin/bash -g ${LDAP_GROUPNAME} -u ${LDAP_UID} ${LDAP_USERNAME}

# Copy project files
RUN mkdir -p /home/${LDAP_USERNAME}
COPY . /home/${LDAP_USERNAME}
RUN chown -R ${LDAP_USERNAME}:${LDAP_GROUPNAME} /home/${LDAP_USERNAME}

# Install required packages
RUN apt-get update -y && apt-get install -y \
    curl git gcc g++ make openssl libssl-dev libbz2-dev libreadline-dev \
    libsqlite3-dev python3-dev libmysqlclient-dev wget

# Switch to the user
USER ${LDAP_USERNAME}
WORKDIR /home/${LDAP_USERNAME}

#####################################
# Miniconda and dependencies
#####################################

# Install Miniconda (Silent mode) in user directory
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.1.0-1-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /home/${LDAP_USERNAME}/miniconda3 && \
    rm miniconda.sh

# Set Conda environment variables
ENV PATH="/home/${LDAP_USERNAME}/miniconda3/bin:$PATH"

# Initialize Conda for bash and activate environment
RUN /home/${LDAP_USERNAME}/miniconda3/bin/conda init bash && \
    echo "source /home/${LDAP_USERNAME}/miniconda3/bin/activate base" >> /home/${LDAP_USERNAME}/.bashrc

# Install dependencies
RUN conda install pytorch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 pytorch-cuda=11.7 -c pytorch -c nvidia

#####################################
# Hugging Face Authentication
#####################################

# Define an argument for Hugging Face token
ARG HF_TOKEN

# Pass the token into the environment
ENV HF_HOME="/home/${LDAP_USERNAME}/.cache/huggingface"
ENV HUGGINGFACE_HUB_CACHE="/home/${LDAP_USERNAME}/.cache/huggingface/hub"
ENV HF_TOKEN=${HF_TOKEN}

# Ensure the Hugging Face directory exists and store the token
RUN mkdir -p ${HF_HOME} && \
    echo ${HF_TOKEN} > ${HF_HOME}/token && \
    chmod 600 ${HF_HOME}/token

# Install Hugging Face CLI and authenticate
RUN pip install huggingface_hub && \
    huggingface-cli login --token ${HF_TOKEN}

#####################################
# Final Setup
#####################################

# Set working directory
WORKDIR /home/${LDAP_USERNAME}/FedBiscuit

# Install additional Python packages
RUN pip install -e .[llm]
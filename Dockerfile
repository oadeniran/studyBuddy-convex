# Use Ubuntu as the base image
FROM ubuntu:latest

# Update package lists and install required packages
RUN apt-get update && apt-get install -y \
    nodejs npm \
    python3 python3-pip

# Set up symbolic links for compatibility with npm
# RUN ln -s /usr/bin/nodejs /usr/bin/node

# Install npx globally
RUN npm install -g npx

# Copy requirements 
COPY requirements.txt requirements.txt

# Install pip requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy the home.py file into the container
COPY . .

#Expose port
EXPOSE 80

# Set the entry point command to run 'npx convex dev' and 'streamlit run home.py'
CMD ["sh", "-c", "npx convex dev && streamlit run Home.py"]

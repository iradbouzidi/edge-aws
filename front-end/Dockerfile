# pull official base image
FROM arm32v7/node:buster-slim

# set working directory
WORKDIR /usr/src/app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# install app dependencies
COPY front-end/package.json ./
COPY front-end/package-lock.json ./
RUN npm install --silent

# add app
COPY front-end/. ./

# expose port
EXPOSE 3001

# start app
CMD ["npm", "start"]
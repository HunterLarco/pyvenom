# Venom

Welcome to the Venom project. Venom is a set of API tools that make server development faster and easier to understand while still staying scalable and modern. Learn more about our vision at [venom.io](http://venom.io)

# PyVenom

PyVenom is a framework that wraps Google App Engine. It's goal is to bring the barrier to entry of servers lower than App Engine already does while still remaining useful.

## Getting Started
### Required Installations

1. Install [homebrew](http://brew.sh/)
1. Install Python

	```
	$ brew install python
	```
1. Install pip

	```
	$ sudo easy_install pip
	```
1. Install Google App Engine

	```
	$ brew install google-app-engine
	```

### How to Use PyVenom

1. Installation 
	
	Simply run
	
	```
	$ sudo pip install pyvenom
	```

	That's it!

1. Creating a New Project

	```
	$ venom create hello-world
	```

1. Run the New Server

	```
	$ cd hello-world
	$ venom start
	```
	
	
	Google App Engine is required for PyVenom to run. If you do not have it installed on your system, you will be prompted to install.
	
	
	```
	Install Google App Engine? (y/n): y
	```

1. Check Your Server

	Goto [localhost:8080/api/v1/helloworld](http://localhost:8080/api/v1/helloworld), you should see a JSON response that says 'Hello World!'. Congrats! You've created your first PyVenom server.

## Miscellaneous Scripts

1. Running Tests

	```
	$ npm run test
	```
1. Running Example Server

	```
	$ npm run example:start
	```
1. Install local Venom on the Example Server

	```
	$ npm run example:venom:install
	```
1. Running venom.io local Server

	```
	$ npm run website:start
	```

Why do we use `npm` for a python project? Because it's a convenient script runner.
# Venom

Welcome to the Venom project. Venom is a set of api tools that make server development faster and easier to understand while still staying scalable and modern. Learn more about our vision at [venom.io](http://venom.io)

---

## PyVenom

PyVenom is a framework that wraps Google App Engine. It's goal is to bring the barrier to entry of servers lower than App Engine already does while still remaining useful.

---

## How to Use PyVenom

**(1) Installation**

Simply run `$ sudo pip install pyvenom`. That's it!

**(2) Creating a New Project**

Run `$ venom create hello-world`

**(3) Run the New Server**

Run `$ cd hello-world` and then `$ venom start`

**(4) Check Your Server**

Goto [localhost:8080/api/v1/helloworld](http://localhost:8080/api/v1/helloworld), you should see a JSON response that says 'Hello World!'. Congrats! You've created your first pyvenom server.

---

## How to Start Contributing

### Required Installations

- **brew** *[install]* see [brew.sh](http://brew.sh/)
- **python** *[install]* `$ brew install python`
- **pip** *[install]* `$ sudo easy_install pip`
- **google-app-engine** *[install]* `$ brew install google-app-engine`

### Scripts

- *Running Tests* `$ npm run test`
- *Running Example Server* `$ npm run example:start`
- *Install local venom on the Example Server* `$ npm run example:venom:install`
- *Running venom.io local Server* `$ npm run website:start`

Why do we use `npm` for a python project? Because it's a convenient script runner.
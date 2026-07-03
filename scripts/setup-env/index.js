const { exec } = require('node:child_process');
const data = require('./package.json');

const checkBaseCmd = `npm ls -g --depth=0`;
const installBaseCmd = `npm i -g`;
const falseList = [];

const listArray = Object.keys(data.globalDependencies);

const callNext = () => {
  if (listArray.length > 0) {
    depCheck(listArray.shift());
  } else {
    runInstall();
  }
};

const runInstall = () => {
  if (falseList.length > 0) {
    console.log('Running install...');
    exec(`${installBaseCmd} ${falseList.join(' ')}`, (error, stdout, stderr) => {
      if (error !== null) {
        console.log(`ERROR: ${error}`);
        return;
      }

      console.log(stdout);
      console.log(stderr);
    });
  } else {
    console.log('Nothing to install...');
  }
};

const depCheck = (dep) => {
  exec(`${checkBaseCmd} ${dep} --json`, (error, stdout, stderr) => {
    const b = JSON.parse(stdout).dependencies;

    if (!b) {
      falseList.push(dep);
      callNext();
      return;
    }

    const B = Object.keys(b)[0];

    if (error === null) {
      if (B.indexOf(dep) !== -1) {
        console.log(`${B} is installed.`);
      }

      if (stderr && stderr.length > 0) {
        console.log(`${stderr.trim()}`);
      }

      callNext();
    }
  });
};

depCheck(listArray.shift());

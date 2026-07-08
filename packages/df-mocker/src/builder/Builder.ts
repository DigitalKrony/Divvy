/*!
 * Copyright (C) Design:Funedikly. All rights reserved.
 */

import fs from 'node:fs';
import path from 'node:path';
import js_beautify from 'js-beautify';
import { faker } from '@faker-js/faker';

import { CreateHexKey, SanitizeJSON, Save } from '@df/utilities';

import type { BuildConfig, RandomProps } from './Builder.types';
import { helpText } from './Builder.help';
import { defaults } from './Builder.defaults';

const CWD = process.cwd();
const configSrc: string = path.join(CWD, `database.config.json`);
const config: BuildConfig = fs.existsSync(path.resolve(configSrc))
  ? JSON.parse(fs.readFileSync(path.resolve(configSrc), 'utf-8'))
  : {};
const fileDest = config.destination ? config.destination : `./lib/data/db.json`;
const BuiltDatabase: any = {};
let DataToConvert: any = {};
let rerun: boolean = false;
let secondRun: boolean = false;

console.log(helpText);

const getExtensionFiles = (files: string[]): any => {
  const ExtensionObject = {};

  files.forEach((file) => {
    const filePath = path.resolve(path.join(CWD, file));
    const extensionFile = fs.existsSync(filePath) ? JSON.parse(fs.readFileSync(filePath, 'utf-8')) : {};

    Object.assign(ExtensionObject, { ...ExtensionObject, ...extensionFile });
  });

  return ExtensionObject;
};

const buildSchemaObject = () => {
  config.includeDefaults && Object.assign(DataToConvert, defaults);
  !!config.extends &&
    Object.assign(DataToConvert, { ...DataToConvert, ...getExtensionFiles(config.extends) });
    
  fakeSchemas();
};

const fakeSchemas = () => {
  Object.keys(DataToConvert).forEach(async (value: string) => {
    const { count, schema } = DataToConvert[value];

    BuiltDatabase[value] = [];

    if (!!schema || !!count) {
      for (let i = 0; i < count; i++) {
        const thisVal = schema;
        const newFakeBlock = processSchema({ item: thisVal, iteration: i});
        BuiltDatabase[value].push(newFakeBlock);
      }
    }
  });

  if (rerun) {
    secondRun = true;
    reprocess();
  }
};

const processSchema = ( args: { item: object | string | any, iteration?: number } ) => {
  const { item, iteration } = args;
  const fakedBlock: any = {};
  
  Object.keys(item).forEach((key: string) => {
    const value = item[key];
    
    if (typeof value === 'object') {
      if(!!item[key].array) {
        fakedBlock[key] = processArray({item: value.array, iteration});
      } else {
        fakedBlock[key] = processSchema({item: value, iteration});
      }

      
    } else if (typeof value === 'string') {
      fakedBlock[key] = fakeValue({value, iteration});
    }
  });

  return fakedBlock;
};

const processArray = ( args: { item: object | any, iteration?: number }) => {
  const { item: { value, count, unique } } = args;

  console.log(value, count, unique);

  // handle value like the object connection
  // parseFloat for count. [min].[max] for number of items in array
  // unique is ?optional? and makes sure that only one of the same value is in the array.

  return [];
}

const fakeValue = (args: {value: string | any, iteration?: number}) => {
  const { value, iteration } = args;

  const internalValue = `${value}`.indexOf(`$`) === 0;
  const fakerValue = /(?<={{)(.*?)(?=}})/g.exec(value);
  let fakedValue: any = '';

  if (!!internalValue) {
    if (value === '$i') {
      fakedValue = iteration;
    } else {
      const internalFn = /(?<=\$)(.*?)(?=\()/g.exec(value)![1];
      const fnProps = /(?<=\()(.*?)(?=\))/g.exec(value)![1];
      const fnVar: any = SanitizeJSON(fnProps);

      fakedValue = eval(`${internalFn}`)(fnVar);
    }
  } else if (!!fakerValue) {
    fakedValue = faker.helpers.fake(value);705959
  } else {
    fakedValue = value;
  }

  return fakedValue;
};

const reprocess = () => {
  Object.keys(BuiltDatabase).forEach( async (key: string) => {
    for (const i in BuiltDatabase[key]) {
      const block = BuiltDatabase[key][i];

      Object.keys(block).forEach((reKey: string) => {
        block[reKey] = fakeValue({ value: block[reKey] });
      });
    }
  });
};

// @ts-ignore-nex-line no-unused-vars
const random = (args: RandomProps): any => {
  const { type } = args;

  switch (type) {
    case 'connection':
      const { key, object } = args;
      const thisObj = DataToConvert[args.object!];
      const connectionIteration = Math.floor(Math.random() * thisObj.count);
      let connectId: string | number = '';

      if (!!key) {
        rerun = true;
        connectId = secondRun ? BuiltDatabase[object][connectionIteration][key] : `$random(${ JSON.stringify(args) })`;
      } else {
        connectId = connectionIteration;
      }

      return connectId;
    case 'hex-key':
      const { lengths } = args;
      const id: string = CreateHexKey({ lengths });
      return id;
  }
};

(() => {
  buildSchemaObject();

  Save(
    fileDest,
    js_beautify(JSON.stringify(BuiltDatabase), {
      end_with_newline: true,
      brace_style: 'expand',
      indent_size: 2,
    })
  );
})();

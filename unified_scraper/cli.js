#!/usr/bin/env node
const { scrape } = require('./index');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
    .usage('Usage: $0 <url>')
    .demandCommand(1)
    .argv;

const url = argv._[0];

(async () => {
    try {
        const data = await scrape(url);
        console.log(JSON.stringify(data, null, 2));
    } catch (error) {
        console.error(JSON.stringify({ error: error.message }));
        process.exit(1);
    }
})();

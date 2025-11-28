const scraper = require('./index');

// Test URLs
const urls = [
    'https://www.nike.com/tr/t/air-force-1-07-ayakkab%C4%B1s%C4%B1-SqKG2H/CT2302-100', // Example Nike
    // Add other URLs here to test
];

async function runTests() {
    console.log("Starting tests...");

    for (const url of urls) {
        console.log(`\nTesting: ${url}`);
        try {
            const result = await scraper.scrape(url);
            console.log("Result:", JSON.stringify(result, null, 2));
        } catch (error) {
            console.error("Error:", error);
        }
    }
}

runTests();

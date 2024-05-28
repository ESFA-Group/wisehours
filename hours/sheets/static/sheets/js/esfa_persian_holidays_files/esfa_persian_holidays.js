"use strict";

// ****
// comment console.log and console.warn in xmldom.parser.js to prevent logging errors in console
// ****

var xpath = require('xpath');
var dom = require('@xmldom/xmldom').DOMParser;
// const fs = require('node:fs');

function replaceChars(str, charMap) {
    // Split the string into an array of characters
    let charArray = str.split('');

    // Map the characters based on the charMap
    let replacedArray = charArray.map(char => {
        return charMap[char] || char;  // Replace with mapped char or keep the original if no mapping exists
    });

    // Join the array back into a string
    return replacedArray.join('');
}

let persianCharsMap = {
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9',
}

async function getHolidays(year, month) {
    var reqBody = `Year=${year}&Month=${month}&Base1=0&Base2=1&Base3=2&Responsive=true`;

    var response = await fetch("https://www.time.ir/", {
        "headers": {
            "accept": "*/*",
            "accept-language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            // "priority": "u=1, i",
            // "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            // "sec-ch-ua-mobile": "?1",
            // "sec-ch-ua-platform": "\"Android\"",
            // "sec-fetch-dest": "empty",
            // "sec-fetch-mode": "cors",
            // "sec-fetch-site": "same-origin",
            // "x-requested-with": "XMLHttpRequest",
            // "Referer": "https://www.time.ir/",
            // "Referrer-Policy": "strict-origin-when-cross-origin"
        },
        "body": reqBody,
        "method": "POST"
    });

    var body = await response.text();


    // fs.writeFile('./ab.html', body, err => {
    //     if (err) {
    //       console.error(err);
    //     } else {
    //       // file written successfully
    //     }
    //   });

    const linkXPath = '//*[contains(@class, \'dayList\')]/div[not(contains(@class, \'disabled\'))]/div[contains(@class, \'holiday\')]/div[contains(@class, \'jalali\')]';

    let doc = new dom().parseFromString(body, 'text/xml');
    let nodes = xpath.select(linkXPath, doc);

    let holidays = [];

    nodes.forEach(element => {
        let dayText = element.textContent;
        dayText = replaceChars(dayText, persianCharsMap);
        let day = Number(dayText);
        holidays.push(day);
    });

    return holidays;
}


const esfa_persian_holidays = {
    getHolidays: getHolidays
};

module.exports = esfa_persian_holidays;
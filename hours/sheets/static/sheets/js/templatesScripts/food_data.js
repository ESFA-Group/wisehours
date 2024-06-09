"use strict";
//CONSTANTS************************************************
const TODAY = new JDate();
// const TODAY = new JDate(1403, 2, 22);


const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH



const foods = [
	{
		num: 0,
		name: "باقالی پلو",
		price: 1400000,
	},
	{
		num: 1,
		name: "چلو کباب کوبیده",
		price: 1400000,
	},
	{
		num: 2,
		name: "چلو جوجه کباب",
		price: 1400000,
	},
	{
		num: 3,
		name: "چلو قیمه",
		price: 1400000,
	},
	{
		num: 4,
		name: "چلو قورمه",
		price: 1400000,
	},
	{
		num: 5,
		name: "زرشک پلو با مرغ",
		price: 1400000,
	},
	{
		num: 6,
		name: "خوراک",
		price: 1400000
	},
	{
		num: 7,
		name: "الویه",
		price: 1400000
	},
	{
		num: 8,
		name: "کشک بادمجان",
		price: 1400000
	},
	{
		num: 9,
		name: "ماست",
		price: 1400000
	},
	{
		num: 10,
		name: "زیتون",
		price: 1400000
	},
]

// ********************************************************

function fillYears() {
	for (let i = window.START_YEAR; i <= ACTIVE_YEAR; i++) {
		$("#year").append($("<option>").text(i));
	}
}

async function getDBTable(url) {
	try {
		let res = await fetch(url);
		return await res.json();
	}
	catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Fetching This month's Sheet",
			message: err,
		});
	}
}

async function getSheetDBT(year, month) {
	const url = `/hours/api/sheets/${year}/${month}`;
	return await getDBTable(url)
}


async function getFoodDataDBT(year, month) {
	return [
		{ "day": 1, "data": [{ "id": 0, "name": "steakd", "price": 250 }, { "id": 1, "name": "kebab", "price": 100 }, { "id": 2, "name": "chicken", "price": 80 }, { "id": 3, "name": "coca", "price": 10 }] },
		{ "day": 17, "data": [{ "id": 0, "name": "steakd", "price": 500 }, { "id": 1, "name": "kebab", "price": 222 }, { "id": 2, "name": "chicken", "price": 150 }, { "id": 3, "name": "coca", "price": 21 }] }
	];
}

function saveFoodDataDBT(fooddata){
	
}

async function renderSheet(food_data) {
	resetFoodSheet();

	const foodColumns = food_data[0].data.map(foodItem => ({
		type: 'numeric',
		title: foodItem.name,
		width: 130,
		readOnly: false
	}));

	const columns = [
		{ type: 'text', title: 'Day', width: 80, readOnly: true },
		{ type: 'text', title: 'WeekDay', width: 130, readOnly: true },
		...foodColumns
	];


	let monthdata = await getSheetDBT(ACTIVE_YEAR, ACTIVE_MONTH)

	let foodSheetData = mergeMonthDataWithFoodData(monthdata.data, food_data)

	window.spreadTable = jspreadsheet(document.getElementById('spreadsheet'), {
		data: foodSheetData,
		columns: columns,
		allowInsertColumn: false,
		allowInsertRow: false,
		allowDeleteRow: false,
		allowRenameColumn: false,
		onundo: onChangeHandler,
		onredo: onChangeHandler,
		onchange: (worksheet, cell, x, y, value) => onChangeHandler(worksheet, cell, x, y, value, foodSheetData, food_data),
		ondeletecolumn: onChangeHandler,
		onselection: onselectionHandler,
		tableOverflow: true,
		tableHeight: "100vh",
		updateTable: function (el, cell, x, y, source, value, id) {
			if (value == "Fri") {
				cell.style.color = 'red';
			}

			const todayIndex = TODAY.getDate() - 1; // Example: disable rows 1, 3, and 5
			if (y < todayIndex) {
				cell.classList.add('readonly');
				cell.setAttribute('readonly', 'readonly');
			}
		}
	});
	window.spreadTable.hideIndex();

}

function resetFoodSheet() {
	if (typeof window.spreadTable === 'object') {
		window.spreadTable.destroy();
	}
}

function onChangeHandler(worksheet, cell, x, y, value, foodSheetData, food_data) {
	const rawData = window.spreadTable.getJson();
	const tableData = convertTableData(rawData);
	const currentValue = foodSheetData[y][food_data[0].data[x - 2].name];
	if (+value === currentValue) {
		return;
	}
	const foodid = x - 2;
	const day = +y + 1;

	let index;
	if ((index = food_data.findIndex(item => item.day === day)) !== -1) {
		let last_data = food_data.at(index).data;
		last_data[foodid].price = +value;
		removeDuplicates(food_data)
		saveFoodDataDBT(fooddata);
		renderSheet(food_data);
	}
	else if (day < food_data.at(-1).day) {
		const newItem = findAndCopyLastLessThan(food_data, day);
		newItem.day = day;
		newItem.data[foodid].price = +value;
		food_data.push(newItem)
		food_data.sort((a, b) => a.day - b.day);
		saveFoodDataDBT(fooddata);
		renderSheet(food_data);
	}
	else {
		let new_data = JSON.parse(JSON.stringify(food_data.at(-1)));
		new_data.day = day;
		new_data.data[foodid].price = +value;
		food_data.push(new_data);
		saveFoodDataDBT(fooddata);
		renderSheet(food_data);
	}
}

function removeDuplicates(data) {
	data.forEach((item, index) => {
		if (index === data.length - 1) return;

		const currentItemData = JSON.stringify(item.data);
		const nextItemData = JSON.stringify(data[index + 1].data);

		if (currentItemData === nextItemData) {
			// Remove the item with the greater day value
			if (item.day > data[index + 1].day) {
				data.splice(index, 1);
			} else {
				data.splice(index + 1, 1);
			}
		}
	});
	return data
}

function findAndCopyLastLessThan(array, newDay) {
	for (let i = array.length - 1; i >= 0; i--) {
		const item = array[i];

		if (item.day < newDay) {
			return JSON.parse(JSON.stringify(item));
		}
	}
	return null;
}

function convertTableData(rawData) {
	/*  table's getJson method won't return table data correctly, some headers (mostly created ones in project adding) 
		are wrong in each rows data. this function iterates each row and correct wrong keys to real keys in header.
	*/
	const headers = window.spreadTable.getHeaders(true);
	rawData.map(row => {
		for (let [key, value] of Object.entries(row)) {
			if (!headers.includes(key)) {
				row[headers[key]] = value;
				delete row[key];
			}
		}
	})
	return rawData
}

function onselectionHandler(worksheet, px, py, ux, uy, origin) {
	// scroll to element while working with arrow keys or sth when selected element is out of viewport
	const td = $(worksheet).find('td.highlight-selected.highlight').get(0);
	if (td === undefined)
		return false
	const box = td.getBoundingClientRect();
	if (box.top > window.innerHeight || box.bottom <= 0)
		td.scrollIntoView();
}

function mergeMonthDataWithFoodData(monthData, foodData) {
	const foodMap = new Map(foodData.map(item => [item.day, item.data]));
	let lastFoodData = [];
	let lastFoodPairs = {};

	return monthData.map(({ Day, WeekDay }) => {
		if (foodMap.has(Day)) {
			lastFoodData = foodMap.get(Day);
			lastFoodPairs = lastFoodData.reduce((acc, { name, price }) => {
				acc[name] = price;
				return acc;
			}, {});
		}

		return { Day, WeekDay, ...lastFoodPairs };
	});
}



$("document").ready(async function () {
	fillYears(ACTIVE_YEAR);
	const food_data = await getFoodDataDBT(ACTIVE_YEAR, ACTIVE_MONTH)
	renderSheet(food_data)
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);


	$("#year, #month").change(function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
	});
});

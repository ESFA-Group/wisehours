"use strict";
//CONSTANTS************************************************
// const TODAY = new JDate(1403, 2, 22);
const TODAY = new JDate();

const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

const CURRENT_MONTH_WEEKS = getWeeksOfMonth()
var ACTIVE_MONTH_WEEKS = CURRENT_MONTH_WEEKS

const [CURRENT_WEEK, CURRENT_WEEK_INDEX] = getCurrentWeek()
var ACTIVE_WEEK = CURRENT_WEEK
var ACTIVE_WEEK_INDEX = CURRENT_WEEK_INDEX


// const foods = [
// 	{
// 		num: 0,
// 		name: "باقالی پلو",
// 		price: 1400000,
// 	},
// 	{
// 		num: 1,
// 		name: "چلو کباب کوبیده",
// 		price: 1400000,
// 	},
// 	{
// 		num: 2,
// 		name: "چلو جوجه کباب",
// 		price: 1400000,
// 	},
// 	{
// 		num: 3,
// 		name: "چلو قیمه",
// 		price: 1400000,
// 	},
// 	{
// 		num: 4,
// 		name: "چلو قورمه",
// 		price: 1400000,
// 	},
// 	{
// 		num: 5,
// 		name: "زرشک پلو با مرغ",
// 		price: 1400000,
// 	},
// 	{
// 		num: 6,
// 		name: "خوراک",
// 		price: 1400000
// 	},
// 	{
// 		num: 7,
// 		name: "الویه",
// 		price: 1400000
// 	},
// 	{
// 		num: 8,
// 		name: "کشک بادمجان",
// 		price: 1400000
// 	},
// 	{
// 		num: 9,
// 		name: "ماست",
// 		price: 1400000
// 	},
// 	{
// 		num: 10,
// 		name: "زیتون",
// 		price: 1400000
// 	},
// ]

const weekdays = [
	'شنبه',
	'یک‌شنبه',
	'دوشنبه',
	'سه‌شنبه',
	'چهارشنبه',
	'پنج‌شنبه',
	'جمعه',
]
// ********************************************************

async function getRequest(url) {
	try {
		let response = await fetch(url);
		return await response.json();
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

async function getFoodDataDBT(year = ACTIVE_YEAR, month = ACTIVE_MONTH) {
	const url = `/hours/api/FoodManagement/${year}/${month}`;
	return await getRequest(url)
}


function fillYears() {
	for (let i = window.START_YEAR; i <= ACTIVE_YEAR; i++) {
		$("#year").append($("<option>").text(i));
	}
}

function fillWeeks() {
	let weeks = getWeeksOfMonth()
	$("#week").empty();
	for (let i = 0; i < weeks.length; i++) {
		$("#week").append($("<option>")
			.text(`week${i + 1} (${weeks[i]['0'].format('MM/DD')} --> ${weeks[i]['6'].format('MM/DD')})`)
			.val(i));
	}
}

function getWeeksOfMonth() {
	let year = ACTIVE_YEAR
	let month = ACTIVE_MONTH
	const totalDaysInMonth = JDate.daysInMonth(year, month);

	let weeksDate = []
	let shouldbreak = false;
	for (let i = 1; i <= totalDaysInMonth; i++) {
		if (shouldbreak) {
			break;
		}
		let startDate = new JDate(year, month, i);
		if (startDate.getDay() === 6) {
			weeksDate.push({
				0: startDate
			})
			for (let j = 1; j < 7; j++) {
				i = i + 1
				if (i > totalDaysInMonth) {
					month += 1;
					if (month > 12) {
						year += 1
						month = 1
					}
					i = 1;
					startDate = new JDate(year, month, i);

					weeksDate[weeksDate.length - 1][j] = startDate;
					shouldbreak = true;
					continue;
				}
				startDate = new JDate(year, month, i);
				weeksDate[weeksDate.length - 1][j] = startDate;
			}
		}
	}
	return weeksDate;
}

function getCurrentWeek() {
	for (const [index, week] of Object.entries(CURRENT_MONTH_WEEKS)) {
		let startweekday = week[0]
		let dayDiff = getDayDiff(TODAY, startweekday)
		if (dayDiff <= 0 && dayDiff >= -6) {
			return [week, index];
		}
	};
}

function getDayDiff(JDate1, JDate2) {
	let diff = JDate2._d.getTime() - JDate1._d.getTime()
	return Math.round(diff / (1000 * 60 * 60 * 24));
}

async function initializeFoodTable() {
	$("#foodTable tbody").empty();
	$("#foodTable thead tr").remove();
	let foods = await getFoodDataDBT()

	let foodData = findLastFoodPriceDataOfTheWeek(foods)
	fillFoodTableHeader(foodData.data)
	fillFoodTablebody()
}

function findLastFoodPriceDataOfTheWeek(dailyFoodsData) {
	let currentWeekFirstDay = ACTIVE_WEEK[0].getDate();
	for (let i = dailyFoodsData.length - 1; i >= 0; i--) {
		const foodData = dailyFoodsData[i];
		if( foodData.day <= currentWeekFirstDay)
			return foodData;
	}
}

function fillFoodTableHeader(foods) {

	var headersRow = $("<tr>");
	headersRow.append($("<th>").text("غذا \\ روز"));


	foods.forEach(function (food) {
		headersRow.append($("<th>", { dataField: food.name }).html(`${food.name}<br>${food.price.toLocaleString('en-US')}`));
	});
	$("#foodTable thead").append(headersRow);
}
function fillFoodTablebody() {
	for (const [index, day] of Object.entries(ACTIVE_WEEK)) {
		var row = $("<tr>");

		// Add day cell
		row.append($(`<td>${day.format("dddd")}</td>`).val(day.date[2]));

		const headerCount = $("#foodTable thead tr th").length
		for (let i = 1; i < headerCount; i++) {
			var cellContent = $("<span>");
			cellContent.append($("<input>", {
				type: "checkbox",
				class: "cell-checkbox",
			}));
			row.append($("<td>").append(cellContent));
		}

		$("#foodTable tbody").append(row);
	}
}

async function fillFoodTable() {

	const food_data = await getFoodData()
	if (food_data.length == 0) {
		return;
	}

	let activeWeek_food_data = food_data[ACTIVE_WEEK_INDEX]
	const [header, ...rows] = $('#foodTable tr')

	activeWeek_food_data.forEach(dayfood => {
		const matchingRow = rows.filter(r => r.cells[0].value == dayfood.day)[0];
		if (matchingRow !== undefined) {
			const [day, ...checkboxes] = matchingRow.cells;
			for (const food of dayfood.foods) {
				var checkbox = checkboxes[food].querySelector('input[type="checkbox"]');
				checkbox['checked'] = true;
				continue;
			}
		}
	});
}

async function getFoodData() {
	const url = `/hours/api/order_food/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	try {
		let res = await fetch(url);
		return await res.json();
	}
	catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Fetching Projects",
			message: err,
			timeout: 6000,
		});
	}
}

async function submitSelectedFoods() {
	$("#submit-food-spinner").removeClass('d-none');
	$("#submitFoodBtn").prop('disabled', true)
	const currentWeekSelectedFood = getSelectedFoodsFromTable();

	saveFoodData(currentWeekSelectedFood);
}


function saveFoodData(data) {
	const url = `/hours/api/order_food/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;

	fetch(url, {
		method: 'post',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': window.CSRF_TOKEN,
		},
		body: JSON.stringify({ "data": data, "index": ACTIVE_WEEK_INDEX }),
	})
		.then(res => res.json())
		.then(() => {
			$("#submit-food-spinner").addClass('d-none');
			$("#submitFoodBtn").prop('disabled', false);
		})
		.catch(err => {
			$("#submit-food-spinner").addClass('d-none');
			$("#submitFoodBtn").prop('disabled', false);
			
			jSuites.notification({
				error: 1,
				name: 'Error',
				title: "Updating Sheet",
				message: err,
			});
		});
}


function getSelectedFoodsFromTable() {
	let currentWeekSelectedFood = [];
	const [headerRow, ...bodyRows] = $('#foodTable tr');

	for (const row of bodyRows) {
		let selectedFoodsInRow = [];
		const [day, ...checkboxes] = row.cells;
		checkboxes.forEach((c, i) => {
			if (c.querySelector('input[type="checkbox"]').checked) {
				selectedFoodsInRow.push(i);
			}
		});
		currentWeekSelectedFood.push({ "day": day.value, "foods": [...selectedFoodsInRow] });
	}
	return currentWeekSelectedFood;
}

function handleChangeWeek() {
	ACTIVE_WEEK_INDEX = $("#week").val();
	ACTIVE_WEEK = ACTIVE_MONTH_WEEKS[ACTIVE_WEEK_INDEX];
	initializeFoodTable()
	fillFoodTable();
}

$("document").ready(async function () {

	fillYears(ACTIVE_YEAR);
	fillWeeks();
	initializeFoodTable()
	fillFoodTable()
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);
	$("#week").val(CURRENT_WEEK_INDEX);

	$("#current-sheet-date").text(`${ACTIVE_YEAR}/${ACTIVE_MONTH}`);



	$("#year, #month").change(function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		fillWeeks();
		handleChangeWeek()
	});
	$("#week").change(function () {
		handleChangeWeek();
	});

	$("#foodTable tbody").on("click", "td", function(e) {
		if (!$(e.target).is('.cell-checkbox')) {
			var $checkbox = $(this).find('.cell-checkbox');
			$checkbox.prop('checked', !$checkbox.prop('checked'));
		}
	});

	$("#submitFoodBtn").on("click", async function () {
		await submitSelectedFoods()
	});
});

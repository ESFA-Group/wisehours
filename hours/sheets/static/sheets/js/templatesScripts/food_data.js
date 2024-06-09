"use strict";
//CONSTANTS************************************************
// const TODAY = new JDate();
const TODAY = new JDate(1403, 2, 22);


const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

const CURRENT_MONTH_WEEKS = getWeeksOfMonth()
var ACTIVE_MONTH_WEEKS = CURRENT_MONTH_WEEKS

const [CURRENT_WEEK, CURRENT_WEEK_INDEX] = getCurrentWeek()
var ACTIVE_WEEK = CURRENT_WEEK
var ACTIVE_WEEK_INDEX = CURRENT_WEEK_INDEX



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

function handleChangeWeek() {
	ACTIVE_WEEK_INDEX = $("#week").val();
	ACTIVE_WEEK = ACTIVE_MONTH_WEEKS[ACTIVE_WEEK_INDEX];
	initializeFoodTable()
	fillFoodTable();
}

$("document").ready(async function () {
	fillYears(ACTIVE_YEAR);
	fillWeeks();
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);
	$("#week").val(CURRENT_WEEK_INDEX);


	$("#year, #month").change(function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		fillWeeks();
		handleChangeWeek()
	});
	$("#week").change(function () {
		handleChangeWeek();
	});
});

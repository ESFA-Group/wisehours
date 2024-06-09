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




foods = [
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

var weekdays = [
	'شنبه',
	'یک‌شنبه',
	'دوشنبه',
	'سه‌شنبه',
	'چهارشنبه',
	'پنج‌شنبه',
	'جمعه',
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
	shouldbreak = false;
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
		dayDiff = getDayDiff(TODAY, startweekday)
		if (dayDiff <= 0 && dayDiff >= -6) {
			return [week, index];
		}
	};
}

function getDayDiff(JDate1, JDate2) {
	diff = JDate2._d.getTime() - JDate1._d.getTime()
	return Math.round(diff / (1000 * 60 * 60 * 24));
}

function initializeFoodTable() {
	$("#foodTable tbody").empty();
	$("#foodTable thead tr").remove();

	fillFoodTableHeader()
	fillFoodTablebody()
}

function fillFoodTableHeader() {
	var headersRow = $("<tr>");
	headersRow.append($("<th>").text("غذا \\ روز"));


	foods.forEach(function (food) {
		headersRow.append($("<th>", { dataField: food.name }).text(food.name));
	});
	$("#foodTable thead").append(headersRow);
}
function fillFoodTablebody() {
	for (const [index, day] of Object.entries(ACTIVE_WEEK)) {
		var row = $("<tr>");

		// Add day cell
		row.append($("<td>").text(day.format("dddd")).val(day.date[2]));

		foods.forEach(food => {
			var cellContent = $("<span>");
			cellContent.append($("<input>", {
				type: "checkbox",
				class: "cell-checkbox",
			}));
			row.append($("<td>").append(cellContent));
		})

		$("#foodTable tbody").append(row);
	}
}

function fillFoodTable() {

	// const food_data = getFoodData(ACTIVE_YEAR, ACTIVE_MONTH)
	// const food_data = [
	// 	{ "day": 1, "foods": [0, 9] },
	// 	{ "day": 2, "foods": [1, 8] },
	// 	{ "day": 3, "foods": [5, 8, 9] },
	// 	{ "day": 6, "foods": [7, 9] },
	// 	{ "day": 7, "foods": [4] },
	// 	{ "day": 11, "foods": [1, 8] },
	// 	{ "day": 12, "foods": [2, 8] },
	// 	{ "day": 13, "foods": [3, 9] },
	// 	{ "day": 16, "foods": [0, 10] }
	// ]
	const food_data = [
		[
			{ "day": 5, "foods": [0, 9] },
			{ "day": 6, "foods": [5, 8, 9] },
			{ "day": 7, "foods": [1, 8] },
			{ "day": 9, "foods": [7, 9] }
		],
		[
			{ "day": 12, "foods": [0, 9] },
			{ "day": 13, "foods": [2] },
			{ "day": 14, "foods": [5, 8, 10] },
			{ "day": 16, "foods": [7, 9] }
		],
		[
			{ "day": 19, "foods": [1, 8] },
			{ "day": 20, "foods": [2, 8] },
			{ "day": 21, "foods": [3, 9] },
			{ "day": 22, "foods": [0, 10] },
			{ "day": 25, "foods": [0, 10] }
		],
		[
			{ "day": 26, "foods": [0, 9] },
			{ "day": 27, "foods": [2, 8] },
			{ "day": 28, "foods": [3] },
			{ "day": 1, "foods": [0, 10] }
		]
	]

	activeWeek_food_data = food_data[ACTIVE_WEEK_INDEX]
	let rows = $('#foodTable tr')

	activeWeek_food_data.forEach(dayfood => {
		const matchingRow = rows.filter((i, r) => r.cells[0].value == dayfood.day)[0];
		if (matchingRow !== undefined) {
			[day, ...checkboxes] = matchingRow.cells;
			for (const food of dayfood.foods) {
				var checkbox = checkboxes[food].querySelector('input[type="checkbox"]');
				checkbox['checked'] = true;
				continue;
			}
		}
	});

}

function submitSelectedFoods() {
	selectedFood = []
	selectedFood = [
		{ "day": 1, "foods": [0, 9] },
		{ "day": 2, "foods": [1, 8] },
		{ "day": 3, "foods": [5, 8, 9] },
		{ "day": 6, "foods": [7, 9] },
		{ "day": 7, "foods": [4] },
		{ "day": 11, "foods": [1, 8] },
		{ "day": 12, "foods": [2, 8] },
		{ "day": 13, "foods": [3, 9] },
		{ "day": 16, "foods": [0, 10] }
	]

	const table = $('#foodTable')[0]
	const tableRows = table.rows
	for (let i = 1; i < tableRows.length; i++) {
		const row = tableRows[i];

	}
	tableRows.forEach(row => {

	});
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

	$('.cell-checkbox').parent().parent().click(function (e) {
		if ($(e.target).is('.cell-checkbox')) {
			return;
		}
		var $this = $(this);
		$this.find('.cell-checkbox').prop('checked', !$this.find('.cell-checkbox').prop('checked'));
	});

	$("#submitFood").on("click", function () {
		selectedFoodObject = submitSelectedFoods()
		alert("Button clicked!");
	});
});

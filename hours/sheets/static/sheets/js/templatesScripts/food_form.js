foods = [
	{
		name: "چلو کباب کوبیده",
		price: 1400000,
	},
	{
		name: "چلو جوجه کباب",
		price: 1400000,
	},
	{
		name: "چلو قیمه",
		price: 1400000,
	},
	{
		name: "چلو قورمه",
		price: 1400000,
	},
	{
		name: "زرشک پلو با مرغ",
		price: 1400000,
	},
	{
		name: "خوراک",
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


function fillYears(year) {
	for (let i = window.START_YEAR; i <= year; i++) {
		$("#year").append($("<option>").text(i));
	}
}

function fillWeeks(year, month) {
	let weeks = getWeeksOfMonth(year, month)
	$("#week").empty();
	for (let i = 0; i < weeks.length; i++) {
		$("#week").append($("<option>").text(`week${i + 1} (${weeks[i]['0'].format('MM/DD')} --> ${weeks[i]['6'].format('MM/DD')})`));
	}
}

function getWeeksOfMonth(year, month) {
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
				i = i+1
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

function fillFoodTable() {
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
	weekdays.forEach(day => {
		var row = $("<tr>");

		// Add day cell
		row.append($("<td>").text(day));

		foods.forEach(food => {
			var cellContent = $("<span>");
			cellContent.append($("<input>", {
				type: "checkbox",
				class: "cell-checkbox",
			}));
			row.append($("<td>").append(cellContent));
		})

		$("#foodTable tbody").append(row);

	});
}

function getSelectedFoods() {
	selectedFood = []
	selectedFood = [
		{ day: 0, selectedFoods: [0] },
		{ day: 1, selectedFoods: [1, 2] },
		{ day: 2, selectedFoods: [5] },
		{ day: 3, selectedFoods: [] },
		{ day: 4, selectedFoods: [4] },
		{ day: 6, selectedFoods: [1, 5] },
	]

	const table = $('#foodTable')[0]
	const tableRows = table.rows
	for (let i = 1; i < tableRows.length; i++) {
		const row = tableRows[i];

	}
	tableRows.forEach(row => {

	});
}

$("document").ready(async function () {
	const today = new JDate();
	const currentYear = today.getFullYear();
	const currentMonth = today.getMonth();
	fillYears(currentYear);
	fillWeeks(currentYear, currentMonth);
	fillFoodTable()
	$("#year").val(currentYear);
	$("#month").val(currentMonth);
	$("#current-sheet-date").text(`${currentYear}/${currentMonth}`);



	$("#year, #month").change(function () {
		fillWeeks($("#year").val(), $("#month").val());
	});

	$('.cell-checkbox').parent().parent().click(function (e) {
		if ($(e.target).is('.cell-checkbox')) {
			return;
		}
		var $this = $(this);
		$this.find('.cell-checkbox').prop('checked', !$this.find('.cell-checkbox').prop('checked'));
	});

	$("#submitFood").on("click", function () {
		selectedFoodObject = getSelectedFoods()
		alert("Button clicked!");
	});
});
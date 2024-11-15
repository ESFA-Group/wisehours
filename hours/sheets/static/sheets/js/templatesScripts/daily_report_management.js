"use strict";
//CONSTANTS************************************************
const TODAY = new JDate();
TODAY._d.setHours(0, 0, 0, 0)
let is_main_commenter = false;
let ActiveUser = "";

const CURRENT_YEAR = TODAY.getFullYear();
var ACTIVE_YEAR = CURRENT_YEAR;

const CURRENT_MONTH = TODAY.getMonth();
var ACTIVE_MONTH = CURRENT_MONTH

var ACTIVE_DAY = TODAY.getDate();
// ********************************************************

function fillYears(yearId, year = CURRENT_YEAR) {
	$(yearId).empty();
	for (let i = window.START_YEAR; i <= year; i++) {
		$(yearId).append($("<option>").text(i));
	}
}

function initialize_date_dropdowns() {
	$("#year").val(ACTIVE_YEAR);
	$("#month").val(ACTIVE_MONTH);
	$("#day").val(ACTIVE_DAY);
}


//#region API-Request 
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

async function postRequest(url, data) {
	try {
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': window.CSRF_TOKEN,
			},
			body: JSON.stringify(data)
		});
		return await response.json()
	} catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Updating Sheet",
			message: err,
		});
	}
}

async function putRequest(url, data) {
	try {
		const response = await fetch(url, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': window.CSRF_TOKEN,
			},
			body: JSON.stringify(data)
		});
		return await response.json()
	} catch (err) {
		jSuites.notification({
			error: 1,
			name: 'Error',
			title: "Updating Sheet",
			message: err,
		});
	}
}
//#endregion

async function get_reports_by_users() {
	const url = `/hours/api/daily_report_management/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;
	return await getRequest(url);
}

function updateTitle() {
	$("#reportTitle").text("Submit Report " + $("#month").val() + "/" + $("#day").val());
}

async function get_all_daily_reports() {
	let res = await get_reports_by_users();
	let reports_by_users = res['data']
	is_main_commenter = res['user']['is_MainReportManager']
	pre_load_user_reports();

	const $userList = $('#userList');
	$.each(reports_by_users, function (userName, reports) {
		const listItem = $('<li></li>')
			.addClass('list-group-item user-item')
			.text(`${userName} (${reports.length} reports)`)
			.attr('data-user-id', userName);

		// Append the list item to the user list
		$userList.append(listItem);

		// Add a click event to each list item
		listItem.on('click', function () {
			$('.user-item').removeClass('active');
			$(this).addClass('active');
			pre_load_user_reports()
			ActiveUser = userName;
			load_user_reports(userName, reports);
		});

		if (Object.keys(reports_by_users).indexOf(userName) === 0) {
			ActiveUser = userName;
			listItem.addClass('active');
		}
	});

	if (Object.keys(reports_by_users).length > 0) {
		const firstUser = Object.keys(reports_by_users)[0];
		const firstReports = reports_by_users[firstUser];
		load_user_reports(firstUser, firstReports);
	}
}

function pre_load_user_reports() {
	const $reportsContainer = $('#reports_container');
	$reportsContainer.empty()
	for (let day = TODAY.getDate(); day >= 1; day--) {
		let reportHtml = `
			<div id="report_${day}" class="border p-2 mb-1 missed-report" style="border-radius: 8px;">
				<div class="card shadow mb-4">
					<div class="card-body">
						<h4 class="card-title fw-bold">Report #${day}</h4>
						<div class="mb-3">
							<p id="report_content_${day}" name="content" class="form-control"></p>
						</div>
					</div>
				</div>
		`;

		if (is_main_commenter) {
			reportHtml += `
				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Vahid's Comment:</h5>
						<div class="mb-3">
							<textarea id="main_comment_${day}" name="content" class="form-control" placeholder="Enter your comment here" rows="4" required></textarea>
						</div>
					</div>
				</div>

				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Koolaji's Comment:</h5>
						<p id="sub_comment_${day}">No comment yet.</p>
					</div>
				</div>
			`;
		} else {
			reportHtml += `
				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Vahid's Comment:</h5>
						<p id="main_comment_${day}">No comment yet.</p>
					</div>
				</div>

				<div class="card shadow mb-4">
					<div class="card-body">
						<h5 class="card-title fw-semibold">Koolaji's Comment:</h5>
						<div class="mb-3">
							<textarea id="sub_comment_${day}" name="content" class="form-control" placeholder="Enter your comment here" rows="4" required></textarea>
						</div>
					</div>
				</div>
			`;
		}

		reportHtml += `
			</div>
			<button id="submitReportBtn_${day}" class="submit_comment_btn btn btn-primary d-flex mb-3 justify-content-center align-items-center position-relative" type="submit" onclick="handleReportSubmit(${day})">
				<span id="submit-report-spinner_${day}" class="spinner-border spinner-border-sm d-none me-1" role="status"></span>
				<span>Submit Report</span>
				<div id="submit-report-check_${day}" class="bg-primary d-none" desabled>
					✅
				</div>
			</button>
			
			<br/>
		`;

		$reportsContainer.append(reportHtml);
	}
}

async function handleReportSubmit(day) {

	disable_btns(day)

	let main_comment = "";
	let sub_comment = "";

	if (is_main_commenter) {
		main_comment = $(`#main_comment_${day}`).val();
	}
	else {
		sub_comment = $(`#sub_comment_${day}`).val();
	}

	const url = `/hours/api/daily_report_management/${ACTIVE_YEAR}/${ACTIVE_MONTH}`;

	const data = {
		userName: ActiveUser,
		day: day,
		main_comment: main_comment,
		sub_comment: sub_comment
	}

	await postRequest(url, data)
	enable_btns(day)
}

function disable_btns(day) {
	$('.submit_comment_btn').prop('disabled', true);

	$(`#submit-report-spinner_${day}`).removeClass('d-none');
}

function enable_btns(day) {
	$('.submit_comment_btn').prop('disabled', false);
	$(`#submit-report-spinner_${day}`).addClass('d-none');
	$(`#submit-report-check_${day}`).removeClass('d-none').fadeIn(500, function () {
		// After fade in, fade out afttn_${daer a delay
		setTimeout(() => {
			$(`#submit-report-check_${day}`).fadeOut(500, function () {
				$(this).addClass('d-none').css('display', '');
			});
		}, 1000); // Delay before fading out
	});
}


function load_user_reports(userName, reports) {
	// Update the report title
	$('#reportTitle').text(`${userName}'s Reports`);

	reports.forEach(r => {
		let day = r.day
		if (r.content !== null && r.content.trim() !== "") {
			$('#report_' + day).removeClass("missed-report")
			$('#report_' + day).addClass("submitted-report")
			$(`#report_content_${day}`).text(r.content);
		}
		$(`#main_comment_${day}`).text(r.main_comment);
		$(`#sub_comment_${day}`).text(r.sub_comment);
	});

	// Clear existing report content
	$('#main_comment').text('');
	$('#sub_comment').text('');

	// Display the reports (example with the first two reports if available)
	if (reports.length > 0) {
		$('#main_comment').text(reports[0]?.content || 'No comment yet.');
	}
	if (reports.length > 1) {
		$('#sub_comment').text(reports[1]?.content || 'No comment yet.');
	}
}

$("document").ready(async function () {
	fillYears("#year");
	initialize_date_dropdowns();
	get_all_daily_reports();

	$("#year, #month").change(async function () {
		ACTIVE_YEAR = $("#year").val()
		ACTIVE_MONTH = $("#month").val()
		get_all_daily_reports();
	});

	$("#day").change(async function () {
		ACTIVE_DAY = $("#day").val();
		get_all_daily_reports();
	});
});

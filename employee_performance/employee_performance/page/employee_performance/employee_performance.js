// Global store for chart instances to allow proper updating without DOM errors
let epd_charts = {
    main_dist: null,
    leads_pulse: null,
    attendance_donut: null
};

frappe.pages['employee-performance'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Employee Performance'),
        single_column: true
    });

    render_layout(page);
    init_dashboard(page);
};

function render_layout(page) {
    let $parent = $(page.body);
    $parent.empty();

    let greeting = get_dynamic_greeting();

    let html = `
		<div class="epd-dashboard">
			<!-- Top Header -->
			<div class="epd-header">
				<div class="epd-greeting">
					<h1 id="epd-greeting-text">${greeting}</h1>
					<p id="epd-date-range-label">${__('Select a date range and click Apply.')}</p>
				</div>
				<div class="epd-filter-row">
					<div class="epd-filter-field" id="employee-selector-container"></div>
					<div class="epd-date-field">
						<label class="epd-date-label">${__('From')}</label>
						<input type="date" id="epd-from-date" class="epd-date-input">
					</div>
					<div class="epd-date-field">
						<label class="epd-date-label">${__('To')}</label>
						<input type="date" id="epd-to-date" class="epd-date-input">
					</div>
					<button class="btn btn-primary btn-sm epd-apply-btn" id="epd-apply-btn">
						<i class="fa fa-check" style="margin-right:5px;"></i>${__('Apply')}
					</button>
				</div>
			</div>

			<!-- 4-Card KPI Grid -->
			<div class="epd-kpi-grid">
				<div class="kpi-card bg-teal">
					<div class="card-value" data-field="total_leads">0</div>
					<div class="card-label">${__("Total Leads")}</div>
					<i class="fa fa-user-plus card-icon" style="opacity: 0.2;"></i>
				</div>
				<div class="kpi-card bg-orange">
					<div class="card-value" data-field="total_opportunities">0</div>
					<div class="card-label">${__("Opportunities")}</div>
					<i class="fa fa-lightbulb card-icon" style="opacity: 0.2;"></i>
				</div>
				<div class="kpi-card bg-blue">
					<div class="card-value" data-field="active_customers">0</div>
					<div class="card-label">${__("Customers")}</div>
					<i class="fa fa-user-check card-icon" style="opacity: 0.2;"></i>
				</div>
				<div class="kpi-card bg-purple">
					<div class="card-value" data-field="conversion_rate">0%</div>
					<div class="card-label">${__("Conversion Rate")}</div>
					<i class="fa fa-percentage card-icon" style="opacity: 0.2;"></i>
				</div>
			</div>

			<!-- Main Content: Horizontal Split -->
			<div class="epd-main-row">
				<!-- Left: Events & Trend -->
				<div class="epd-content-section">
					<div class="section-title">
						<span id="events-section-title">${__("Activity Distribution")}</span>
						<span>${__("Events & Categories")}</span>
					</div>
					<div id="main-distribution-chart" style="height: 350px; min-height: 350px;"></div>

                    <div style="margin-top: 40px;">
                        <div class="section-title">${__("Leads Pulse")}</div>
                        <div id="leads-pulse-chart" style="height: 200px; min-height: 200px;"></div>
                    </div>
				</div>

				<!-- Right: Attendance & Log -->
				<div class="epd-content-section">
					<div class="section-title">${__("Attendance Overview")}</div>
					<div id="attendance-donut-chart" style="height: 280px; min-height: 280px;"></div>
					
					<div class="epd-table-container" style="margin-top: 20px;">
						<div class="section-title">${__("Recent Activity Log")}</div>
                        <div class="compact-timeline" id="checkin-timeline" style="min-height: 100px;"></div>
					</div>
				</div>
			</div>

            <!-- Bottom Row: Multi-Column Performance Table -->
            <div class="epd-table-container" style="margin-top: 20px;">
                <div class="epd-content-section">
                    <div class="section-title">${__("Comprehensive Performance Metrics")}</div>
                    <table class="epd-table">
                        <thead>
                            <tr>
                                <th>${__("Indicator")}</th>
                                <th>${__("Value")}</th>
                                <th>${__("Description")}</th>
                            </tr>
                        </thead>
                        <tbody id="performance-body">
                            <tr>
                                <td><div class="emp-name">${__("Total Attendance")}</div></td>
                                <td data-field="attendance_total">0</td>
                                <td><div class="emp-meta">${__("Total present days in selected period.")}</div></td>
                            </tr>
                            <tr>
                                <td><div class="emp-name">${__("Daily Report Count")}</div></td>
                                <td data-field="daily_report">0</td>
                                <td><div class="emp-meta">${__("Total recorded logs for selected period.")}</div></td>
                            </tr>
                            <tr>
                                <td><div class="emp-name">${__("Appointments")}</div></td>
                                <td data-field="appointments">0</td>
                                <td><div class="emp-meta">${__("Scheduled sessions processed.")}</div></td>
                            </tr>
                            <tr>
                                <td><div class="emp-name">${__("Total Task")}</div></td>
                                <td data-field="total_task">0</td>
                                <td><div class="emp-meta">${__("Total tasks assigned in selected period.")}</div></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
		</div>
	`;

    $(html).appendTo($parent);
}

function get_dynamic_greeting() {
    let hour = new Date().getHours();
    if (hour < 12) return __('Good Morning');
    if (hour < 17) return __('Good Afternoon');
    return __('Good Evening');
}

// ---------------------------------------------------------------
// Default date helpers
// ---------------------------------------------------------------
function get_first_day_of_month() {
    let now = new Date();
    return frappe.datetime.obj_to_str(new Date(now.getFullYear(), now.getMonth(), 1));
}

function get_today() {
    return frappe.datetime.get_today();
}

// ---------------------------------------------------------------
// Dashboard initialisation
// ---------------------------------------------------------------
function init_dashboard(page) {
    // --- Employee selector (Frappe Link control) ---
    let selector = frappe.ui.form.make_control({
        parent: $('#employee-selector-container'),
        df: {
            label: '',
            fieldtype: 'Link',
            fieldname: 'employee',
            options: 'Employee',
            placeholder: __('Choose employee')
        },
        render_input: true
    });

    // --- Native date inputs (calendar picker, no free typing) ---
    let $from = $('#epd-from-date');
    let $to = $('#epd-to-date');
    $from.val(get_first_day_of_month());
    $to.val(get_today());

    // --- Apply button ---
    $('#epd-apply-btn').on('click', function () {
        let emp = selector.get_value();
        let from = $from.val();
        let to = $to.val();
        if (!emp) {
            frappe.msgprint(__('Please select an employee first.'));
            return;
        }
        if (from && to && from > to) {
            frappe.msgprint(__('From Date cannot be after To Date.'));
            return;
        }
        refresh_dashboard(emp, from, to);
    });

    // --- Auto-load current user's employee ---
    frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name').then(r => {
        if (r && r.message && r.message.name) {
            selector.set_value(r.message.name);
            refresh_dashboard(r.message.name, $from.val(), $to.val());
        }
    });

    page.employee_selector = selector;
}


// ---------------------------------------------------------------
// Clear all client-side caches for this dashboard
// ---------------------------------------------------------------
function clear_dashboard_cache() {
    // 1. Frappe model/doctype cache
    if (frappe.model && frappe.model.clear_cache) {
        frappe.model.clear_cache();
    }
    // 2. Frappe's internal request/response cache
    if (frappe.cache && frappe.cache.clear) {
        frappe.cache.clear();
    }
    // 3. Any localStorage keys we may have set
    try {
        Object.keys(localStorage).forEach(function (key) {
            if (key.startsWith('epd_') || key.includes('employee_performance')) {
                localStorage.removeItem(key);
            }
        });
    } catch (e) { /* ignore */ }

    console.log('EPD: Client cache cleared');
}

// ---------------------------------------------------------------
// Refresh dashboard
// ---------------------------------------------------------------
function refresh_dashboard(employee, from_date, to_date) {
    if (!employee) return;

    // Clear cache before every fetch so Apply always returns fresh data
    clear_dashboard_cache();

    // Show loading state on Apply button
    let $btn = $('#epd-apply-btn');
    $btn.prop('disabled', true).html(`<i class="fa fa-spinner fa-spin" style="margin-right:5px;"></i>${__('Loading...')}`);

    frappe.call({
        method: 'employee_performance.employee_performance.page.employee_performance.employee_performance.get_employee_dashboard',
        args: {
            employee: employee,
            from_date: from_date || get_first_day_of_month(),
            to_date: to_date || get_today(),
            _ts: Date.now()   // cache-buster: forces a fresh request each time
        },
        no_spinner: true,
        callback: function (r) {
            $btn.prop('disabled', false).html(`<i class="fa fa-check" style="margin-right:5px;"></i>${__('Apply')}`);
            if (r.message) {
                update_ui(r.message);
            }
        },
        error: function () {
            $btn.prop('disabled', false).html(`<i class="fa fa-check" style="margin-right:5px;"></i>${__('Apply')}`);
        }
    });
}

// ---------------------------------------------------------------
// Update UI with API response
// ---------------------------------------------------------------
function update_ui(data) {
    if (!data) {
        console.error("EPD: No data received in update_ui");
        return;
    }
    console.log("EPD: Update UI with data:", data);

    // Update date range label in header
    if (data.date_range) {
        let from_fmt = frappe.datetime.str_to_user(data.date_range.from_date);
        let to_fmt = frappe.datetime.str_to_user(data.date_range.to_date);
        $('#epd-date-range-label').text(`${__('Showing data from')} ${from_fmt} ${__('to')} ${to_fmt}`);
        $('#events-section-title').text(`${__('Activity Distribution')} (${from_fmt} – ${to_fmt})`);
    }

    // KPI cards
    $('[data-field="total_leads"]').text(data.crm.total_leads || 0);
    $('[data-field="total_opportunities"]').text(data.crm.total_opportunities || 0);
    $('[data-field="active_customers"]').text(data.crm.active_customers || 0);
    $('[data-field="conversion_rate"]').text((data.crm.conversion_rate || 0) + '%');

    // Table metrics
    $('[data-field="attendance_total"]').text(data.hr.present_days || 0);
    $('[data-field="daily_report"]').text(data.daily_report || 0);
    $('[data-field="appointments"]').text(data.appointments ? data.appointments.total || 0 : 0);
    $('[data-field="total_task"]').text(data.total_task || 0);

    // Charts — wait for frappe.Chart to be ready
    render_charts_when_ready(data);

    // Timeline — no frappe.Chart dependency
    try {
        render_activity_timeline(data.hr.recent_checkins);
    } catch (e) {
        console.error("EPD: Error in timeline", e);
    }
}

/**
 * Retry loop: retries every 300 ms up to maxRetries times.
 */
function render_charts_when_ready(data, retries) {
    if (retries === undefined) retries = 10;

    if (window.frappe && frappe.Chart) {
        console.log("EPD: frappe.Chart ready — rendering charts");
        try { render_main_dist(data.events_chart); } catch (e) { console.error("EPD: main distribution chart error", e); }
        try { render_leads_pulse(data.leads_pulse); } catch (e) { console.error("EPD: leads pulse chart error", e); }
        try { render_attendance_donut(data.attendance_chart); } catch (e) { console.error("EPD: attendance donut error", e); }
    } else if (retries > 0) {
        console.warn(`EPD: frappe.Chart not ready yet — retrying (${retries} left)`);
        setTimeout(() => render_charts_when_ready(data, retries - 1), 300);
    } else {
        console.error("EPD: frappe.Chart never became available after max retries");
    }
}

function render_main_dist(data) {
    let container_id = "main-distribution-chart";
    let $container = $("#" + container_id);
    if (!$container.length) return;

    let total = (data && data.values) ? data.values.reduce((a, b) => a + b, 0) : 0;

    let chart_data = {
        labels: total > 0 ? data.labels : [__("No Data")],
        datasets: [{ name: __("Activity"), values: total > 0 ? data.values : [0] }]
    };

    if (epd_charts.main_dist) {
        epd_charts.main_dist.update(chart_data);
    } else {
        epd_charts.main_dist = new frappe.Chart("#" + container_id, {
            data: chart_data,
            type: 'bar',
            height: 350,
            colors: ['#3b82f6'],
            barOptions: { spaceRatio: 0.2 },
            axisOptions: { xIsSeries: 1 }
        });
    }

    // Force whole numbers on the Y/X axis by hiding any labels with decimals
    setTimeout(() => {
        $("#" + container_id).find('.y-axis-text, .x-axis-text').each(function () {
            if ($(this).text().includes('.')) {
                $(this).html(''); // Clear the text
            }
        });
    }, 200);
}

function render_leads_pulse(data) {
    let container_id = "leads-pulse-chart";
    let $container = $("#" + container_id);
    if (!$container.length) return;

    let total = (data && data.values) ? data.values.reduce((a, b) => a + b, 0) : 0;

    let chart_data = {
        labels: total > 0 ? data.labels : [__("No Data")],
        datasets: [{ name: __("Leads"), values: total > 0 ? data.values : [0] }]
    };

    if (epd_charts.leads_pulse) {
        epd_charts.leads_pulse.update(chart_data);
    } else {
        epd_charts.leads_pulse = new frappe.Chart("#" + container_id, {
            data: chart_data,
            type: 'line',
            height: 200,
            colors: ['#a855f7'],
            lineOptions: { regionFill: 1, hideDots: 1 }
        });
    }

    // Force whole numbers
    setTimeout(() => {
        $("#" + container_id).find('.y-axis-text, .x-axis-text').each(function () {
            if ($(this).text().includes('.')) {
                $(this).html('');
            }
        });
    }, 200);
}

function render_attendance_donut(data) {
    let container_id = "attendance-donut-chart";
    let $container = $("#" + container_id);
    if (!$container.length) return;

    let total = (data && data.values) ? data.values.reduce((a, b) => a + b, 0) : 0;

    let chart_data = {
        labels: total > 0 ? data.labels : [__("No Data")],
        datasets: [{ values: total > 0 ? data.values : [1] }] // Donut chart needs at least 1 value to draw a circle
    };

    // For empty donut, make it grey
    let current_colors = total > 0 ? ['#22c55e', '#ef4444', '#f59e0b'] : ['#e2e8f0'];

    if (epd_charts.attendance_donut) {
        // Frappe chart doesn't gracefully update colors via update(), but the data will at least render.
        epd_charts.attendance_donut.update(chart_data);
    } else {
        epd_charts.attendance_donut = new frappe.Chart("#" + container_id, {
            data: chart_data,
            type: 'donut',
            height: 280,
            colors: current_colors,
            donutOptions: { strokeWidth: 40 }
        });
    }
}

function render_activity_timeline(reports) {
    let $container = $('#checkin-timeline');
    if (!$container.length) return;
    $container.empty();

    if (!reports || reports.length === 0) {
        $container.append(`<div class="text-muted text-center" style="padding: 20px;">${__('No recent check-ins found')}</div>`);
        return;
    }

    reports.slice(0, 10).forEach(log => {
        // Show Date + Time for checkins
        let datetime = frappe.datetime.str_to_user(log.time);

        // Determine color class based on OUT/IN
        let badgeClass = (log.log_type === 'OUT') ? 'log-out' : 'log-in';
        let typeLabel = (log.log_type === 'OUT') ? __('Check OUT') : __('Check IN');

        $container.append(`
			<div class="timeline-row">
				<div class="emp-name" style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${datetime}
                </div>
				<div class="timeline-log-type ${badgeClass}">${typeLabel}</div>
			</div>
		`);
    });
}